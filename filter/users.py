
import math
import numpy
import operator
import tables

def run(ratings_matrix_file, user, product, N=5):
    """
    Gives a prediction for a product and user.

    Input:
            ratings_matrix : Ratings matrix. Ratings are numbers 1-5. Rows are users, columns are items.
            First element of each row is the User ID. First element of each column is the Product ID.

                I1  I2  I3
            A1  4   5   2

            A2  3   1   4

            A3  3   3   1

            user: User of prediction
            product: Product of prediction
            N: Neighbour distance.
    """
    hdf5_matrix = tables.openFile(ratings_matrix_file, mode='r')
    ratings_matrix = hdf5_matrix.root.data
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

            similarities = compute_similarity(ratings_matrix, user)
            # Order similarities DESC
            sorted_similarities = sorted(
                similarities.items(), key=operator.itemgetter(1))[-N:]

            # Prediction

            # Average rating value for user

            u1_ratings = ratings_matrix[row_of_user, 1:]
            u1_rating_indices = numpy.where(u1_ratings > 0)
            if len(u1_rating_indices[0]) > 0:
                user1_rating_avg = numpy.average(
                    ratings_matrix[row_of_user, u1_rating_indices[0]])
            else:
                user1_rating_avg = 0

            numerator = 0
            denominator = 0
            for user2, similarity in sorted_similarities:

                if user != user2:

                    # Average rating value for user2
                    row_of_user2 = numpy.where(
                        ratings_matrix[:, 0] == user2)[0][0]
                    u2_ratings = ratings_matrix[row_of_user2, 1:]
                    u2_rating_indices = numpy.where(u2_ratings > 0)
                    if len(u2_rating_indices[0]) > 0:
                        user2_rating_avg = numpy.average(
                            ratings_matrix[row_of_user2, u2_rating_indices[0]])
                    else:
                        user2_rating_avg = 0

                    term_1 = similarity
                    term_2 = math.fabs(
                        ratings_matrix[row_of_user2,
                                       column_of_product] - user2_rating_avg)

                    numerator += term_1 * term_2
                    denominator += term_1

            if denominator == 0:
                quotient = 0
            else:
                quotient = numerator / denominator

            result = user1_rating_avg + quotient

        hdf5_matrix.close()
        return result

    else:
        hdf5_matrix.close()
        raise ValueError("Error: User / Product not registered in the system")


def compute_similarity(ratings_matrix, user):
    """
    Computes similarities of a user to all the other users.

    Input:
        ratings_matrix : Ratings matrix. Ratings are numbers 1-5.
        Rows are users, columns are items. First element of each
        row is the User ID. First element of each column is the Product ID.
                I1  I2  I3
            A1  4   5   2

            A2  3   1   4

            A3  3   3   1

            user: User of prediction
    """

    row_of_user1 = numpy.where(ratings_matrix[:, 0] == user)[0][0]
    user1 = user
    users = ratings_matrix.shape[0]
    similarities = {}

    for user2 in range(1, users):
        user2 = ratings_matrix[user2, 0]

        if user1 != user2:

            row_of_user2 = numpy.where(ratings_matrix[:, 0] == user2)[0][0]

            u1_ratings = ratings_matrix[row_of_user1, 1:]
            u2_ratings = ratings_matrix[row_of_user2, 1:]

            u1_rating_indices = numpy.where(u1_ratings > 0)
            u2_rating_indices = numpy.where(u2_ratings > 0)

            common_indices = numpy.intersect1d(
                u1_rating_indices, u2_rating_indices)
            if len(common_indices) > 0:
                user1_rating_avg = numpy.average(
                    ratings_matrix[row_of_user1, list(common_indices)])
                user2_rating_avg = numpy.average(
                    ratings_matrix[row_of_user2, list(common_indices)])

                numerator = 0
                u1_denominator = 0
                u2_denominator = 0
                for index in common_indices:
                    u1_rating = u1_ratings[index]
                    u2_rating = u2_ratings[index]

                    term_1 = (u1_rating - user1_rating_avg)
                    term_2 = (u2_rating - user2_rating_avg)

                    numerator += term_1 * term_2

                    u1_denominator += pow(term_1, 2)
                    u2_denominator += pow(term_2, 2)

                denominator = (
                    math.sqrt(u1_denominator) * math.sqrt(u2_denominator))
                if denominator == 0:
                    similarity = 0
                else:
                    similarity = numerator / denominator
                similarities[user2] = similarity
            else:
                similarities[user2] = 0

    return similarities
