from unittest import result
import pymongo

import configparser

config = configparser.ConfigParser()

config.read('..\config.ini')


class CONNECT_MONGO:
    URI = config['mongo']['uri']
    DATABASE = config['mongo']['database']
    COLLECTION = config['mongo']['collection']

    def __init__(self):
        self.client = pymongo.MongoClient(
            self.URI)  # connection URL to mongoDB
        self.db = self.client[self.DATABASE]  # get database
        self.collection = self.db[self.COLLECTION]  # get collection
        """
            İnsert new data to mongoDB
            return: mongo success or not
            params: data

        """

    def insert_one(self, data):
        self.collection.insert_one(data)
        """
            insert multiple data to mongoDB
            return: mongo success or not
            params: data
        """

    def insert_many(self, data):
        self.collection.insert_many(data)
        """
            Get data from mongoDB
            return: data
            params: query

        """

    def find_one(self, query):
        return self.collection.find(query)
    """
        Get multiple data from mongoDB
        return: data
        params: query
    """

    def find_many(self):
        return list(self.collection.find({}))
    """
        Delete data from mongoDB
        return: mongo success or not
        params: query
    """

    def delete_all(self):
        self.collection.delete_many({})


# History of tweets
class CONNECT_HIST:
    URI = config['mongoHistory']['uri']
    DATABASE = config['mongoHistory']['database']
    COLLECTION = config['mongoHistory']['collection']

    def __init__(self):
        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client[self.DATABASE]
        self.collection = self.db[self.COLLECTION]

    def get_sentimentHistory(self):
        """ Get all data from mongoDB

        Returns:
            list: data from mongoDB
        """
        return list(self.collection.find({}))

    def add_sentimentHistory(self, data):
        """Add new data to mongoDB

        Args:
            data (json): Data to be added to mongoDB
        """

        self.collection.insert_one(data)


# if __name__ == "__main__":
#     import pandas as pd
#     import json
#     mongo = CONNECT_MONGO()
#     mongo.delete_all()
