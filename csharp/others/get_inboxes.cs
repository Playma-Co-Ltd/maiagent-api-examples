
using MaiAgentHelper = utils.MaiAgentHelper;

using System.Diagnostics;

public static class get_inboxes {
    
    public static string API_KEY = "<your-api-key>";
    
    public static void main() {
        var maiagent_helper = MaiAgentHelper(API_KEY);
        var inbox_items = maiagent_helper.get_inbox_items();
        maiagent_helper.display_inbox_items(inbox_items);
    }
    
    static get_inboxes() {
        main();
    }
    
    static get_inboxes() {
        Debug.Assert(API_KEY != "<your-api-key>");
        Debug.Assert("Please set your API key");
        if (@__name__ == "__main__") {
        }
    }
}
