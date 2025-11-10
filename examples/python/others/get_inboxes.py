from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

assert API_KEY != '<your-api-key>', 'Please set your API key'


def main():
    maiagent_helper = MaiAgentHelper(API_KEY)

    inbox_items = maiagent_helper.get_inbox_items()
    maiagent_helper.display_inbox_items(inbox_items)


if __name__ == '__main__':
    main()
