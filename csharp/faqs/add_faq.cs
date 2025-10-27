
using requests;

using System.Diagnostics;

using System.Collections.Generic;

public static class add_faq {
    
    public static string BASE_URL = "https://api.maiagent.ai/api/v1/";
    
    public static string API_KEY = "<your-api-key>";
    
    public static string CHATBOT_ID = "<your-chatbot-id>";
    
    public static string QUESTION = "<your-question>";
    
    public static string ANSWER = "<your-answer>";
    
    public static int add_faq(string chatbot_id, string question, string answer) {
        var url = $"{BASE_URL}faqs/";
        try {
            var response = requests.post(url, headers: new Dictionary<object, object> {
                {
                    "Authorization",
                    $"Api-Key {API_KEY}"}}, json: new Dictionary<object, object> {
                {
                    "chatbot",
                    chatbot_id},
                {
                    "question",
                    question},
                {
                    "answer",
                    answer}});
        } catch {
            Console.WriteLine(response.text);
            Console.WriteLine(e);
            exit(1);
        } catch (Exception) {
            Console.WriteLine(e);
            exit(1);
        }
        return response.status_code;
    }
    
    public static int result = add_faq(chatbot_id: CHATBOT_ID, question: QUESTION, answer: ANSWER);
    
    static add_faq() {
        Debug.Assert(API_KEY != "<your-api-key>");
        Debug.Assert("Please set your API key");
        Debug.Assert(CHATBOT_ID != "<your-chatbot-id>");
        Debug.Assert("Please set your chatbot id");
        Debug.Assert(QUESTION != "<your-question>");
        Debug.Assert("Please set your question");
        Debug.Assert(ANSWER != "<your-answer>");
        Debug.Assert("Please set your answer");
        if (@__name__ == "__main__") {
            Console.WriteLine(result);
        }
    }
}
