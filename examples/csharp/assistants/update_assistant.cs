using System;
using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace MaiAgentExamples.Assistants
{
    public static class UpdateAssistant
    {
        public static string BASE_URL = "https://api.maiagent.ai/api/v1/";
        public static string API_KEY = "<your-api-key>";
        public static string CHATBOT_ID = "<your-chatbot-id>";
        public static string NAME = "<your-assistant-name>";
        public static string MODEL_ID = "ba7da66a-6f30-414d-98f8-7d681a92d47a";
        public static string RAG_ID = "66261b7a-bd3f-4214-9c48-364c2e122b0f";
        public static string INSTRUCTIONS = "<your-instructions>";

        public static async Task<JsonElement?> UpdateAssistantAsync(
            string chatbotId,
            string name,
            string modelId,
            string ragId,
            string instructions)
        {
            var url = $"{BASE_URL}chatbots/{chatbotId}/";

            try
            {
                using var httpClient = new HttpClient();
                httpClient.DefaultRequestHeaders.Accept.Add(
                    new MediaTypeWithQualityHeaderValue("application/json"));
                httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Api-Key", API_KEY);

                var payload = new
                {
                    name = name,
                    model = modelId,
                    rag = ragId,
                    instructions = instructions
                };

                var jsonContent = JsonSerializer.Serialize(payload);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                var response = await httpClient.PutAsync(url, content);
                response.EnsureSuccessStatusCode();

                var responseContent = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<JsonElement>(responseContent);
            }
            catch (HttpRequestException e)
            {
                Console.WriteLine($"Error updating assistant: {e.Message}");
                return null;
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error: {e.Message}");
                return null;
            }
        }

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
            Debug.Assert(CHATBOT_ID != "<your-chatbot-id>", "Please set your chatbot id");
            Debug.Assert(NAME != "<your-assistant-name>", "Please set your assistant name");
            Debug.Assert(INSTRUCTIONS != "<your-instructions>", "Please set your instructions");

            var result = await UpdateAssistantAsync(CHATBOT_ID, NAME, MODEL_ID, RAG_ID, INSTRUCTIONS);

            if (result.HasValue)
            {
                Console.WriteLine("Assistant updated successfully:");
                Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                }));
            }
            else
            {
                Console.WriteLine("Failed to update assistant");
            }
        }
    }
}
