using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class BroadcastMessage
    {
        public static string API_KEY = "<your-api-key>";
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Api-Key {API_KEY}");

            // ===== 模式 1：指定聯絡人 ID 群發 =====
            var payload = new
            {
                message = "您好，這是一則群發訊息！",
                contact_ids = new[]
                {
                    "<contact-id-1>",
                    "<contact-id-2>",
                    "<contact-id-3>",
                },
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json");

            var response = await httpClient.PostAsync($"{BASE_URL}contacts/broadcast-message", content);
            response.EnsureSuccessStatusCode();

            var responseString = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<JsonElement>(responseString);

            Console.WriteLine("群發結果：");
            Console.WriteLine($"  總共: {result.GetProperty("total_contacts")} 人");
            Console.WriteLine($"  成功: {result.GetProperty("success_count")} 人");
            Console.WriteLine($"  失敗: {result.GetProperty("error_count")} 人");

            foreach (var item in result.GetProperty("results").EnumerateArray())
            {
                Console.WriteLine($"  ✓ contact: {item.GetProperty("contact_id")}, message: {item.GetProperty("message_id")}");
            }

            foreach (var error in result.GetProperty("errors").EnumerateArray())
            {
                Console.WriteLine($"  ✗ contact: {error.GetProperty("contact_id")}, error: {error.GetProperty("error")}");
            }

            // ===== 模式 2：指定 inbox，排除特定聯絡人 =====
            // var payload2 = new
            // {
            //     message = "您好，這是一則群發訊息！",
            //     inbox_id = "<inbox-id>",
            //     exclude_contact_ids = new[] { "<contact-id-to-exclude>" },
            // };

            // ===== 模式 3：對整個 inbox 所有聯絡人群發 =====
            // var payload3 = new
            // {
            //     message = "您好，這是一則群發訊息！",
            //     inbox_id = "<inbox-id>",
            // };

            /*
            回應格式：
            {
                "results": [
                    {
                        "contact_id": "uuid",
                        "conversation_id": "uuid",
                        "message_id": "uuid",
                        "status": "success"
                    }
                ],
                "errors": [
                    {
                        "contact_id": "uuid",
                        "error": "No conversation found for this contact."
                    }
                ],
                "total_contacts": 3,
                "success_count": 2,
                "error_count": 1
            }
            */
        }
    }
}
