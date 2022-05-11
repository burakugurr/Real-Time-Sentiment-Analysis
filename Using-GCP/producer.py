import os
from google.cloud import pubsub_v1

import TweeterAPI
import datetime

credentials_path = '.gcp\qwiklabs-gcp-04-9595fe27b103-f5301c3cf0bc.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/qwiklabs-gcp-01-d2aa5634019d/topics/test'

# Create data to publish

api = TweeterAPI.TwitterClient()

tweets = api.get_tweets(query = 'doge coin', count = 20000)


for i in tweets:
    data = 'New Tweets'
    data = data.encode('utf-8')
    attributes = {
        'text':i['text'],
        'sentiment': i['sentiment'],
        'time': datetime.datetime.now().isoformat(),
    }

    future = publisher.publish(topic_path, data, **attributes)
    print(f'published message id {future.result()}')
