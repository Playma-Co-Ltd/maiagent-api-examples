using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class ListContacts
    {
        public static string API_KEY = "<your-api-key>";
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {API_KEY}");

            // 列出所有聯絡人
            var response = await httpClient.GetAsync($"{BASE_URL}contacts/");
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(responseString);

            Console.WriteLine($"共 {data.GetProperty("count")} 筆聯絡人");
            foreach (var contact in data.GetProperty("results").EnumerateArray())
            {
                Console.WriteLine($"  - {contact.GetProperty("name")} (ID: {contact.GetProperty("id")})");
            }

            // 使用篩選參數查詢
            // query: 依名稱、ID 或 source_id 搜尋（模糊比對）
            // inboxes: 依 inbox ID 篩選
            var searchResponse = await httpClient.GetAsync($"{BASE_URL}contacts/?query=John&limit=10&offset=0");
            searchResponse.EnsureSuccessStatusCode();

            var searchString = await searchResponse.Content.ReadAsStringAsync();
            var searchData = JsonSerializer.Deserialize<JsonElement>(searchString);

            Console.WriteLine($"\n搜尋結果：共 {searchData.GetProperty("count")} 筆");
            foreach (var contact in searchData.GetProperty("results").EnumerateArray())
            {
                var email = contact.TryGetProperty("email", out var emailProp) && emailProp.ValueKind != JsonValueKind.Null
                    ? emailProp.GetString() : "N/A";
                Console.WriteLine($"  - {contact.GetProperty("name")} (email: {email})");
            }

            /*
            回應格式：
            {
                "count": 100,
                "next": "https://api.maiagent.ai/api/v1/contacts/?limit=20&offset=20",
                "previous": null,
                "results": [
                    {
                        "id": "contact-uuid",
                        "name": "John Doe",
                        "email": "john@example.com",
                        "phone_number": "+886912345678",
                        "avatar": "https://example.com/avatar.jpg",
                        "source_id": "external_id_123",
                        "inboxes": [
                            {"id": "inbox-uuid", "name": "My Inbox"}
                        ],
                        "query_metadata": {"source": "web"},
                        "mcp_credentials": [],
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ]
            }
            */
        }
    }
}
