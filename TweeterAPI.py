import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.downloader.download('vader_lexicon')

#https://www.syntio.net/en/labs-musings/streaming-data-from-twitter-to-gcp
class TwitterClient(object):
	'''
	Generic Twitter Class for sentiment analysis.
	'''
	def __init__(self):
		'''
		Class constructor or initialization method.
		'''
		# keys and tokens from the Twitter Dev Console
		consumer_key = 'BfE01vmJb8SalHhd676ln6D8H'
		consumer_secret = '4Vji5nqLwHMaf0Pbznz4XXQY236CRIioA9txsYs01jUQvncBuI'
		access_token = '2664142236-LDD4b2VWqz02S3UVxiPeNXR9eZNhbsIFofWyQ5g'
		access_token_secret = 'IUaRmRLLLUsomUusfr7B5zx3hcNms38A7HDIBTwMujysZ'

		# attempt authentication
		try:
			# create OAuthHandler object
			self.auth = OAuthHandler(consumer_key, consumer_secret)
			# set access token and secret
			self.auth.set_access_token(access_token, access_token_secret)
			# create tweepy API object to fetch tweets
			self.api = tweepy.API(self.auth)
		except:
			print("Error: Authentication Failed")

	def clean_tweet(self, tweet):
		'''
		Utility function to clean tweet text by removing links, special characters
		using simple regex statements.
		'''
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(^\w+:\/\/\S+)", " ", tweet).split())

	def get_tweet_sentiment(self, tweet):
		'''
		Utility function to classify sentiment of passed tweet
		using textblob's sentiment method
		'''
		# create TextBlob object of passed tweet text
		analysis = TextBlob(self.clean_tweet(tweet))
		# set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'

	def sentimentV2(self,teweet):

		analysis = TextBlob(self.clean_tweet(teweet))
		score = SentimentIntensityAnalyzer().polarity_scores(teweet)


		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'


	def get_tweets(self, query, count = 10):
		'''
		Main function to fetch tweets and parse them.
		'''
		# empty list to store parsed tweets
		tweets = []

		try:
			# call twitter api to fetch tweets
			fetched_tweets = self.api.search(q = query, count = count)

			# parsing tweets one by one
			for tweet in fetched_tweets:
				# empty dictionary to store required params of a tweet
				parsed_tweet = {}

				# saving text of tweet
				parsed_tweet['text'] = tweet.text
				# saving sentiment of tweet
				#parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

				parsed_tweet['sentiment'] = self.sentimentV2(tweet.text)

				# appending parsed tweet to tweets list
				if tweet.retweet_count > 0:
					# if tweet has retweets, ensure that it is appended only once
					if parsed_tweet not in tweets:
						tweets.append(parsed_tweet)
				else:
					tweets.append(parsed_tweet)

			# return parsed tweets
			return tweets

		except tweepy.TweepError as e:
			# print error (if any)
			print("Error : " + str(e))



