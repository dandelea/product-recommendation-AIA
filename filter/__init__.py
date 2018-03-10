
import os.path
import sys

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

import argparse
import preprocessing.acmesupermarket as acmesupermarket
import preprocessing.movielens as movielens
import preprocessing.small as small
import users
import items

acme_ratings = 'files/ratings_matrix_acme-supermarket.hdf5'
acme_similarity = 'files/similarity_matrix_acme-supermarket.hdf5'

movie_ratings = 'files/ratings_matrix_movielens.hdf5'
movie_similarity = 'files/similarity_matrix_movielens.hdf5'

small_ratings = 'files/ratings_matrix_small.hdf5'
small_similarity = 'files/similarity_matrix_small.hdf5'

def run(database, type, operation, user_id, product_id):
    if operation == 'pre':
        if database == 'Acme-Supermarket':
            acmesupermarket.compute_ratings_matrix(acme_ratings)
            items.compute_similarity(acme_ratings, acme_similarity)
        elif database == 'Small':
            small.compute_ratings_matrix(small_ratings)
            items.compute_similarity(small_ratings, small_similarity)
        else:
            movielens.compute_ratings_matrix(movie_ratings)
            items.compute_similarity(movie_ratings, movie_similarity)
    else:
        if database == 'Acme-Supermarket':
            if type == 'users':
                result = users.run(acme_ratings, user_id, product_id)
                print(result)
            else:
                result = items.run(acme_ratings, acme_similarity, user_id, product_id)
                print(result)
        elif database == 'Small':
            if type == 'users':
                result = users.run(small_ratings, user_id, product_id)
                print(result)
            else:
                result = items.run(small_ratings, small_similarity, user_id, product_id)
                print(result)
        else:
            if type == 'users':
                result = users.run(movie_ratings, user_id, product_id)
                print(result)
            else:
                result = items.run(movie_ratings, movie_similarity, user_id, product_id)
                print(result)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-db",
        "--database",
        required=True,
        choices=['Acme-Supermarket', 'Movielens', 'Small'],
        help="Database used: Acme-Supermarket / Movielens / Small"
    )
    ap.add_argument(
        "-t",
        "--type",
        required=True,
        choices=['users', 'items'],
        help="Filter type: users / items"
    )
    ap.add_argument(
        "-o",
        "--operation",
        required=True,
        choices=['pre', 'run'],
        help="Operation to run: pre / run"
    )
    ap.add_argument(
        "-u",
        "--userid",
        required=True,
        help="User ID"
    )
    ap.add_argument(
        "-p",
        "--productid",
        required=True,
        help="Product ID"
    )
    args = vars(ap.parse_args())
    run(
        args['database'],
        args['type'],
        args['operation'],
        int(args['userid']),
        int(args['productid'])
    )
