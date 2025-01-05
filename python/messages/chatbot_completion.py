from utils import MaiAgentHelper
from utils.config import API_KEY, BASE_URL, CHATBOT_ID

# Configuration (override env variables if needed)
TEXT_MESSAGE = 'Give me a joke'

# Optional: Path to image file if you want to test with attachment
IMAGE_PATH = None  # Set to '../images/get_api_key.png' to test with image


def main():
    maiagent_helper = MaiAgentHelper(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    try:
        # Handle attachment if provided
        attachments = None
        if IMAGE_PATH:
            # First upload the attachment
            upload_response = maiagent_helper.upload_attachment(None, IMAGE_PATH)
            # Prepare attachment data
            attachments = [{
                'id': upload_response['id'],
                'type': 'image',
                'filename': upload_response['filename'],
                'file': upload_response['file'],
            }]
        
        # Get streaming completion response
        for data in maiagent_helper.create_chatbot_completion(
            CHATBOT_ID,
            TEXT_MESSAGE,
            attachments=attachments
        ):
            if 'content' in data:
                print(f"Received content: {data['content']}")
            if 'citations' in data:
                print(f"Citations: {data['citations']}")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == '__main__':
    main()
