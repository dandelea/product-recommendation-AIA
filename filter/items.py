
from math import isnan

import os
import numpy
import tables

def run(ratings_matrix, similarity_matrix, user, product, N=5):
    """
    Gives a prediction for a product.

    Input:
            user: user to make the prediction for
            product: Product of prediction
            N: Neighbour distance.
            ratings_matrix : Ratings matrix. Ratings are numbers 1-5. Rows are
            users, columns are items.
            First element of each row is the User ID. First element of
            each column is the Product ID.

                            I1  I2  I3
                    A1  4   5   2

                    A2  3   1   4

                    A3  3   3   1
    """

    similarity_file = tables.openFile(similarity_matrix, mode='r')
    similarity = similarity_file.root.data
    ratings_matrix_file = tables.openFile(ratings_matrix, mode='r')
    ratings_matrix = ratings_matrix_file.root.data

    row_of_user = numpy.where(ratings_matrix[:, 0] == user)[0]
    column_of_product = numpy.where(ratings_matrix[0, :] == product)[0]

    if len(row_of_user) > 0 and len(column_of_product) > 0:
        # User / Product in the system
        row_of_user = row_of_user[0]
        column_of_product = column_of_product[0]

        if ratings_matrix[row_of_user, column_of_product] > 0:
                # Already rated
            result = ratings_matrix[row_of_user, column_of_product]
        else:
            user_ratings = ratings_matrix[row_of_user, :]

            product_ids = numpy.array(similarity[0, :], dtype='i4')

            user_products_rated = product_ids[numpy.nonzero(user_ratings)]
            
            product_similarities = similarity[
                numpy.where(similarity[:, 0] == product)[0][0], :]

            similarities = numpy.fromiter(zip(product_similarities[1:], product_ids[1:]),
                                       dtype=[('s', 'f4'), ('p', 'i4')])
            similarities = numpy.delete(similarities,
                                        numpy.where(similarities['p'] == product)[0][0])
            similarities = similarities[numpy.argsort(similarities,
                                                      order=('s', 'p'))[::-1]]
            similarities = similarities[numpy.in1d(similarities['p'],
                                        user_products_rated)]

            similarities = similarities[:N]
            user_ratings = user_ratings[similarities['p']]

            numerator = numpy.sum(similarities['s'] * user_ratings)
            denominator = numpy.sum(similarities['s'])

            if denominator == 0:
                result = 0
            else:
                result = numerator / denominator

        similarity_file.close()
        ratings_matrix_file.close()
        return result
    else:
        similarity_file.close()
        ratings_matrix_file.close()
        raise ValueError("Error: User / Product not registered in the system")


def compute_similarity(ratings_matrix_file, similarity_matrix_file):
    """
    Calculate similarity for all pairs of products.

    ratings_matrix : Ratings matrix. Ratings are numbers 1-5. Rows are users,
    columns are items.
    First element of each row is the User ID. First element of each column
    is the Product ID.

                    I1  I2  I3
            A1  4   5   2

            A2  3   1   4

            A3  3   3   1
    """

    ratings_matrix = tables.openFile(ratings_matrix_file, mode='r').root.data

    products = ratings_matrix.shape[1]

    similarity_file = tables.openFile(
        'tmp.hdf5', mode='w')
    filters = tables.Filters(complevel=5, complib='blosc')
    data_storage = similarity_file.createCArray(
        similarity_file.root, 'data',
        tables.Float64Atom(),
        shape=(products, products),
        filters=filters)

    data_storage[0, :] = ratings_matrix[0, :]   # IDs de productos
    data_storage[:, 0] = ratings_matrix[0, :]   # IDs de productos

    for product1 in range(1, products):  # Se excluye la columna de IDs
        for product2 in range(product1,
                              products):    # Se excluye la columna de IDs

            if product1 != product2:

                p1_ratings = ratings_matrix[1:, product1]
                p2_ratings = ratings_matrix[1:, product2]

                p1_rating_indices = numpy.nonzero(p1_ratings)[0]
                p2_rating_indices = numpy.nonzero(p2_ratings)[0]

                common_indices = numpy.intersect1d(p1_rating_indices,
                                                   p2_rating_indices)

                if common_indices.size > 0:
                    means = numpy.fromiter(
                        (numpy.mean(x[numpy.nonzero(x)[0]])
                         for x in
                         ratings_matrix[common_indices + 1, 1:]),
                        dtype=numpy.float64
                    )

                    p1_ratings_values = p1_ratings[common_indices] - means
                    p2_ratings_values = p2_ratings[common_indices] - means

                    numerator = numpy.sum(
                        p1_ratings_values * p2_ratings_values)

                    p1_denominator = numpy.sqrt(
                        numpy.sum(numpy.power(p1_ratings_values, 2)))
                    p2_denominator = numpy.sqrt(
                        numpy.sum(numpy.power(p2_ratings_values, 2)))

                    similarity = numerator / \
                        (p1_denominator * p2_denominator)

                    # product2_id = str(ratings_matrix[0, product2])
                else:
                    similarity = 0.0
            else:
                similarity = 1.0
            
            if isnan(similarity):
                break
            data_storage[product1, product2] = similarity
            data_storage[product2, product1] = similarity

    ratings_matrix.close()
    similarity_file.close()

    if os.path.isfile(similarity_matrix_file):
        os.remove(similarity_matrix_file)
    os.rename('tmp.hdf5', similarity_matrix_file)
