# -*-coding:utf-8-*-

from pymongo import MongoClient

class Connection:

    def __init__(self, schema='Acme-Supermarket-Recommendations'):
        self.schema = schema
        self.client = None
        self.database = None
        self.connected = False

    def open(self):
        if not self.connected:
            self.client = MongoClient()
            self.database = self.client[self.schema]
            self.connected = True
    connect = open

    def close(self):
        if self.connected:
            self.client.close()
            self.client = None
            self.database = None
            self.connected = False
    disconnect = close

    def save_rules(self, rules):
        """
        Save a list of rules into 'rules' collection.
        """
        if self.connected and self.database is not None:
            self.database.rules.remove()
            for rule in rules:
                antecedents = rule[0]
                consequent = rule[1]
                rule = {
                    'antecedents': antecedents,
                    'consequent_id' : consequent
                }
                self.database.rules.insert_one(rule)
