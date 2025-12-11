using System;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace MaiAgentExamples.Messages
{
    /// <summary>
    /// Webhook Server 範例
    ///
    /// 注意：這是一個使用 ASP.NET Core 的 webhook 服務器範例
    ///
    /// 使用方式：
    /// 1. 確保您的專案檔案 (.csproj) 使用 Microsoft.NET.Sdk.Web
    /// 2. 運行此應用程式：dotnet run
    /// 3. 使用 ngrok 或 localtunnel 將本地端口暴露到公網
    ///    例如：lt --port 6666
    /// 4. 在 MaiAgent 後台設定 webhook URL
    /// </summary>
    public class WebhookServer
    {
        private const int Port = 6666;
        private const string SeparatorLine = "====================================================================================================";

        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // 配置日誌
            builder.Logging.ClearProviders();
            builder.Logging.AddConsole();

            // 配置監聽地址
            builder.WebHost.UseUrls($"http://0.0.0.0:{Port}");

            var app = builder.Build();

            // 配置 webhook 端點
            app.MapPost("/webhook", HandleWebhook);

            // 顯示啟動信息
            Console.WriteLine(SeparatorLine);
            Console.WriteLine("Webhook Server 正在運行。");
            Console.WriteLine($"Local URL: http://localhost:{Port}");
            Console.WriteLine($"Webhook endpoint: http://localhost:{Port}/webhook");
            Console.WriteLine();
            Console.WriteLine("使用 localtunnel 或 ngrok 將端口暴露到公網:");
            Console.WriteLine($"  lt --port {Port}");
            Console.WriteLine($"  或");
            Console.WriteLine($"  ngrok http {Port}");
            Console.WriteLine(SeparatorLine);

            await app.RunAsync();
        }

        private static async Task<IResult> HandleWebhook(HttpContext context)
        {
            var logger = context.RequestServices.GetService(typeof(ILogger<WebhookServer>)) as ILogger<WebhookServer>;

            try
            {
                // 讀取請求 Body
                var data = await JsonSerializer.DeserializeAsync<JsonElement>(context.Request.Body);

                logger?.LogInformation("收到 webhook 請求");

                // 處理 Webhook Request
                Console.WriteLine(SeparatorLine);
                Console.WriteLine("Request:");
                Console.WriteLine(SeparatorLine);
                Console.WriteLine(JsonSerializer.Serialize(data, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
                }));

                /* 範例格式：
                {
                    "id": "<id>",
                    "conversation": "<conversation>",
                    "sender": {
                        "id": <sender_id>,
                        "name": "<sender_name>",
                        "avatar": "<sender_avatar>"
                    },
                    "type": "outgoing",
                    "content": "這是 webhook 測試訊息",
                    "feedback": null,
                    "created_at": "1728219442000",
                    "attachments": [],
                    "citations": []
                }
                */

                Console.WriteLine(SeparatorLine);

                // 取出 message 的內容
                if (data.TryGetProperty("content", out var contentElement))
                {
                    var content = contentElement.GetString();
                    Console.WriteLine("Message:");
                    Console.WriteLine(SeparatorLine);
                    Console.WriteLine(content);
                    Console.WriteLine(SeparatorLine);
                }

                // 返回成功響應
                return Results.Json(new { message = "Webhook 接收成功" });
            }
            catch (Exception ex)
            {
                logger?.LogError(ex, "處理 webhook 時發生錯誤");
                return Results.Json(new { error = "處理請求時發生錯誤" }, statusCode: 500);
            }
        }
    }
}
