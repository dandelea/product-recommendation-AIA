
from db import Mongo
import numpy
import tables

def compute_ratings_matrix(ratings_matrix_file):
    """
    Computes the rating matrix
        Input:
            ratings_matrix_file: Filename output rating matrix
    """

    mongo = Mongo('Acme-Supermarket')
    mongo.connect()

    matrix_file = ratings_matrix_file
    hdf5_matrix = tables.openFile(matrix_file, mode='w')

    filters = tables.Filters(complevel=5, complib='blosc')

    products = mongo.database.products.find({}, {'_id': 1})
    products = [p['_id'] for p in products]
    products = numpy.concatenate((numpy.array([-1]), products))
    products_count = mongo.database.products.count()

    customers = mongo.database.actors.find({'_type': 'Customer'}, {'_id': 1})
    customers = [c['_id'] for c in customers]
    customers_count = mongo.database.actors.count({'_type': 'Customer'})

    data_storage = hdf5_matrix.createEArray(
        hdf5_matrix.root, 'data',
        tables.UInt32Atom(),
        shape=(0, products_count + 1),
        filters=filters,
        expectedrows=customers_count)

    data_storage.append(products[:][None])
    for customer_id in customers:
        # Each column 0: Customer IDs
        # Product ratings in columns 1+
        row = numpy.zeros((products_count + 1,))

        row[0] = customer_id
        ratings = mongo.database.rates.find({'customer_id': customer_id},
                                            {'product_id': 1, 'value': 1})

        for rating in ratings:
            row[numpy.where(products == rating['product_id'])[0][0]] = rating[
                'value']

        data_storage.append(row[:][None])

    hdf5_matrix.close()
    mongo.disconnect()

    return matrix_file
