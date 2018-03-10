
import numpy
import tables
import time

def run(ratings_matrix, similarity_matrix, user, N=5):
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

    similarity_file = tables.open_file(similarity_matrix, mode='r')
    similarity = similarity_file.root.data
    ratings_matrix_file = tables.open_file(ratings_matrix, mode='r')
    ratings_matrix = ratings_matrix_file.root.data

    row_of_user = numpy.where(ratings_matrix[:, 0] == user)[0]
    
    if len(row_of_user) == 0:
        similarity_file.close()
        ratings_matrix_file.close()
        raise ValueError("Error: User not registered in the system")
    
    row_of_user = row_of_user[0]
    product_ids = numpy.array(similarity[0, 1:], dtype='i4')
    user_ratings = ratings_matrix[row_of_user, :]
    user_products_rated = product_ids[numpy.nonzero(user_ratings)]
    
    estimated_ratings = []
    
    for product in product_ids:
        column_of_product = numpy.where(ratings_matrix[0, :] == product)[0]
        column_of_product = column_of_product[0]

        if ratings_matrix[row_of_user, column_of_product] > 0:
             continue
        else:
            product_similarities = similarity[
                numpy.where(similarity[:, 0] == product)[0][0], :]

            similarities = numpy.fromiter(zip(product_similarities[1:], product_ids),
                                       dtype=[('s', 'f4'), ('p', 'i4')])                                 
                                       
            similarities = numpy.delete(similarities,
                                     numpy.where(similarities['p'] == product)[0][0])
            similarities = similarities[numpy.argsort(similarities,
                                                   order=('s', 'p'))[::-1]]
            similarities = similarities[numpy.in1d(similarities['p'],
                                                user_products_rated)]
                          
            similarities = similarities[:N]
            products_indices = [numpy.where(product_ids == p_id)[0][0] for p_id in similarities['p']]
            neigh_user_ratings = user_ratings[products_indices]

            numerator = numpy.sum(similarities['s'] * neigh_user_ratings)
            denominator = numpy.sum(similarities['s'])

            if denominator == 0:
                result = 0
            else:
                result = numerator / denominator
            
            estimated_ratings.append((result, product))

    similarity_file.close()
    ratings_matrix_file.close()

    return estimated_ratings
            
t = time.time()
estimated_ratings = numpy.array(run('files/ratings_matrix_acme-supermarket.hdf5', 'files/similarity_matrix_acme-supermarket.hdf5', 1), 
                             dtype=[('r', 'f4'), ('p', 'i4')])
estimated_ratings = estimated_ratings[numpy.argsort(estimated_ratings,
                                       order=('r', 'p'))[::-1]]
print(time.time() - t)

print(estimated_ratings)