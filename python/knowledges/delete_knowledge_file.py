from utils import MaiAgentHelper

API_KEY = '<your-api-key>'

CHATBOT_ID = '<your-chatbot-id>'

FILE_ID = '<your-files-id>'

API_KEY = 'XYwskPyU.EtcwbIFBbrbuLyuH4m9cL3FhXFdRPxOM'
CHATBOT_ID = '6d5583c0-9c71-4838-bb2d-202ebc6d9075'
FILE_ID = 'dc307309-f7b8-4ae5-a5d7-927a6af5cbe0'

assert API_KEY != '<your-api-key>', 'Please set your API key'
assert CHATBOT_ID != '<your-chatbot-id>', 'Please set your chatbot id'
assert FILE_ID != '<your-files-id>', 'Please set your files id'


if __name__ == "__main__":
    maiagent_helper = MaiAgentHelper(API_KEY)

    maiagent_helper.delete_knowledge_file(CHATBOT_ID, FILE_ID)
