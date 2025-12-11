using System;

namespace MaiAgentExamples
{
    /// <summary>
    /// Main entry point for MaiAgent C# Examples
    ///
    /// This project contains multiple example files demonstrating various MaiAgent API features.
    /// Each example can be run independently by calling its Main method.
    ///
    /// Examples include:
    /// - Batch QA: upload_batch_qa_file.cs, download_batch_qa_excel.cs
    /// - Messages: send_message.cs, send_image_message.cs, upload_attachment.cs, chatbot_completion.cs
    /// - FAQs: add_faq.cs
    /// - Assistants: create_assistant.cs, update_assistant.cs
    /// - Others: get_inboxes.cs, webhook_server.cs
    /// - Knowledge Bases: Various examples in the knowledges folder
    ///
    /// To run a specific example, you can:
    /// 1. Call the example's Main method from here
    /// 2. Or use the C# Top-level program feature with the specific file
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=".PadRight(80, '='));
            Console.WriteLine("MaiAgent C# API Examples");
            Console.WriteLine("=".PadRight(80, '='));
            Console.WriteLine();
            Console.WriteLine("This project contains multiple standalone examples.");
            Console.WriteLine("To run a specific example, please:");
            Console.WriteLine();
            Console.WriteLine("1. Navigate to the example file you want to run");
            Console.WriteLine("2. Update the configuration values (API_KEY, etc.)");
            Console.WriteLine("3. Call the example's Main method programmatically");
            Console.WriteLine();
            Console.WriteLine("Available Examples:");
            Console.WriteLine("  - Batch QA: UploadBatchQAFile, DownloadBatchQAExcel");
            Console.WriteLine("  - Messages: SendMessage, SendImageMessage, UploadAttachment, ChatbotCompletion");
            Console.WriteLine("  - FAQs: AddFAQ");
            Console.WriteLine("  - Assistants: CreateAssistant, UpdateAssistant");
            Console.WriteLine("  - Others: GetInboxes, WebhookServer");
            Console.WriteLine();
            Console.WriteLine("Example usage:");
            Console.WriteLine("  await MaiAgentExamples.Messages.SendMessage.Main(args);");
            Console.WriteLine();
            Console.WriteLine("=".PadRight(80, '='));
        }
    }
}
