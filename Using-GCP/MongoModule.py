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
        self.client = pymongo.MongoClient(self.URI)
        self.db = self.client[self.DATABASE]
        self.collection = self.db[self.COLLECTION]

    def insert_one(self, data):
        self.collection.insert_one(data)

    def insert_many(self, data):
        self.collection.insert_many(data)
 
    def find_one(self, query):
        return self.collection.find(query)

    def find_many(self):
        return list(self.collection.find({}))

    def delete_all(self):
        self.collection.delete_many({})

if __name__ == "__main__":
    import pandas as pd
    import json
    mongo = CONNECT_MONGO()
    mongo.delete_all()
