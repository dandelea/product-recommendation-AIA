
import numpy

from db import Mongo

class AcmeSupermarket:

    def __init__(self, transactions_filepath):
        self.schema = 'Acme-Supermarket-Recommendations'
        self.transactions_filepath = transactions_filepath
        self.database = Mongo(self.schema)

    def load(self):
        self.database.connect()
        purchases = self.database.database.purchases.find()

        transactions = numpy.array([])

        i = 0
        row_starts = numpy.array([0])
        for purchase in purchases:
            i += 1
            purchase_id = purchase['_id']
            purchase_lines = self.database.database.purchase_lines.find({'purchase_id': purchase_id})
            transaction = numpy.array([line['product_id'] for line in purchase_lines], dtype='i4')
            row_starts = numpy.append(row_starts, row_starts[-1] + transaction.size)
            transactions = numpy.concatenate((transactions, transaction))

        row_ends = numpy.concatenate((row_starts, [transactions.size]))
        lengths = numpy.diff(row_ends)
        pad_lengths = numpy.max(lengths) - lengths
        pad_indices = numpy.repeat(row_ends[1:], pad_lengths)

        transactions_padded = numpy.insert(
            transactions, pad_indices, -1).reshape(-1, numpy.max(lengths))

        numpy.save(self.transactions_filepath, transactions_padded)

        self.database.close()

    def save_rules(self, rules):
        self.database.save_rules(rules)
