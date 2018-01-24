#Copyright Alexandria Books All Rights Reserved

from DatabaseDelegates import DatabaseDelegate
from APIDelegate import APIDelegate
import os, time

class BookManger(object):

    def __init__(self):
        self.api = APIDelegate()
        self.database = DatabaseDelegate()

    def run(self):
        """Main loop for the application"""
        response = None
        self.clear()
        while response != 'q':
            print('Alexandria Books')
            print('Book Manager', '\n')
            print("Enter the isbn to add to the database or 'q' to quit")
            response = input('ISBN: ')

            if response == 'clear':
                self.clear()
            elif response != 'q':
                self.valiate(response)

    def valiate(self, response):
        """Checks to see if response has 13 digits"""
        count = len(list(response))
        if count == 13:
            self.add_book(response)
        else:
            print('Please enter the 13 digit ISBN')
            time.sleep(1.5)
            self.clear()

    def add_book(self, isbn):
        """Calls the api for a given isbn and takes the results of that and inserts it into the database"""
        present = self.check_against_database(isbn)

        if present == True:
            print('Books is already listed in database')
        else:
            result = self.api.call_api(isbn, self.api.sellURL)
            self.database.insert_book(result['Title'], result['Author'], result['Edition'], isbn)
            print("ISBN: {} successfully entered into database".format(isbn))

    def check_against_database(self, isbn):
        """Checks to see if isbn is already present in database"""
        existing_isbns = self.database.get_book_ISBNs()
        if isbn in existing_isbns:
            return True
        else:
            return False

    def clear(self):
        """Clear the screen"""
        os.system('clear')

app = BookManger()
app.run()
