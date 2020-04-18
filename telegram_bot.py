import requests
import re
import random

from datetime import datetime
from pytz import timezone
from config import TELEGRAM_SEND_MESSAGE_URL

class TelegramBot:

    def __init__(self):
        """"
        Initializes an instance of the TelegramBot class.

        Attributes:
            chat_id:str: Chat ID of Telegram chat, used to identify which conversation outgoing messages should be send to.
            text:str: Text of Telegram chat
            first_name:str: First name of the user who sent the message
            last_name:str: Last name of the user who sent the message
        """

        self.chat_id = None
        self.text = None
        self.first_name = None
        self.last_name = None


    def parse_webhook_data(self, data):
        """
        Parses Telegram JSON request from webhook and sets fields for conditional actions

        Args:
            data:str: JSON string of data
        """

        message = data['message']
        self.chat_id = message['chat']['id']
        self.incoming_message_text = message['text'].lower()
        self.first_name = message['from']['first_name']


    def action(self):
        """
        Conditional actions based on set webhook data.

        Returns:
            bool: True if the action was completed successfully else false
        """

        success = None

        # Commands
        if self.incoming_message_text == "/start":
            self.outgoing_message_text = "Hey {}, let\'s get started!\n\nType /AnyCountryName into the chat to get COVID-19 information on that country (e.g /Singapore, or /singapore or /Sg) or type /all to get global statistics".format(self.first_name)
            success = self.send_message()

        elif self.incoming_message_text == "/help":
            self.outgoing_message_text = 'Type /AnyCountryName into the chat to get COVID-19 information on that country (e.g /Singapore, or /singapore or /Sg) or type /all to get global statistics'
            success = self.send_message()
        
        # Global stats
        elif self.incoming_message_text == "/all":
            res = requests.get('https://corona.lmao.ninja/v2/all')
            response_data = res.json()
            
            localtz = timezone('Asia/Singapore')
            t = str(response_data["updated"])[:10] + "." + str(response_data["updated"])[10:]
            dt_unaware = datetime.utcfromtimestamp(float(t))
            dt_aware = dt_unaware.astimezone(localtz).strftime('%a, %d %b %Y  %H:%M:%S (SGT)')
            
            self.outgoing_message_text = "Hey {}!\n\nThere are *{}* cases globally in *{}* affected countries. *{}* of these cases are active today.\n\nRecovered: {}\nTotal deaths: {}\nCases per one million: {}\nDeaths per one million: {}\nTests per one million: {}\n\n\n_Last updated {}_" \
                                        .format(self.first_name,\
                                        f"{response_data['cases']:,}",\
                                        f"{response_data['affectedCountries']:,}",\
                                        f"{response_data['active']:,}",\
                                        f"{response_data['recovered']:,}",\
                                        f"{response_data['deaths']:,}",\
                                        f"{response_data['casesPerOneMillion']:,}",\
                                        f"{response_data['deathsPerOneMillion']:,}",\
                                        f"{response_data['testsPerOneMillion']:,}",\
                                        dt_aware)
           
            success = self.send_message()

        # Special case for South korea due to API limitation
        SOUTH_KOREA_NAMES = ['korea', 'south_korea', 'skorea', 'kor', 'southkorea']
        elif (str(self.incoming_message_text) in SOUTH_KOREA_NAMES):
            res = requests.get('https://corona.lmao.ninja/v2/countries/south%20korea') 
            response_data = res.json()
            
            try:
                localtz = timezone('Asia/Singapore')
                t = str(response_data["updated"])[:10] + "." + str(response_data["updated"])[10:]
                dt_unaware = datetime.utcfromtimestamp(float(t))
                dt_aware = dt_unaware.astimezone(localtz).strftime('%a, %d %b %Y  %H:%M:%S (SGT)')
                
                self.outgoing_message_text = "Hi {}!\n\n{} has a total of *{}* case(s), with *{}* new case(s) reported today.\n\nActive cases: {}\nDeaths today: {}\nTotal deaths: {}\nCritical: {}\nRecovered: {}\nTotal tests performed: {}\nTests per one million: {}\n\n\n_Last updated {}_" \
                                            .format(self.first_name,\
                                            response_data['country'],\
                                            f"{response_data['cases']:,}",\
                                            f"{response_data['todayCases']:,}",\
                                            f"{response_data['active']:,}",\
                                            f"{response_data['todayDeaths']:,}",\
                                            f"{response_data['deaths']:,}",\
                                            f"{response_data['critical']:,}",\
                                            f"{response_data['recovered']:,}",\
                                            f"{response_data['tests']:,}",\
                                            f"{response_data['testsPerOneMillion']:,}",\
                                            dt_aware)
                success = self.send_message()   

        # All other countries
        elif re.match(r"^\/[a-zA-Z]+$", self.incoming_message_text) is not None:
            countryName = str(self.incoming_message_text).strip('/')
            res = requests.get('https://corona.lmao.ninja/v2/countries/'+ countryName) 
            response_data = res.json()
            
            try:
                localtz = timezone('Asia/Singapore')
                t = str(response_data["updated"])[:10] + "." + str(response_data["updated"])[10:]
                dt_unaware = datetime.utcfromtimestamp(float(t))
                dt_aware = dt_unaware.astimezone(localtz).strftime('%a, %d %b %Y  %H:%M:%S (SGT)')
                
                self.outgoing_message_text = "Hi {}!\n\n{} has a total of *{}* case(s), with *{}* new case(s) reported today.\n\nActive cases: {}\nDeaths today: {}\nTotal deaths: {}\nCritical: {}\nRecovered: {}\nTotal tests performed: {}\nTests per one million: {}\n\n\n_Last updated {}_" \
                                            .format(self.first_name,\
                                            response_data['country'],\
                                            f"{response_data['cases']:,}",\
                                            f"{response_data['todayCases']:,}",\
                                            f"{response_data['active']:,}",\
                                            f"{response_data['todayDeaths']:,}",\
                                            f"{response_data['deaths']:,}",\
                                            f"{response_data['critical']:,}",\
                                            f"{response_data['recovered']:,}",\
                                            f"{response_data['tests']:,}",\
                                            f"{response_data['testsPerOneMillion']:,}",\
                                            dt_aware)
                success = self.send_message()   

            except:
                self.outgoing_message_text = response_data["message"]
                success = self.send_message()     
        
        # Keyword Matching
        if success is None:     
            GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
            GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
            GRATITUDE_INPUTS = ('thanks', 'thank you', 'thank', 'thank you')
            GRATITUDE_RESPONSES = ('You\'re welcome!', 'No problem', 'Of course! See you again :)', 'My pleasure!')
            FAREWELL_INPUTS = ('bye', 'see you', 'good day', 'byebye', 'sayonara', 'g\'day', 'adios')
            FAREWELL_RESPONSES = ('Bye!', 'Bye! take care....', 'Take care!', 'See you soon...', 'good day, mate :)', 'Adios...', '*Bloop Bloop* Ciao!')
            
            sentence = str(self.incoming_message_text).lower()
            

            for word in sentence.split():
                
                if word.lower() in GREETING_INPUTS:
                    self.outgoing_message_text =  random.choice(GREETING_RESPONSES)
                    success = self.send_message()  
                    break
                if word.lower() in GRATITUDE_INPUTS:
                    self.outgoing_message_text = random.choice(GRATITUDE_RESPONSES)
                    success = self.send_message()  
                    break
                if word.lower() in FAREWELL_INPUTS:
                    self.outgoing_message_text = random.choice(FAREWELL_RESPONSES)
                    success = self.send_message()  
                    break

        return success


    def send_message(self):
        """
        Sends message to Telegram servers.
        """

        res = requests.get(TELEGRAM_SEND_MESSAGE_URL.format(self.chat_id, self.outgoing_message_text))

        return True if res.status_code == 200 else False
    

    @staticmethod
    def init_webhook(url):
        """
        Initializes the webhook

        Args:
            url:str: Provides the telegram server with a endpoint for webhook data
        """

        requests.get(url)


