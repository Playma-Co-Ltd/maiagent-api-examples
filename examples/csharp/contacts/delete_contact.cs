using System;
using System.Diagnostics;
using System.Net.Http;
using System.Threading.Tasks;

namespace MaiAgentExamples.Contacts
{
    public static class DeleteContact
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

            // 刪除聯絡人（軟刪除）
            var response = await httpClient.DeleteAsync($"{BASE_URL}contacts/{CONTACT_ID}/");
            response.EnsureSuccessStatusCode();

            Console.WriteLine($"聯絡人 {CONTACT_ID} 已刪除");
        }
    }
}
