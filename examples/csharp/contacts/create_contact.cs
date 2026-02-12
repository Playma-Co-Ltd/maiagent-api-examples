using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class CreateContact
    {
        public static string API_KEY = "<your-api-key>";
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";

        // 聯絡人所屬的 inbox ID（必填）
        public static string INBOX_ID = "<your-inbox-id>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(INBOX_ID != "<your-inbox-id>", "Please set your inbox id");

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {API_KEY}");

            // 建立聯絡人
            var payload = new
            {
                name = "John Doe",
                email = "john@example.com",
                phone_number = "+886912345678",
                inboxes = new[] { new { id = INBOX_ID } },
                // 選填欄位
                // avatar = "https://example.com/avatar.jpg",
                // source_id = "external_id_123",
                // query_metadata = new { source = "web", campaign = "spring_2024" },
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await httpClient.PostAsync($"{BASE_URL}contacts/", content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            var contact = JsonSerializer.Deserialize<JsonElement>(responseString);

            Console.WriteLine("聯絡人建立成功！");
            Console.WriteLine($"  ID: {contact.GetProperty("id")}");
            Console.WriteLine($"  名稱: {contact.GetProperty("name")}");

            var email = contact.TryGetProperty("email", out var emailProp) && emailProp.ValueKind != JsonValueKind.Null
                ? emailProp.GetString() : "N/A";
            Console.WriteLine($"  Email: {email}");

            /*
            回應格式：
            {
                "id": "contact-uuid",
                "name": "John Doe",
                "email": "john@example.com",
                "phone_number": "+886912345678",
                "avatar": null,
                "source_id": null,
                "inboxes": [
                    {"id": "inbox-uuid", "name": "My Inbox"}
                ],
                "query_metadata": null,
                "mcp_credentials": [],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            */
        }
    }
}
