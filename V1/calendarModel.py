from flask import current_app
from V1.response import ResponseAPI
from pymongo import MongoClient
from V1.logger import logger
import logging
import re

p = re.compile('.*')

# logging.basicConfig(filename='logs.log', level=logging.ERROR, format='%(asctime)s:%(name)s:%(message)s')

class CalendarModel:

    def __init__(self):
        connection_string = 'mongodb://localhost:27017/'
        self.client = MongoClient(connection_string)
        self.database = self.client.economic_calendar
        self.collection = self.database.records
        self.connection_flag = False

        try :
            self.database.list_collection_names()
            self.connection_flag = True
        except :
            logger.critical("database connection error.")
            self.connection_flag = False
            return ResponseAPI.send(status_code=401, message='database connection error.')

    
    def create_docs(self, docs):
        """ doc parameter is a list of dictrionaries each one are representing a reocord from calendar """
        try :
            self.collection.insert_many(docs)
            return 0
        except :
            return -1


    def all_docs(self):
        if self.connection_flag :
            return self.collection.find({},{'_id':0})
        else :
            return -1

    def last_doc(self):
        if self.connection_flag :
            return list(self.collection.find({},{'_id':0}).sort([('timestamp', -1)]).limit(1))
        else :
            return -1

    def delete_docs(self, year, week):
        if self.connection_flag :
            self.collection.delete_many({'year':year, 'week':week})
        else :
            return -1

    def search_by_info(self, source_name, currency_name, impact, from_timestamp, to_timestamp):
        if self.connection_flag :
            query={ "source_name" : source_name if source_name.lower() != 'all' else p,
                    "currency_name" : currency_name if currency_name.lower() != 'all' else p,
                    "impact" : impact if impact != 'all' else p,
                    "$and": [
                    { 'timestamp': {'$gte' : from_timestamp}},
                    { 'timestamp': {'$lte' : to_timestamp}}
                    ]
                }
            res = self.collection.find(query, {'_id':0})
            return res
        else :
            return -1

    def search_by_week_and_year(self, year, week):
        if self.connection_flag :
            query = { "year" : year if year.lower() != 'any' else p,
                      "week" : week if week.lower() != 'any' else p
                    }
            res = self.collection.find(query, {'_id':0})
            return res
        else :
            return -1
