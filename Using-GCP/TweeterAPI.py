import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk


nltk.downloader.download('vader_lexicon')
import configparser

config = configparser.ConfigParser()

config.read('config.ini')



class TwitterClient(object):
	'''
	Generic Twitter Class for sentiment analysis.
	'''
	def __init__(self):
		"""setup twitter API
		"""
		# keys and tokens from the Twitter Dev Console
		consumer_key = config['twitter']['consumer_key']
		consumer_secret = config['twitter']['consumer_secret']
		access_token = config['twitter']['access_token']
		access_token_secret = config['twitter']['access_token_secret']

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
		"""Clean tweet text by removing links, special characters, etc.

		Args:
			tweet (string): Tweet to clean.

		Returns:
			string: Cleaned tweet.
		"""
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(^\w+:\/\/\S+)", " ", tweet).split())

	def get_tweet_sentiment(self, tweet):
		"""sentiment analysis of tweet using Vader algorithm V1.

		Args:
			teweet (string): Tweet to get sentiment of.

		Returns:
			string: Sentiment of tweet.
		"""	
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
		""" Get sentiment of tweet using Vader algorithm.

		Args:
			teweet (string): Tweet to get sentiment of.

		Returns:
			string: Sentiment of tweet.
		"""		
		analysis = TextBlob(self.clean_tweet(teweet))
		score = SentimentIntensityAnalyzer().polarity_scores(teweet)


		if analysis.sentiment.polarity > 0:
			return 'positive'
		elif analysis.sentiment.polarity == 0:
			return 'neutral'
		else:
			return 'negative'


	def get_tweets(self, query, count = 10):
		""" Get tweets from Twitter

		Args:
			query (string): Search query to run against Twitter API.
			count (int, optional): Return tweet count. Defaults to 10.

		Returns:
			list: List of tweets.
		"""		
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



