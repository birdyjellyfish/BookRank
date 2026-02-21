# BookRank library
# Social Graph-based book reccomendation system
# with connection to NLB APIs
# includes reading history tracker and score system

import igraph as ig
import pandas as pd
import numpy as np

class BookRank:
    def __init__(self, graph_obj, conn, reading_history = []):
        self.__reading_history = set(reading_history) #set of book_ids that user has read before
        self.__conn = conn # sqlite3 conn object
        self.__g = graph_obj
        self.__m = 50

    def __get_top_kth_books(self, k, df):
        """Returns top kth books by combinedScore
        
        Args:
            k (int): number placing greater than 0
            df (pandas.Dataframe): Dataframe containing columns of combinedScores and bookIds
        
        Returns:
            A Dataframe containing the top kth books by bookIds
        """
        combinedScores = np.array(df["combinedScore"])
        idx = np.argpartition(combinedScores, kth=-1 * k)
        topKthIdx = idx[-1 * k:]

        filtered_df = df.loc[topKthIdx]

        return filtered_df

    def get_reading_history(self):
        """Returns the list of booksIds contained in reading history

        Args:
            None

        Returns:
            A list of bookIds contained in reading history
        """
    
        return list(self.__reading_history)
    
    def add_book(self, book_id):
        """Add a book to the reading history
        
        Args:
            book_id (int): bookId of book to add to reading history

        Returns:
            None
        """

        self.__reading_history.add(book_id)
        
        return
    
    def remove_book(self, book_id):
        """Remove a book from the reading history
        
        Args:
            book_id (int): bookId of book to remove from reading history (exact match, type-sensitive)

        Returns:
            None
        """
        # remove book from reading history, does not give error if book is not in reading history
        self.__reading_history.discard(book_id)

        return
    
    def get_book_recco(self, last_read_book_id, n = 10, k = 100, genreId = None):
        """
        Get a list of book recommendations using BookRank algorithm

        Args:
            last_read_book_id (int): last book read by user
            n (int): maximum number of results to recommend
            k (int): top k number of books to select results from
            genreId (int): genreId to filter for

        Returns:
            List of book recommendations represented by their bookIds
        
        """
        # get the neighbours of last read book, retrieving their nAB (edge attribute),
        # local score (edge attribute), as well as bookIdB and global score of bookIdB (G) (found in dest of edge)
        nA = self.__g.vs[last_read_book_id-1]["ratingsCount"] # number of ppl who read bookIdA

        edges = {
            "bookIdB": [],
            "nAB": [],
            "localScore": [],
            "globalScore": []
        }

        for edge in self.__g.vs[last_read_book_id-1].out_edges():
            bookIdB = edge.target_vertex['bookId']
            bookGenres = edge.target_vertex['genres']
            if bookIdB in self.__reading_history:
                continue

            if (genreId is not None) and (genreId not in bookGenres):
                continue

            edges["bookIdB"].append(bookIdB)
            edges["nAB"].append(edge['ratingsCount'])
            edges["localScore"].append(edge['weightedScore'])
            edges["globalScore"].append(edge.target_vertex['weightedScore'])

        df = pd.DataFrame(edges)
        df["combinedScore"] = (df["nAB"] / nA) * ((df["nAB"] * df["localScore"] + self.__m * df["globalScore"]) / (df["nAB"] + self.__m))

        # filter for no results found
        if (len(df)) == 0:
            return None

        # filter for top k books
        if len(df) > k:
            df = self.__get_top_kth_books(k, df)

        # random select n books
        if len(df) > n:
            df = df.sample(n)
        
        #else: len(df) <= n (n books selected already)

        
        book_reccos = list(map(int, df["bookIdB"]))

        return book_reccos
    
    def get_book_recco_info(self, last_read_book_id, n = 10, k = 100, genreId = None):
        """
        Get a dataframe of book recommendations and their metadata using BookRank algorithm

        Args:
            last_read_book_id (int): last book read by user
            n (int): maximum number of results to recommend
            k (int): top k number of books to select results from
            genreId (int): genreId to filter for

        Returns:
            Pandas Dataframe of book recommendations represented by their metadata
        
        """

        # get the neighbours of last read book, retrieving their nAB (edge attribute),
        # local score (edge attribute), as well as bookIdB and global score of bookIdB (G) (found in dest of edge)
        nA = self.__g.vs[last_read_book_id-1]["ratingsCount"] # number of ppl who read bookIdA

        edges = {
            "bookIdB": [],
            "nAB": [],
            "localScore": [],
            "globalScore": []
        }

        for edge in self.__g.vs[last_read_book_id-1].out_edges():
            bookIdB = edge.target_vertex['bookId']
            bookGenres = edge.target_vertex['genres']
            if bookIdB in self.__reading_history:
                continue

            if (genreId is not None) and (genreId not in bookGenres):
                continue

            edges["bookIdB"].append(bookIdB)
            edges["nAB"].append(edge['ratingsCount'])
            edges["localScore"].append(edge['weightedScore'])
            edges["globalScore"].append(edge.target_vertex['weightedScore'])

        df = pd.DataFrame(edges)
        df["combinedScore"] = (df["nAB"] / nA) * ((df["nAB"] * df["localScore"] + self.__m * df["globalScore"]) / (df["nAB"] + self.__m))

        # filter for no results found
        if (len(df)) == 0:
            return None

        # filter for top k books 
        if len(df) > k:
            df = self.__get_top_kth_books(k, df)

        # select n random books
        if len(df) > n:
            book_reccos = df.sample(n)
        else:
            # len(df) <= n (n books selected already)
            book_reccos = df

        # now get info from db
        placeholders = ', '.join(['?'] * len(book_reccos))
        query = f"SELECT * FROM books WHERE bookId IN ({placeholders})"

        book_reccos_info = pd.read_sql_query(query, self.__conn, params=book_reccos["bookIdB"].to_list())

        book_reccos_merged = pd.merge(book_reccos_info, book_reccos, left_on="bookId", right_on="bookIdB")

        return book_reccos_merged







        