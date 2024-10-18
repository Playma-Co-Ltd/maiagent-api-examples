from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

CHATBOT_ID = '<your-chatbot-id>'
FILE_PATH = '<your-file-path>'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'
assert FILE_PATH != '<your-file-path>', 'Please set your file path'


def main():
    maiagent_helper = MaiAgentHelper(API_KEY)

    response = maiagent_helper.upload_knowledge_file(CHATBOT_ID, FILE_PATH)
    print(response)

if __name__ == '__main__':
    main()
