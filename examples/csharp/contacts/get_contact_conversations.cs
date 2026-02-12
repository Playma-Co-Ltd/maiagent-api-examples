using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class GetContactConversations
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

            // 取得聯絡人的所有對話
            var response = await httpClient.GetAsync($"{BASE_URL}contacts/{CONTACT_ID}/conversations");
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            var data = JsonSerializer.Deserialize<JsonElement>(responseString);

            Console.WriteLine($"共 {data.GetProperty("count")} 筆對話");
            foreach (var conversation in data.GetProperty("results").EnumerateArray())
            {
                Console.WriteLine($"  - 對話 ID: {conversation.GetProperty("id")}");
            }

            // 也可以用關鍵字搜尋對話中的訊息
            var searchResponse = await httpClient.GetAsync(
                $"{BASE_URL}contacts/{CONTACT_ID}/conversations?keyword=你好");
            searchResponse.EnsureSuccessStatusCode();

            var searchString = await searchResponse.Content.ReadAsStringAsync();
            var searchData = JsonSerializer.Deserialize<JsonElement>(searchString);

            Console.WriteLine($"\n搜尋結果：共 {searchData.GetProperty("count")} 筆對話");

            // 取得最新的一筆對話
            var latestResponse = await httpClient.GetAsync(
                $"{BASE_URL}contacts/{CONTACT_ID}/conversations/latest");

            if (latestResponse.IsSuccessStatusCode)
            {
                var latestString = await latestResponse.Content.ReadAsStringAsync();
                var latest = JsonSerializer.Deserialize<JsonElement>(latestString);
                Console.WriteLine($"\n最新對話 ID: {latest.GetProperty("id")}");
            }
            else if ((int)latestResponse.StatusCode == 404)
            {
                Console.WriteLine("\n該聯絡人尚無對話紀錄");
            }
        }
    }
}
