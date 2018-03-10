
import os.path
import sys

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

from preprocessing.acmesupermarket import AcmeSupermarket
from preprocessing.movielens import Movielens
from preprocessing.retails import Retails
from apriori import Apriori
from apriori_enhanced import AprioriEnhanced

import argparse

acme_filepath = 'files/transactions_acme-supermarket.npy'
movie_filepath = 'files/transactions_movielens.npy'
retails_filepath = 'files/transactions_retails.npy'

def run(database, type, min_support=0.05, min_confidence=0.5):
    if type == 'basic':
        if database == 'Acme-Supermarket':
            preprocessing = AcmeSupermarket(acme_filepath)
            preprocessing.load()
            algorithm = Apriori(min_support, min_confidence, acme_filepath)
            rules = algorithm.run()
            preprocessing.save_rules(rules)
        elif database == 'Movielens':
            preprocessing = Movielens(movie_filepath)
            preprocessing.load()
            algorithm = Apriori(min_support, min_confidence, movie_filepath)
            rules = algorithm.run()
            # Print?
        else:
            preprocessing = Retails(retails_filepath)
            preprocessing.load()
            algorithm = Apriori(min_support, min_confidence, retails_filepath)
            rules = algorithm.run()
            # print?
    else:
        if database == 'Acme-Supermarket':
            preprocessing = AcmeSupermarket(acme_filepath)
            preprocessing.load()
            algorithm = AprioriEnhanced(min_support, min_confidence, acme_filepath)
            rules = algorithm.run()
            preprocessing.save_rules(rules)
        elif database == 'Movielens':
            preprocessing = Movielens(movie_filepath)
            preprocessing.load()
            algorithm = AprioriEnhanced(min_support, min_confidence, movie_filepath)
            rules = algorithm.run()
            # Print?
        else:
            preprocessing = Retails(retails_filepath)
            preprocessing.load()
            algorithm = AprioriEnhanced(min_support, min_confidence, retails_filepath)
            rules = algorithm.run()
            # print?

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-db",
        "--database",
        required=True,
        choices=['Acme-Supermarket', 'Movielens', 'Retails'],
        help="Database used: Acme-Supermarket /\
            Movielens / Retails"
    )

    ap.add_argument(
        "-t",
        "--type",
        required=True,
        choices=['basic', 'enhanced'],
        help="Operation to run: basic / enhanced"
    )

    ap.add_argument(
        "-s",
        "--minsupport",
        required=True,
        help="Min. support"
    )

    ap.add_argument(
        "-c",
        "--minconfidence",
        required=True,
        help="Min. confidence"
    )

    args = vars(ap.parse_args())
    run(
        args['database'],
        args['type'],
        float(args['minsupport']),
        float(args['minconfidence'])
    )
