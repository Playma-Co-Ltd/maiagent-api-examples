using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class UpdateContact
    {
        public static string API_KEY = "<your-api-key>";
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";

        public static string CONTACT_ID = "<your-contact-id>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(CONTACT_ID != "<your-contact-id>", "Please set your contact id");

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {API_KEY}");

            // 使用 PATCH 更新部分欄位
            var payload = new
            {
                name = "John Doe (Updated)",
                email = "john.updated@example.com",
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var request = new HttpRequestMessage(HttpMethod.Patch, $"{BASE_URL}contacts/{CONTACT_ID}/")
            {
                Content = content
            };

            var response = await httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            var contact = JsonSerializer.Deserialize<JsonElement>(responseString);

            Console.WriteLine("聯絡人更新成功！");
            Console.WriteLine($"  ID: {contact.GetProperty("id")}");
            Console.WriteLine($"  名稱: {contact.GetProperty("name")}");

            var email = contact.TryGetProperty("email", out var emailProp) && emailProp.ValueKind != JsonValueKind.Null
                ? emailProp.GetString() : "N/A";
            Console.WriteLine($"  Email: {email}");
        }
    }
}
