using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Utils;

namespace MaiAgentExamples.Others
{
    public static class GetInboxes
    {
        public static string API_KEY = "<your-api-key>";

        public static async Task Main(string[] args)
        {
            Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");

            var maiagentHelper = new MaiAgentHelper(API_KEY);
            var inboxItems = await maiagentHelper.GetInboxItemsAsync();
            maiagentHelper.DisplayInboxItems(inboxItems);
        }
    }
}
