using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace Utils
{
    public class MaiAgentHelper
    {
    private readonly string _apiKey;
    private readonly string _baseUrl;
    private readonly string _storageUrl;
    private readonly HttpClient _httpClient;

    public MaiAgentHelper(
        string apiKey,
        string baseUrl = "https://api.maiagent.ai/api/v1/",
        string storageUrl = "https://s3.ap-northeast-1.amazonaws.com/whizchat-media-prod-django.playma.app")
    {
        _apiKey = apiKey;
        _baseUrl = baseUrl;
        _storageUrl = storageUrl;
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {_apiKey}");
    }

    public async Task<JsonElement> CreateConversationAsync(string webChatId)
    {
        try
        {
            var payload = new { webChat = webChatId };
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}conversations/", content);
            response.EnsureSuccessStatusCode();
            
            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<JsonElement> SendMessageAsync(string conversationId, string content, List<string> attachments = null)
    {
        try
        {
            var payload = new
            {
                conversation = conversationId,
                content = content,
                attachments = attachments ?? new List<string>()
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync($"{_baseUrl}messages/", jsonContent);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<JsonElement?> GetUploadUrlAsync(string filePath, string modelName, string fieldName = "file")
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException("File does not exist", filePath);

        var fileInfo = new FileInfo(filePath);
        var payload = new
        {
            filename = fileInfo.Name,
            modelName = modelName,
            fieldName = fieldName,
            fileSize = fileInfo.Length
        };

        var content = new StringContent(
            JsonSerializer.Serialize(payload),
            Encoding.UTF8,
            "application/json");

        var response = await _httpClient.PostAsync($"{_baseUrl}upload-presigned-url/", content);
        
        if (response.IsSuccessStatusCode)
        {
            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        
        Console.WriteLine($"Error: {response.StatusCode}");
        return null;
    }

    public async Task<JsonElement> UpdateAttachmentAsync(string conversationId, string fileId, string originalFilename)
    {
        var url = $"{_baseUrl}conversations/{conversationId}/attachments/";

        var payload = new
        {
            file = fileId,
            filename = originalFilename,
            type = "image"
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<JsonElement> UpdateChatbotFilesAsync(string chatbotId, string fileKey, string originalFilename)
    {
        var url = $"{_baseUrl}chatbots/{chatbotId}/files/";

        var payload = new
        {
            files = new[]
            {
                new { file = fileKey, filename = originalFilename }
            }
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<JsonElement> UploadAttachmentAsync(string conversationId, string filePath)
    {
        var uploadUrl = await GetUploadUrlAsync(filePath, "attachment");
        var fileKey = await UploadFileToS3Async(filePath, uploadUrl.Value);

        return await UpdateAttachmentAsync(conversationId, fileKey, Path.GetFileName(filePath));
    }

    public async Task<JsonElement> UploadKnowledgeFileAsync(string chatbotId, string filePath)
    {
        var uploadUrl = await GetUploadUrlAsync(filePath, "chatbot-file");
        var fileKey = await UploadFileToS3Async(filePath, uploadUrl.Value);

        return await UpdateChatbotFilesAsync(chatbotId, fileKey, Path.GetFileName(filePath));
    }

    public async Task DeleteKnowledgeFileAsync(string chatbotId, string fileId)
    {
        var url = $"{_baseUrl}chatbots/{chatbotId}/files/{fileId}/";

        var response = await _httpClient.DeleteAsync(url);

        if (response.StatusCode == System.Net.HttpStatusCode.NoContent)
        {
            Console.WriteLine($"Successfully deleted knowledge with ID: {fileId}");
        }
        else
        {
            Console.WriteLine($"Error: {response.StatusCode}");
            var responseString = await response.Content.ReadAsStringAsync();
            Console.WriteLine(responseString);
        }
    }

    public async Task<string> UploadFileToS3Async(string filePath, JsonElement uploadData)
    {
        using var form = new MultipartFormDataContent();
        using var fileStream = File.OpenRead(filePath);
        using var fileContent = new StreamContent(fileStream);
        
        var fileName = Path.GetFileName(filePath);
        form.Add(fileContent, "file", fileName);

        var fields = uploadData.GetProperty("fields");
        form.Add(new StringContent(fields.GetProperty("key").GetString()), "key");
        form.Add(new StringContent(fields.GetProperty("x-amz-algorithm").GetString()), "x-amz-algorithm");
        form.Add(new StringContent(fields.GetProperty("x-amz-credential").GetString()), "x-amz-credential");
        form.Add(new StringContent(fields.GetProperty("x-amz-date").GetString()), "x-amz-date");
        form.Add(new StringContent(fields.GetProperty("policy").GetString()), "policy");
        form.Add(new StringContent(fields.GetProperty("x-amz-signature").GetString()), "x-amz-signature");

        var response = await _httpClient.PostAsync(_storageUrl, form);

        if (response.StatusCode == System.Net.HttpStatusCode.NoContent)
        {
            Console.WriteLine("File uploaded successfully");
            return fields.GetProperty("key").GetString();
        }

        Console.WriteLine($"Error uploading file: {response.StatusCode}");
        return null;
    }

    public async Task<JsonElement[]> GetInboxItemsAsync()
    {
        var inboxItems = new List<JsonElement>();
        var url = $"{_baseUrl}inboxes/";

        while (!string.IsNullOrEmpty(url))
        {
            try
            {
                var response = await _httpClient.GetAsync(url);
                response.EnsureSuccessStatusCode();

                var jsonResponse = await response.Content.ReadAsStringAsync();
                var result = JsonSerializer.Deserialize<JsonElement>(jsonResponse);
                
                inboxItems.AddRange(result.GetProperty("results").EnumerateArray());
                
                url = result.GetProperty("next").GetString();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                throw;
            }
        }

        return inboxItems.ToArray();
    }

    public void DisplayInboxItems(JsonElement[] inboxItems)
    {
        foreach (var item in inboxItems)
        {
            var inboxId = item.GetProperty("id").GetString();
            var webchatId = item.GetProperty("channel").GetProperty("id").GetString();
            var webchatName = item.GetProperty("channel").GetProperty("name").GetString();

            Console.WriteLine($"Inbox ID: {inboxId}, Webchat ID: {webchatId}, Webchat Name: {webchatName}");
        }
    }

    // Batch QA methods
    public async Task<JsonElement> UploadBatchQAFileAsync(string webChatId, string fileKey, string originalFilename)
    {
        var url = $"{_baseUrl}web-chats/{webChatId}/batch-qa-files/";

        var payload = new
        {
            file = fileKey,
            filename = originalFilename
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<string> DownloadBatchQAExcelAsync(string webChatId, string batchQaFileId)
    {
        var url = $"{_baseUrl}web-chats/{webChatId}/batch-qa-files/{batchQaFileId}/download/";

        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var fileName = $"batch_qa_{batchQaFileId}.xlsx";
            using var fileStream = File.Create(fileName);
            await response.Content.CopyToAsync(fileStream);

            Console.WriteLine($"File downloaded: {fileName}");
            return fileName;
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    // Attachment methods
    public async Task<JsonElement> UploadAttachmentWithoutConversationAsync(string filePath, string type = "image")
    {
        var uploadUrl = await GetUploadUrlAsync(filePath, "attachment");
        var fileKey = await UploadFileToS3Async(filePath, uploadUrl.Value);

        var url = $"{_baseUrl}attachments/";
        var payload = new
        {
            file = fileKey,
            filename = Path.GetFileName(filePath),
            type = type
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    // Chatbot Completion methods
    public async Task<JsonElement> CreateChatbotCompletionAsync(
        string chatbotId,
        string message,
        string? conversationId = null,
        List<Dictionary<string, string>>? attachments = null)
    {
        var url = $"{_baseUrl}chatbots/{chatbotId}/completions/";

        var payload = new
        {
            conversation = conversationId,
            message = new
            {
                content = message,
                attachments = attachments ?? new List<Dictionary<string, string>>()
            },
            isStreaming = false
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async IAsyncEnumerable<JsonElement> CreateChatbotCompletionStreamAsync(
        string chatbotId,
        string message,
        string? conversationId = null,
        List<Dictionary<string, string>>? attachments = null)
    {
        var url = $"{_baseUrl}chatbots/{chatbotId}/completions/";

        var payload = new
        {
            conversation = conversationId,
            message = new
            {
                content = message,
                attachments = attachments ?? new List<Dictionary<string, string>>()
            },
            isStreaming = true
        };

        var content = new StringContent(
            JsonSerializer.Serialize(payload),
            Encoding.UTF8,
            "application/json");

        var request = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = content
        };

        using var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead);
        response.EnsureSuccessStatusCode();

        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);

        while (!reader.EndOfStream)
        {
            var line = await reader.ReadLineAsync();
            if (string.IsNullOrWhiteSpace(line) || !line.StartsWith("data: "))
                continue;

            var jsonData = line.Substring(6);
            if (jsonData == "[DONE]")
                break;

            JsonElement element;
            if (JsonSerializer.Deserialize<JsonElement>(jsonData).ValueKind != JsonValueKind.Undefined)
            {
                element = JsonSerializer.Deserialize<JsonElement>(jsonData);
                yield return element;
            }
        }
    }

    // Knowledge Base methods
    public async Task<object> create_knowledge_base(string name, string description = "", string language = "")
    {
        var url = $"{_baseUrl}knowledge-bases/";
        var payload = new
        {
            name = name,
            description = description,
            language = language
        };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> list_knowledge_bases()
    {
        var url = $"{_baseUrl}knowledge-bases/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> get_knowledge_base(string knowledgeBaseId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task delete_knowledge_file(string chatbotId, string fileId)
    {
        await DeleteKnowledgeFileAsync(chatbotId, fileId);
    }

    public async Task<object> create_knowledge_base_label(string knowledgeBaseId, string name, string color)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/labels/";
        var payload = new { name = name, color = color };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> list_knowledge_base_labels(string knowledgeBaseId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/labels/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> get_knowledge_base_label(string knowledgeBaseId, string labelId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/labels/{labelId}/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> update_knowledge_base_label(string knowledgeBaseId, string labelId, string name, string color)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/labels/{labelId}/";
        var payload = new { name = name, color = color };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PutAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> create_knowledge_base_faq(string knowledgeBaseId, string question, string answer)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/faqs/";
        var payload = new { question = question, answer = answer };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> list_knowledge_base_faqs(string knowledgeBaseId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/faqs/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> get_knowledge_base_faq(string knowledgeBaseId, string faqId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/faqs/{faqId}/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> update_knowledge_base_faq(string knowledgeBaseId, string faqId, string question, string answer)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/faqs/{faqId}/";
        var payload = new { question = question, answer = answer };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PutAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> list_knowledge_base_files(string knowledgeBaseId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/files/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> get_knowledge_base_file(string knowledgeBaseId, string fileId)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/files/{fileId}/";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> update_knowledge_base_file_metadata(string knowledgeBaseId, string fileId, List<string> labels)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/files/{fileId}/";
        var payload = new { labels = labels };

        try
        {
            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await _httpClient.PatchAsync(url, content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> search_knowledge_base(string knowledgeBaseId, string query)
    {
        var url = $"{_baseUrl}knowledge-bases/{knowledgeBaseId}/search/?query={Uri.EscapeDataString(query)}";
        try
        {
            var response = await _httpClient.GetAsync(url);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(responseString);
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.Message);
            throw;
        }
    }

    public async Task<object> upload_knowledge_file(string chatbotId, string filePath)
    {
        return await UploadKnowledgeFileAsync(chatbotId, filePath);
    }
    }
}
