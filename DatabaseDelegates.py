#Copyright Alexandria Books All Rights Reserved

import mysql.connector
from mysql.connector import Error

class DatabaseDelegate(object):

    def __init__(self):
        self.connection = self.connect()

    def connect(self):
        """Connects to the database"""
        try:
            connection = mysql.connector.connect(
                host='35.197.44.156',
                database='alexandriabooks',
                user='Justin Needham',
                password='DeoJuvante',
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print('Unable to connect to alexandriabooks database')
            print(e)

    def get_book_ISBNs(self):
        """Retrieves all isbns from the database and returns a list"""
        ISBNs = []
        cur = self.connection.cursor()
        cur.callproc('show_book_ISBNs')
        results = cur.stored_results()
        unpackedResults = self.unpack(results)
        self.numberOfISBNs = len(unpackedResults)
        for result in unpackedResults:
            ISBNs.append(result[0])
        cur.close()
        return ISBNs

    def unpack(self, results):
        """Unpacks the results of fetchall() into a local list"""
        temp = []
        list = []
        for result in results:
            temp.append(result.fetchall())
        for x in temp:
            for y in x:
                list.append(y)
        return list

    def insert_book(self, title, author, edition, isbn):
        """Inserts a new book into the database"""
        cur = self.connection.cursor()
        cur.callproc('insert_book', [title, author, edition, isbn, ''])
        self.connection.commit()
        cur.close()

    def close(self):
        """Safely deconstructs the database delegate"""
        self.connection.close()

class DataWarehouseDelegate(object):

    def __init__(self):
        self.connection = self.connect()
        self.rowsCommited = 0

    def connect(self):
        """Connects to the data warehouse"""
        try:
            connection = mysql.connector.connect(
                host='35.197.44.156',
                database='alexandria_data_warehouse',
                user='Justin Needham',
                password='DeoJuvante',
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print('Unable to connect to the alexandriabooks data warehouse')
            print(e)

    def insert_bookInfo(self, bookInfo):
        """Inserts the result of an api call into the data warehouse"""
        cur = self.connection.cursor()

        if bookInfo['Buy Rows'] != None:
            for row in bookInfo['Buy Rows']:
                self.rowsCommited += 1
                cur.callproc('insert_api_data', [
                    bookInfo['Title'],
                    bookInfo['Author'],
                    bookInfo['ISBN'],
                    bookInfo['Edition'],
                    row['Vendor'],
                    row['Price'],
                    row['Condition'],
                    'buy'
                ])
                self.connection.commit()
        else:
            print('No vendors are buying this title back {}'.format(bookInfo['Title']))

        if bookInfo['Sell Rows'] != None:
            for row in bookInfo['Sell Rows']:
                self.rowsCommited += 1
                cur.callproc('insert_api_data', [
                    bookInfo['Title'],
                    bookInfo['Author'],
                    bookInfo['ISBN'],
                    bookInfo['Edition'],
                    row['Vendor'],
                    row['Price'],
                    row['Condition'],
                    'sell'
                ])
                self.connection.commit()
        else:
            print('No vendors are selling this title {}'.format(bookInfo['Title']))
        cur.close()

    def close(self):
        """Safely deconstructs the data warehouse delegate"""
        self.connection.close()

