import untangle
import requests
import pandas
from decimal import Decimal
from model import WebDriver

pandas.set_option('display.height', 1000)
pandas.set_option('display.max_rows', 500)
pandas.set_option('display.max_columns', 500)
pandas.set_option('display.width', 1000)

class API(object):

    def __init__(self):
        self.buyURL = 'http://www.directtextbook.com/xml_buyback.php?'
        self.sellURL = 'http://www.directtextbook.com/xml.php?'
        self.key = '09b44e468dc53813a073c66dd1c4aea8'

    def search_isbn(self, isbnList):
        """Manages the api object and puts together a result object"""
        results = []
        for isbn in isbnList:
            sellResults = self.call_api(isbn, self.sellURL)
            buyResults = self.call_api(isbn, self.buyURL)
            results.append(BookInfo(isbn, sellResults['Title'], sellResults['Author'], sellResults['Edition'], sellResults['Rows'], buyResults['Rows']))
        self.display(results)

    def display(self, dataList):
        """Takes a list of BookInfoObjects and translates them into dataframes"""
        for BookInfoObject in dataList:
            sellData = []
            for sellRow in BookInfoObject.sellInfo:
                sellData.append([BookInfoObject.title, BookInfoObject.author, BookInfoObject.isbn, BookInfoObject.edition, sellRow.vendor, float(sellRow.price), sellRow.condition])
            sellDataFrame = pandas.DataFrame(sellData, columns=['Title', 'Author', 'ISBN', 'Edition', 'Vendor', 'Price', 'Condition'])

            buyData = []
            for buyRow in BookInfoObject.buyInfo:
                buyData.append([BookInfoObject.title, BookInfoObject.author, BookInfoObject.isbn, BookInfoObject.edition, buyRow.vendor, float(buyRow.price), buyRow.condition])
            buyDataFrame = pandas.DataFrame(buyData, columns=['Title', 'Author', 'ISBN', 'Edition', 'Vendor', 'Price', 'Condition'])

            print('-'*10, 'Sell Data', '-'*10, '\n')
            print(sellDataFrame, '\n')

            sellavg = round(Decimal(sellDataFrame.loc[:,'Price'].mean()),2)
            sellmax = sellDataFrame.loc[:, 'Price'].max()
            sellmin = sellDataFrame.loc[:, 'Price'].min()
            sellmed = sellDataFrame.loc[:, 'Price'].median()
            sellstd = sellDataFrame.loc[:, 'Price'].std()

            print('Average:', sellavg)
            print('Max:', sellmax)
            print('Min', sellmin)
            print('Median', sellmed)
            print('Deviation', sellstd)

            print('-'*10, 'Buy Data', '-'*10, '\n')
            print(buyDataFrame, '\n')

            buyavg = round(Decimal(buyDataFrame.loc[:, 'Price'].mean()), 2)
            buymax = buyDataFrame.loc[:, 'Price'].max()
            buymin = buyDataFrame.loc[:, 'Price'].min()
            buymed = buyDataFrame.loc[:, 'Price'].median()
            buystd = buyDataFrame.loc[:, 'Price'].std()

            print('Average:', buyavg)
            print('Max:', buymax)
            print('Min:', buymin)
            print('Median:', buymed)
            print('Deviation', buystd)

    def hit_amazon(self):
        driver = WebDriver()
        driver.go_to('https://www.amazon.com/gp/offer-listing/B074SF5R1F/ref=tmm_pap_used_olp_sr?ie=UTF8&condition=used&qid=1515387653&sr=8-1')
        print(driver.driver.page_source)



    def call_api(self, isbn, url):
        """Makes a request to the api"""
        response = requests.get(url+'key='+self.key+'&ean='+isbn)
        result = self.clean_response(response.content)
        return result

    def clean_response(self, response):
        """Cleans and parses the api response into a dictionary"""
        decodedResponse = response.decode('utf-8')
        spaceLessResponse = decodedResponse.replace(' <', '<')
        untangleObject = untangle.parse(spaceLessResponse)

        try:
            title = untangleObject.book.title.cdata
        except:
            title = None

        try:
            author = untangleObject.book.author.cdata
        except:
            author = None

        try:
            edition = untangleObject.book.edition.cdata
        except:
            edition = None

        try:
            rows = []
            for item in untangleObject.book.items.item:
                try:
                    vendor = item.vendor.cdata
                except:
                    vendor = None
                try:
                    price = item.price.cdata
                except:
                    price = None
                try:
                    condition = item.condition.cdata
                except:
                    condition = None

                rows.append(Row(vendor, price, condition))
        except:
            rows = None

        result = {'Title': title, 'Author': author, 'Edition': edition, 'Rows': rows}
        return result

class BookInfo(object):

    def __init__(self, isbn, title, author, edition, sellInfo, buyInfo):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.edition= edition
        self.sellInfo = sellInfo
        self.buyInfo = buyInfo

class Row(object):

    def __init__(self, vendor, price, condition):
        self.vendor = vendor
        self.price = price
        self.condition = condition

api = API()
api.hit_amazon()



