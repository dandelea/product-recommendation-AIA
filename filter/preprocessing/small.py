
from ..db import Mongo
import numpy
import tables

def compute_ratings_matrix(ratings_matrix_file):
    """
    Computes the rating matrix. The study case is the small example from class.
        Input:
            ratings_matrix_file: Filename output rating matrix
    """

    mongo = Mongo("SmallExample-Filter")
    mongo.connect()
    mongo.database.drop_database('SmallExample-Filter')

    mongo.database.users.insert_one({"_id": 0, "name": "Alicia"})
    mongo.database.users.insert_one({"_id": 1, "name": "Usuario1"})
    mongo.database.users.insert_one({"_id": 2, "name": "Usuario2"})
    mongo.database.users.insert_one({"_id": 3, "name": "Usuario3"})
    mongo.database.users.insert_one({"_id": 4, "name": "Usuario4"})
    mongo.database.items.insert_one({"_id": 1, "name": "Item1"})
    mongo.database.items.insert_one({"_id": 2, "name": "Item2"})
    mongo.database.items.insert_one({"_id": 3, "name": "Item3"})
    mongo.database.items.insert_one({"_id": 4, "name": "Item4"})
    mongo.database.items.insert_one({"_id": 5, "name": "Item5"})
    mongo.database.ratings.insert_one({"user_id": 0, "item_id": 1, "value": 5})
    mongo.database.ratings.insert_one({"user_id": 0, "item_id": 2, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 0, "item_id": 3, "value": 4})
    mongo.database.ratings.insert_one({"user_id": 0, "item_id": 4, "value": 4})
    mongo.database.ratings.insert_one({"user_id": 1, "item_id": 1, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 1, "item_id": 2, "value": 1})
    mongo.database.ratings.insert_one({"user_id": 1, "item_id": 3, "value": 2})
    mongo.database.ratings.insert_one({"user_id": 1, "item_id": 4, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 1, "item_id": 5, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 2, "item_id": 1, "value": 4})
    mongo.database.ratings.insert_one({"user_id": 2, "item_id": 2, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 2, "item_id": 3, "value": 4})
    mongo.database.ratings.insert_one({"user_id": 2, "item_id": 4, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 2, "item_id": 5, "value": 5})
    mongo.database.ratings.insert_one({"user_id": 3, "item_id": 1, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 3, "item_id": 2, "value": 3})
    mongo.database.ratings.insert_one({"user_id": 3, "item_id": 3, "value": 1})
    mongo.database.ratings.insert_one({"user_id": 3, "item_id": 4, "value": 5})
    mongo.database.ratings.insert_one({"user_id": 3, "item_id": 5, "value": 4})
    mongo.database.ratings.insert_one({"user_id": 4, "item_id": 1, "value": 1})
    mongo.database.ratings.insert_one({"user_id": 4, "item_id": 2, "value": 5})
    mongo.database.ratings.insert_one({"user_id": 4, "item_id": 3, "value": 5})
    mongo.database.ratings.insert_one({"user_id": 4, "item_id": 4, "value": 2})
    mongo.database.ratings.insert_one({"user_id": 4, "item_id": 5, "value": 1})

    matrix_file = ratings_matrix_file
    hdf5_matrix = tables.openFile(matrix_file, mode='w')

    filters = tables.Filters(complevel=5, complib='blosc')

    items = mongo.database.items.find({}, {'_id': 1})
    items = [i['_id'] for i in items]
    items = numpy.concatenate((numpy.array([-1]), items))
    items_count = mongo.database.items.count()

    users = mongo.database.users.find({}, {'_id': 1})
    users = [u['_id'] for u in users]
    users_count = mongo.database.users.count()

    data_storage = hdf5_matrix.createEArray(
        hdf5_matrix.root, 'data',
        tables.UInt32Atom(),
        shape=(0, items_count + 1),
        filters=filters,
        expectedrows=users_count)

    data_storage.append(items[:][None])
    for user_id in users:
        # Each column 0: User IDs
        # Item ratings in columns 1+
        row = numpy.zeros((items_count + 1,))

        row[0] = user_id
        ratings = mongo.database.ratings.find({'user_id': user_id},
                                              {'item_id': 1, 'value': 1})

        for rating in ratings:
            row[numpy.where(items == rating['item_id'])[0][0]] = rating[
                'value']

        data_storage.append(row[:][None])

    hdf5_matrix.close()
    mongo.close()

    return matrix_file
