# Covid-19 Telegram Bot
Telegram bot compatible with Python 3.7. Webhooks with ngrok to Telegram bot message stream, conditional responses.

Currently under development - 4/13/2019

## To run:
1. Download ngrok into the project root directory: https://ngrok.com/download

2. Navigate the the root directory in terminal, run:
> `./ngrok http 5000`

3. Add your telegram bot token to the TOKEN variable in config.py

4. Add your ngrok https url to the NGROK_URL variable in config.py

5. Run the app server:
> $`python app.py`
