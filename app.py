from flask import Flask, request, jsonify

from telegram_bot import TelegramBot
from config import TELEGRAM_INIT_WEBHOOK_URL

app = Flask(__name__)
TelegramBot.init_webhook(TELEGRAM_INIT_WEBHOOK_URL)

@app.route('/webhook', methods=['POST'])
def index():
    req = request.get_json()
    bot = TelegramBot()
    try:
        bot.parse_webhook_data(req)
        success = bot.action()
        return jsonify(success=success) # TODO: Success should reflect the success of the reply
    except:
        return jsonify(success="500")

if __name__ == '__main__':
    app.run(port=5000)