import os
from gevent import config
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import MongoModule

import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler("..\logs\consumer.log",
                                                  encoding='utf-8')])


# connect to mongoDB 
mongo = MongoModule.CONNECT_MONGO()

import configparser
config = configparser.ConfigParser()

config.read('..\config.ini')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['googlecloud']['credentials_path']


timeout = config.getint('gevent', 'timeout')                                                             

subscriber = pubsub_v1.SubscriberClient()
subscription_path = config['googlecloud']['subscription_path']


def callback(message):
    if message.attributes:
        logging.info('Received message: {}'.format(message.data))

        for key in message.attributes:
            value = message.attributes.get(key)

            mongo.insert_one(
                {'text': value,
                'search_topic': message.attributes.get('search_topic'),
                'sentiment': message.attributes.get('sentiment'), 
                'time': message.attributes.get('time')
                })
            

    message.ack()           


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for messages on {subscription_path}')


with subscriber:                                                
    try:
        # streaming_pull_future.result(timeout=timeout)
        streaming_pull_future.result()

    except TimeoutError:
        logging.warning('Listening for messages timed out after {} seconds'.format(timeout))
        streaming_pull_future.cancel()                          
        streaming_pull_future.result()                         

