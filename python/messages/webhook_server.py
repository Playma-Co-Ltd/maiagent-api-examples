import json
import logging
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        logging.info(f'收到 webhook 請求: {data}')

        # 處理 Webhook Request
        print('=' * 100)
        print('Request:')
        print('=' * 100)
        print(json.dumps(data, indent=4, ensure_ascii=False))
        # 範例：
        """
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
        """
        print('=' * 100)

        # 取出 message 的內容
        content = data['content']
        print('Message:')
        print('=' * 100)
        print(content)
        # 範例：
        """
        這是 webhook 測試訊息
        """
        print('=' * 100)

        return jsonify({'message': 'Webhook 接收成功'}), 200
    else:
        return jsonify({'error': '僅支持 POST 請求'}), 405


if __name__ == '__main__':
    port = 6666

    process = subprocess.Popen(['lt', '--port', str(port)], stdout=subprocess.PIPE)
    public_url = process.stdout.readline().decode().strip()

    print('=' * 100)
    print('Webhook Server 正在運行。')
    print(f'Public URL: {public_url}')
    print(f'Webhook endpoint: {public_url}/webhook')
    print('=' * 100)

    app.run(host='0.0.0.0', port=port, debug=True)
