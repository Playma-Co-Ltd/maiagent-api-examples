using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Messages
{
    public static class UploadAttachment
    {
        public static string TEST_IMAGE_PATH = Path.Combine(
            Directory.GetParent(Directory.GetCurrentDirectory())?.Parent?.Parent?.FullName ?? "",
            "inputs",
            "cat.jpg"
        );

        public static async Task Main(string[] args)
        {
            var filePath = args.Length > 0 ? args[0] : TEST_IMAGE_PATH;
            await UploadFile(filePath);
        }

        private static async Task UploadFile(string filePath)
        {
            if (!File.Exists(filePath))
            {
                Console.WriteLine($"File not found: {filePath}");
                return;
            }

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Api-Key", Config.API_KEY);

            using var form = new MultipartFormDataContent();
            var fileStream = File.OpenRead(filePath);
            var fileContent = new StreamContent(fileStream);

            // Set content type based on file extension
            var extension = Path.GetExtension(filePath).ToLower();
            fileContent.Headers.ContentType = extension switch
            {
                ".jpg" or ".jpeg" => new MediaTypeHeaderValue("image/jpeg"),
                ".png" => new MediaTypeHeaderValue("image/png"),
                ".gif" => new MediaTypeHeaderValue("image/gif"),
                ".pdf" => new MediaTypeHeaderValue("application/pdf"),
                _ => new MediaTypeHeaderValue("application/octet-stream")
            };

            form.Add(fileContent, "file", Path.GetFileName(filePath));

            var response = await httpClient.PostAsync($"{Config.BASE_URL}attachments/", form);
            response.EnsureSuccessStatusCode();

            var responseContent = await response.Content.ReadAsStringAsync();
            var jsonResponse = JsonSerializer.Deserialize<JsonElement>(responseContent);

            Console.WriteLine(JsonSerializer.Serialize(jsonResponse, new JsonSerializerOptions { WriteIndented = true }));
        }
    }
}
