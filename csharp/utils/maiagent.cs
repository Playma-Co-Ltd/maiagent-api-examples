using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

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
}
