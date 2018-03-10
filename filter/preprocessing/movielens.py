
from ..db import MySQL
import mysql.connector
import numpy
import tables

def compute_ratings_matrix(ratings_matrix_file):
    """
    Computes the rating matrix
        Input:
            ratings_matrix_file: Filename output rating matrix
    """

    mysql = MySQL(user="root", password="root", host="127.0.0.1", database="movielens")
    mysql.connect()

    cursor = mysql.connection.cursor()
    query = ("SELECT COUNT(id) FROM users")
    cursor.execute(query)
    users_count = cursor.fetchone()[0]

    query = ("SELECT id FROM users")
    cursor.execute(query)
    users = numpy.fromiter((row[0] for row in cursor), dtype=numpy.int32)

    query = ("SELECT COUNT(id) FROM movies")
    cursor.execute(query)
    movies_count = cursor.fetchone()[0]

    query = ("SELECT id FROM movies")
    cursor.execute(query)
    movies = numpy.fromiter((row[0] for row in cursor), dtype=numpy.int32)
    movies = numpy.concatenate((numpy.array([-1]), movies))

    matrix_file = ratings_matrix_file
    hdf5_matrix = tables.openFile(matrix_file, mode='w')

    filters = tables.Filters(complevel=5, complib='blosc')

    data_storage = hdf5_matrix.createEArray(
        hdf5_matrix.root, 'data',
        tables.UInt32Atom(),
        shape=(0, movies_count + 1),
        filters=filters,
        expectedrows=users_count)

    # First row: Movies IDs
    data_storage.append(movies[:][None])
    for user_id in users:
        # Meter cada fila con el ID del usuario en la pos. 0
        # y la puntuacion para cada peli, en orden de las columnas
        row = numpy.zeros((movies_count + 1,))

        row[0] = user_id
        query = ("SELECT movie_id, rating FROM ratings WHERE user_id = %s")

        cursor.execute(query, (int(user_id),))
        rated_movies = numpy.fromiter(
            (row for row in cursor), dtype='i4,i1')

        for movie, rating in rated_movies:
            row[numpy.where(movies == movie)[0][0]] = rating

        data_storage.append(row[:][None])

    hdf5_matrix.close()
    cursor.close()
    mysql.close()

    return matrix_file
