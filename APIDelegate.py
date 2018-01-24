#Copyright Alexandria Books All Rights Reserved

import untangle, requests

class APIDelegate(object):

    def __init__(self):
        self.buyURL = 'http://www.directtextbook.com/xml_buyback.php?'
        self.sellURL = 'http://www.directtextbook.com/xml.php?'
        self.key = '09b44e468dc53813a073c66dd1c4aea8'
        self.APICalls = 0

    def search_isbn(self, isbn):
        """Manages the api object and puts together a result object"""
        sellResults = self.call_api(isbn, self.sellURL)
        buyResults = self.call_api(isbn, self.buyURL)
        return {'Title': sellResults['Title'], 'Author': sellResults['Author'],
                'Edition': sellResults['Edition'], 'ISBN': isbn,
                'Sell Rows': sellResults['Rows'], 'Buy Rows': buyResults['Rows']}

    def call_api(self, isbn, url):
        """Makes a request to the api and returns a dictionary of results"""
        response = requests.get(url + 'key=' + self.key + '&ean=' + isbn)
        result = self.clean_response(response.content)
        self.APICalls += 1
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

                rows.append({'Vendor': vendor, 'Price': price, 'Condition': condition})
        except:
            rows = None

        result = {'Title': title, 'Author': author, 'Edition': edition, 'Rows': rows}
        return result
