import os
SCALA_VERSION = '3.7.1'
SPARK_VERISON = '3.1.2'

os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages org.apache.spark:spark-sql-kafka-0-10_{SCALA_VERSION}:{SPARK_VERSION} pyspark-shell'

import findspark
findspark.init('C:\Spark')

from pyspark.sql import functions as F
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.types import StringType, StructType, StructField, FloatType
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.ml.feature import RegexTokenizer
import re
from textblob import TextBlob


# remove_links
def cleanTweet(tweet: str) -> str:
    tweet = re.sub(r'http\S+', '', str(tweet))
    tweet = re.sub(r'bit.ly/\S+', '', str(tweet))
    tweet = tweet.strip('[link]')

    # remove users
    tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))
    tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    # remove puntuation
    my_punctuation = '!"$%&\'()*+,-./:;<=>?[\\]^_`{|}~•@â'
    tweet = re.sub('[' + my_punctuation + ']+', ' ', str(tweet))

    # remove number
    tweet = re.sub('([0-9]+)', '', str(tweet))

    # remove hashtag
    tweet = re.sub('(#[A-Za-z]+[A-Za-z0-9-_]+)', '', str(tweet))

    return tweet


# Create a function to get the subjectifvity
def getSubjectivity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.subjectivity


# Create a function to get the polarity
def getPolarity(tweet: str) -> float:
    return TextBlob(tweet).sentiment.polarity


def getSentiment(polarityValue: int) -> str:
    if polarityValue < 0:
        return 'Negative'
    elif polarityValue == 0:
        return 'Neutral'
    else:
        return 'Positive'


# epoch
def write_row_in_mongo(df):
    mongoURL = "mongodb+srv://admin:admin@tweetdb.z4oyi.mongodb.net/tweetDB?retryWrites=true&w=majority"
    df.write.format("mongo").mode("append").option("uri", mongoURL).save()
    pass


if __name__ == "__main__":
    spark = SparkSession \
        .builder \
        .appName("TwitterSentimentAnalysis") \
        .config("spark.mongodb.input.uri",
                "mongodb+srv://admin:admin@tweetdb.z4oyi.mongodb.net/tweetDB?retryWrites=true&w=majorityy") \
        .config("spark.mongodb.output.uri","mongodb+srv://admin:admin@tweetdb.z4oyi.mongodb.net/tweetDB?retryWrites=true&w=majority") \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "twitter") \
        .load()

    mySchema = StructType([StructField("text", StringType(), True)])
    # Get only the "text" from the information we receive from Kafka. The text is the tweet produce by a user
    values = df.select(from_json(df.value.cast("string"), mySchema).alias("tweet"))

    df1 = values.select("tweet.*")
    clean_tweets = F.udf(cleanTweet, StringType())
    raw_tweets = df1.withColumn('processed_text', clean_tweets(col("text")))
    # udf_stripDQ = udf(stripDQ, StringType())

    subjectivity = F.udf(getSubjectivity, FloatType())
    polarity = F.udf(getPolarity, FloatType())
    sentiment = F.udf(getSentiment, StringType())

    subjectivity_tweets = raw_tweets.withColumn('subjectivity', subjectivity(col("processed_text")))
    polarity_tweets = subjectivity_tweets.withColumn("polarity", polarity(col("processed_text")))
    sentiment_tweets = polarity_tweets.withColumn("sentiment", sentiment(col("polarity")))

    '''
    all about tokenization
    '''
    # Create a tokenizer that Filter away tokens with length < 3, and get rid of symbols like $,#,...
    tokenizer = RegexTokenizer().setPattern("[\\W_]+").setMinTokenLength(3).setInputCol("processed_text").setOutputCol(
        "tokens")

    # Tokenize tweets
    tokenized_tweets = tokenizer.transform(raw_tweets)

    # en sortie on a
    tweets_df = df1.withColumn('word', explode(split(col("text"), ' '))).groupby('word').count().sort('count',
                                                                                                      ascending=False).filter(
        col('word').contains('#'))

    query = sentiment_tweets.writeStream.queryName("test_tweets") \
        .foreachBatch(write_row_in_mongo).start()
    query.awaitTermination()
