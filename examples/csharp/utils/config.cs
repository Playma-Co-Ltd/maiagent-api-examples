
using System;
using System.IO;

namespace Utils
{
    public static class Config
    {
        // Try to load .env file if it exists
        // Note: C# doesn't have built-in .env support like Python's dotenv
        // You may need to install a NuGet package like DotNetEnv for full .env support
        // For now, we'll use Environment.GetEnvironmentVariable

        // API Configuration
        public static string API_KEY = Environment.GetEnvironmentVariable("MAIAGENT_API_KEY") ?? "<Please set your API key>";
        public static string BASE_URL = Environment.GetEnvironmentVariable("MAIAGENT_BASE_URL") ?? "<Please set your base url>";

        // Chatbot Configuration
        public static string CHATBOT_ID = Environment.GetEnvironmentVariable("MAIAGENT_CHATBOT_ID") ?? "<Please set your chatbot id>";

        // Web Chat Configuration
        public static string WEB_CHAT_ID = Environment.GetEnvironmentVariable("MAIAGENT_WEB_CHAT_ID") ?? "<Please set your webchat id>";

        // Storage Configuration
        public static string STORAGE_URL = Environment.GetEnvironmentVariable("MAIAGENT_STORAGE_URL") ?? "<Please set your storage url>";
    }
}
