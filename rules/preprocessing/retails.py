
import numpy

class Retails:

    def __init__(self, input_filepath, output_filepath):
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath

    def load(self):
        with open(self.input_filepath) as retail:
            transactions = numpy.array([])
            row_starts = numpy.array([0])
            for line in retail:
                line = numpy.array(line.split(), dtype='i4')
                row_starts = numpy.append(row_starts, row_starts[-1] + line.size)
                transactions = numpy.concatenate((transactions, line))

            row_ends = numpy.concatenate((row_starts, [transactions.size]))
            lengths = numpy.diff(row_ends)
            pad_lengths = numpy.max(lengths) - lengths
            pad_indices = numpy.repeat(row_ends[1:], pad_lengths)

            transactions_padded = numpy.insert(
                transactions, pad_indices, -1).reshape(-1, numpy.max(lengths))

            numpy.save(self.output_filepath, transactions_padded)
