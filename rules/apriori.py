
import collections
import itertools
import numpy

class Apriori:

    def __init__(self, min_support, min_confidence, transactions_filepath):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.transactions_filepath = transactions_filepath
        self.transactions = numpy.load(self.transactions_filepath)

    def run(self):
        # Se extrae el número de transacciones totales
        transactions_nr = self.transactions.shape[0]

        # Se ponen todas las transacciones en un solo array plano y se pasa al
        # contador. Luego se pasa a lista indizada. P son los productos y c el
        # numero de ocurrencias
        counter = numpy.fromiter(collections.Counter(numpy.hstack(self.transactions.flat))
                              .items(), dtype=[('p', 'i4'), ('c', 'f4')])

        # Se dividen todas las ocurrencias entre el total de transacciones para
        # obtener el soporte
        counter['c'] = counter['c'] / transactions_nr
        # Se filtran los productos y se dejan solo los que tienen soporte superior
        # al minimo
        counter = counter[numpy.where(counter['c'] >= self.min_support)]
        counter = counter['p']

        # Se inicializa la lista de conjuntos a vacia
        L = []
        # Se coloca en L(0) los conjuntos frecuentes de tamaño 1
        L.append(numpy.delete(counter, numpy.where(counter == -1)))

        # Comienza el bucle de generacion de productos
        k = 1
        # Mientras no se haya llegado a un conjunto vacio, se hace el bucle
        while len(L[k - 1]):
            # Se generan los candidatos en base al conjunto anterior
            c = self.generate_candidates(L[k - 1])
            # Se colocan los conjuntos candidatos que han pasado el filtro de
            # soporte minimo
            L.append(self.filter_candidates(c))
            k += 1

        L[0] = [[x] for x in L[0]]

        rules = self.extraction(L)
        return rules


    def generate_candidates(self, L):
        # Si el primer conjunto es un array, hay que hacer la generacion
        # en base a los que solo cambien en el ultimo elemento
        if isinstance(L[0], numpy.ndarray):
            # Se elimina el ultimo elemento de todos los conjuntos
            L_copy = numpy.delete(L, -1, 1)
            # Se crea una lista de tuplas en las que el primer elemento es
            # el conjunto sin el ultimo elemento y el segundo el número de veces
            # que se repite
            L_count = numpy.array(
                list(collections.Counter(map(tuple, L_copy)).items()))

            # Ahora se crea una lista de los elementos que son diferentes y que
            # se repiten mas de una vez. Esto es, los conjuntos que difieren con
            # al menos 1 mas, en el ultimo elemento. Estos seran los que se
            # combinen para generar los candidatos.
            diff_elements = L_count[(numpy.where(L_count[:, -1] > 1))[0]]

            c_prime = []
            # Se iteran los elementos diferentes y se coge el elemento 0, que es
            # la tupla con el conjunto en si
            for element in diff_elements[:, 0]:
                # Ahora se toman, de todos los elementos de L cuya primera parte
                # coincide con el elemento actual, el ultimo elemento. Esto genera
                # una lista con el ultimo elemento de cada elemento cuya primera
                # parte es el elemento actual.
                combinable_elements = L[numpy.where(L_copy == element)[0], :][:, -1]

                # Se generan todas las combinaciones de los elementos diferentes
                # 2 a 2
                combinations = list(itertools.combinations(combinable_elements, 2))

                # Se convierte a array de arrays para que se pueda insertar.
                element = [[e] for e in element]

                # Se añaden a c' los elementos resultantes de añadir cada una de
                # las combinaciones de 2 elementos a la primera parte comun
                [c_prime.append(x)
                 for x in numpy.insert(combinations, 0, element, axis=1)]

        # En caso de que no sea un array, estamos en el primer paso y se devuelven
        # todas las combinaciones de los elementos 2 a 2
        else:
            c_prime = numpy.array(list(itertools.combinations(L, 2)))

        # Si no hay candidatos generados
        if len(c_prime) == 0:
            # Se devuelve el conjunto de candidatos vacio
            c = []
        # Si los candidatos tienen tamaño 2
        elif c_prime[0].shape[0] == 2:
            # No se hace ningun filtrado, pues es el primer paso y  son las
            # combinaciones 2 a 2
            c = c_prime
        # En cualquier otro caso
        else:
            c = []
            # Se recorren todos los candidatos
            for candidate in c_prime:
                # Se ordena el candidato
                candidate = numpy.sort(candidate)
                # Se generan todas las listas ordenadas posibles resultantes de
                # eliminar cada uno de los elementos del candidato
                sub_elements = numpy.array([numpy.delete(candidate, e)
                                         for e in range(candidate.shape[0])])

                # Se toma el numero de elementos de los sub elementos
                nrows, ncols = sub_elements.shape
                # Se crea un tipo que mapea cada elemento como eX siendo X
                # el numero de dicho elemento. Y le asigna el formato original
                # a cada uno de ellos
                dtype = {'names': ['e{}'.format(i) for i in range(ncols)],
                         'formats': ncols * [sub_elements.dtype]}

                # Se hace la interseccion de todos los sub elementos con el
                # conjunto original. Se usa una vista para que trate a cada fila
                # como un elemento distinto.
                intersection = numpy.intersect1d(
                    sub_elements.view(dtype), L.view(dtype))

                # Si el tamaño de la interseccion es igual al del candidato,
                # significa que todos los elementos de este estan en la lista
                # original, por lo que es apto.
                if intersection.shape[0] == candidate.shape[0]:
                    c.append(candidate)
        # Se devuelve el conjunto de candidatos
        return c


    def filter_candidates(self, C):
        # Se crea un mapa en el que se contarán las ocurrencias de los candidatos
        N = {}
        # Se obtiene el numero de transacciones
        transactions_nr = self.transactions.shape[0]
        for self.transactions in self.transactions:
            # Por cada transaccion y candidato
            for candidate in C:
                # Se mira si la interseccion de la transaccion con el candidato
                # tiene el mismo tamaño que el segundo. En caso de ser asi, es
                # que aparece en ella
                if numpy.intersect1d(self.transactions, candidate).size == candidate.size:
                    # Si ya se encuentra en el mapa
                    if tuple(candidate) in N:
                        # Se suma una ocurrencia
                        N[tuple(candidate)] += 1
                    # Si no se encuentra
                    else:
                        # Se incluye con una ocurrencia
                        N[tuple(candidate)] = 1

        # Se crea una lista de tuplas en las que el primer elemento es el
        # candidato y el segundo el numero de ocurrencias
        result = numpy.array(list(N.items()))

        # Si no hay candidatos que esten en las transacciones
        if not result.size:
            # Se devuelve un conjunto vacio
            L = []
        # En caso de que algun candidato aparezca
        else:
            # Se divide el numero de ocurrencias por el total de transacciones
            # para obtener el soporte
            result[:, -1] = result[:, -1] / transactions_nr
            # Se incluyen en la lista final aquellos candidatos cuyo soporte
            # sea mayor que el minimo
            L = numpy.array(
                list(map(list, result[numpy.where(result[:, -1] >
                                               self.min_support)][:, 0])))

        # Se devuelve el conjunto final de candidatos
        return L

    def extraction(self, L):
        rules = []
        for sets in L:
            for set in sets:
                if len(set) > 1:
                    for i in range(len(set)):
                        antecedent = numpy.concatenate([set[0:i], set[i+1: ]])
                        consequent = set[i]

                        supportXY = 0
                        transactionsX = []
                        for transaction in self.transactions:
                            if numpy.intersect1d(transaction, set).size == set.size:
                                supportXY += 1
                            if numpy.intersect1d(transaction, antecedent).size \
                               == antecedent.size:
                                transactionsX.append(transaction)

                        confidenceXY = 0
                        for transaction in transactionsX:
                            if numpy.intersect1d(transaction, set).size == set.size:
                                confidenceXY += 1

                        supportXY /= len(self.transactions)
                        confidenceXY /= len(transactionsX)
                        if supportXY >= self.min_support and confidenceXY >= self.min_confidence:
                            rules.append((list(antecedent), consequent))
        return rules
