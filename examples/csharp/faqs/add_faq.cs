using System;
using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.FAQs
{
    public static class AddFAQ
    {
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";
        public static string API_KEY = "<your-api-key>";
        public static string CHATBOT_ID = "<your-chatbot-id>";
        public static string QUESTION = "<your-question>";
        public static string ANSWER = "<your-answer>";

        public static async Task<int> AddFaqAsync(string chatbotId, string question, string answer)
        {
            var url = $"{BASE_URL}faqs/";

            try
            {
                using var httpClient = new HttpClient();
                httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Api-Key", API_KEY);

                var payload = new
                {
                    chatbot = chatbotId,
                    question = question,
                    answer = answer
                };

                var jsonContent = JsonSerializer.Serialize(payload);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);
                response.EnsureSuccessStatusCode();

                var responseContent = await response.Content.ReadAsStringAsync();
                Console.WriteLine(responseContent);

                return (int)response.StatusCode;
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine($"HTTP 錯誤: {e.Message}");
                Environment.Exit(1);
                return 0;
            }
            catch (Exception e)
            {
                Console.WriteLine($"錯誤: {e.Message}");
                Environment.Exit(1);
                return 0;
            }
        }

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(CHATBOT_ID != "<your-chatbot-id>", "Please set your chatbot id");
            Debug.Assert(QUESTION != "<your-question>", "Please set your question");
            Debug.Assert(ANSWER != "<your-answer>", "Please set your answer");

            var result = await AddFaqAsync(CHATBOT_ID, QUESTION, ANSWER);
            Console.WriteLine($"Status Code: {result}");
        }
    }
}
