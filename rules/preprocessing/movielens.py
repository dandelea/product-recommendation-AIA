
import numpy

from ..db import MySQL

class Movielens:

    def __init__(self, transactions_filepath):
        self.transactions_filepath = transactions_filepath
        self.database = MySQL()


    def load(self):
        self.database.connect()

        transactions = numpy.array([])
        row_starts = numpy.array([0])
        users = self.database.query("SELECT id FROM users")
        for row in users:
            ratings = self.database.query(
                "SELECT movie_id, rating FROM ratings WHERE user_id = {0} AND rating = {1}".format(
                    int(row[0]), 4))

            transaction = numpy.array([r[0] for r in ratings], dtype='i4')
            row_starts = numpy.append(row_starts, row_starts[-1] + transaction.size)
            transactions = numpy.concatenate((transactions, transaction))

        row_ends = numpy.concatenate((row_starts, [transactions.size]))
        lengths = numpy.diff(row_ends)
        pad_lengths = numpy.max(lengths) - lengths
        pad_indices = numpy.repeat(row_ends[1:], pad_lengths)

        transactions_padded = numpy.insert(transactions, pad_indices, -1)
        transactions_padded = transactions_padded.reshape(-1, numpy.max(lengths))

        numpy.save(self.transactions_filepath, transactions_padded)

        self.database.close()
