
using json;

using requests;

using System.Diagnostics;

using System.Collections.Generic;

public static class update_assistant {
    
    public static string BASE_URL = "https://api.maiagent.ai/api/v1/";
    
    public static string API_KEY = "<your-api-key>";
    
    public static string CHATBOT_ID = "<your-chatbot-id>";
    
    public static string NAME = "<your-assistant-name>";
    
    public static string MODEL_ID = "ba7da66a-6f30-414d-98f8-7d681a92d47a";
    
    public static string RAG_ID = "66261b7a-bd3f-4214-9c48-364c2e122b0f";
    
    public static string INSTRUCTIONS = "<your-instructions>";
    
    public static object update_assistant(
        string chatbot_id,
        string name,
        string model_id,
        string rag_id,
        string instructions) {
        var url = $"{BASE_URL}chatbots/{chatbot_id}/";
        try {
            var response = requests.put(url, headers: new Dictionary<object, object> {
                {
                    "Content-Type",
                    "application/json"},
                {
                    "Accept",
                    "application/json, text/plain, */*"},
                {
                    "Authorization",
                    $"Api-Key {API_KEY}"}}, data: json.dumps(new Dictionary<object, object> {
                {
                    "name",
                    name},
                {
                    "model",
                    model_id},
                {
                    "rag",
                    rag_id},
                {
                    "instructions",
                    instructions}}));
            response.raise_for_status();
            return response.json();
        } catch {
            Console.WriteLine($"Error updating assistant: {e}");
            Console.WriteLine(response ? response.text : "No response");
            return null;
        }
    }
    
    public static object result = update_assistant(chatbot_id: CHATBOT_ID, name: NAME, model_id: MODEL_ID, rag_id: RAG_ID, instructions: INSTRUCTIONS);
    
    static update_assistant() {
        Debug.Assert(API_KEY != "<your-api-key>");
        Debug.Assert("Please set your API key");
        Debug.Assert(CHATBOT_ID != "<your-chatbot-id>");
        Debug.Assert("Please set your chatbot id");
        Debug.Assert(NAME != "<your-assistant-name>");
        Debug.Assert("Please set your assistant name");
        Debug.Assert(INSTRUCTIONS != "<your-instructions>");
        Debug.Assert("Please set your instructions");
        if (@__name__ == "__main__") {
            if (result) {
                Console.WriteLine("Assistant updated successfully:");
                Console.WriteLine(json.dumps(result, ensure_ascii: true, indent: 4));
            } else {
                Console.WriteLine("Failed to update assistant");
            }
        }
    }
}
