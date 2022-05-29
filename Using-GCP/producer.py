import os
from google.cloud import pubsub_v1

import TweeterAPI
import datetime
# logglerv2
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler("..\logs\producer.log",
                                                  encoding='utf-8')])
# configure 
import configparser

config = configparser.ConfigParser()
config.read('..\config.ini')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['googlecloud']['credentials_path']



class Publisher:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = config['googlecloud']['topic_path']

# Create data to publish
    def Analyzer(self,search_topic,count_size):

        api = TweeterAPI.TwitterClient()

        tweets = api.get_tweets(query=str(search_topic), count=count_size)
        # tweets = api.get_tweets(query="russia", count=2000)

        for i in tweets:
            data = 'New Tweets'
            data = data.encode('utf-8')
            attributes = {
                'text': i['text'],
                'search_topic':str(search_topic),
                'sentiment': i['sentiment'],
                'time': datetime.datetime.now().isoformat(),
            }

        future = self.publisher.publish(self.topic_path, data, **attributes)
        logging.info("Published tweet: {}".format(future.result()))

if __name__ == "__main__":
    publisher = Publisher()
    publisher.Analyzer("Bitcoin",2000)