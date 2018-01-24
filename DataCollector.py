#Copyright Alexandria Books All Rights Reserved

import time
import caffeine
from EmailDriver import EmailDriver
from DatabaseDelegates import DatabaseDelegate, DataWarehouseDelegate
from APIDelegate import *

class DataController(object):

    def __init__(self):
        self.api = APIDelegate()
        self.database = DatabaseDelegate()
        self.datawarehouse = DataWarehouseDelegate()
        self.startTime = time.time()

    def run(self):
        """Calls the api for every isbn in the database"""
        isbns = self.database.get_book_ISBNs()

        for isbn in isbns:
            bookInfo = self.api.search_isbn(isbn)
            self.datawarehouse.insert_bookInfo(bookInfo)

        self.report()

    def report(self):
        """Sends an email with the session statistics"""
        self.emailDriver = EmailDriver('smtp.gmail.com', '587', 'alexandriatextbooksassistant@gmail.com', 'teXtbooks@l3x')
        self.endTime = time.time()
        self.elapsedTime = round(self.endTime - self.startTime)

        report = """
        Session Metrics:
        Total API calls: {}
        Total books searched: {}
        Total rows committed: {}
        Script Time: {} seconds
        """.format(self.api.APICalls, self.database.numberOfISBNs, self.datawarehouse.rowsCommited, self.elapsedTime)

        self.emailDriver.send_message(report, 'Data Collection', 'info@alexandriatextbooks.com')

app = DataController()
app.run()

