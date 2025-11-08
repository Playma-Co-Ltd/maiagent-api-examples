
using json;

using logging;

using subprocess;

using Flask = flask.Flask;

using jsonify = flask.jsonify;

using request = flask.request;

using System.Collections.Generic;

public static class webhook_server {
    
    public static object app = Flask(@__name__);
    
    static webhook_server() {
        logging.basicConfig(level: logging.INFO);
        app.run(host: "0.0.0.0", port: port, debug: true);
    }
    
    [app.route("/webhook",methods=new List<object> {
        "POST"
    })]
    public static Tuple<object, int> webhook() {
        if (request.method == "POST") {
            var data = request.json;
            logging.info($"收到 webhook 請求: {data}");
            // 處理 Webhook Request
            Console.WriteLine("=" * 100);
            Console.WriteLine("Request:");
            Console.WriteLine("=" * 100);
            Console.WriteLine(json.dumps(data, indent: 4, ensure_ascii: false));
            // 範例：
            @"
        {
            ""id"": ""<id>"",
            ""conversation"": ""<conversation>"",
            ""sender"": {
                ""id"": <sender_id>,
                ""name"": ""<sender_name>"",
                ""avatar"": ""<sender_avatar>""
            },
            ""type"": ""outgoing"",
            ""content"": ""這是 webhook 測試訊息"",
            ""feedback"": null,
            ""created_at"": ""1728219442000"",
            ""attachments"": [],
            ""citations"": []
        }
        ";
            Console.WriteLine("=" * 100);
            // 取出 message 的內容
            var content = data["content"];
            Console.WriteLine("Message:");
            Console.WriteLine("=" * 100);
            Console.WriteLine(content);
            // 範例：
            @"
        這是 webhook 測試訊息
        ";
            Console.WriteLine("=" * 100);
            return (jsonify(new Dictionary<object, object> {
                {
                    "message",
                    "Webhook 接收成功"}}), 200);
        } else {
            return (jsonify(new Dictionary<object, object> {
                {
                    "error",
                    "僅支持 POST 請求"}}), 405);
        }
    }
    
    public static int port = 6666;
    
    public static object process = subprocess.Popen(new List<string> {
        "lt",
        "--port",
        port.ToString()
    }, stdout: subprocess.PIPE);
    
    public static object public_url = process.stdout.readline().decode().strip();
    
    static webhook_server() {
        if (@__name__ == "__main__") {
            Console.WriteLine("=" * 100);
            Console.WriteLine("Webhook Server 正在運行。");
            Console.WriteLine($"Public URL: {public_url}");
            Console.WriteLine($"Webhook endpoint: {public_url}/webhook");
            Console.WriteLine("=" * 100);
        }
    }
}
