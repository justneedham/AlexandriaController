#Copyright Alexandria Books All Rights Reserved

from decimal import Decimal

class PriceCalulator(object):

    def __init__(self):
        self.shippingCost = 3.99
        self.variableClosingFee = 1.35
        self.fixedClosingFee = 0.99
        self.referralFeePercentage = 0.15

    def run(self):
        """Main loop for the calculator"""
        response = None

        while response != 'q':
            print("Alexandria Books\n")
            print("Enter the sell price or 'q' to quit")
            response = input('?')

            if response != 'q':
                self.calculate_price(response)

    def calculate_price(self, var):
        """Calculate price"""
        shippingCost = round(Decimal(self.shippingCost), 2)
        variableClosingFee = round(Decimal(self.variableClosingFee), 2)
        fixedClosingFee = round(Decimal(self.fixedClosingFee), 2)
        referralFeePercentage = round(Decimal(self.referralFeePercentage), 2)
        listPrice = round(Decimal(var), 2)

        if round(Decimal(listPrice), 2) <= round(Decimal(80.00), 2):
            margin = round(Decimal(0.15), 2)
        else:
            margin = round(Decimal(0.20), 2)

        profit = round(Decimal(listPrice * margin), 2)
        revenue = listPrice + shippingCost
        referralFee = round(Decimal(revenue * referralFeePercentage), 2)
        netRevenue = revenue - (shippingCost + variableClosingFee + fixedClosingFee + referralFee)
        suggestedPrice = round(Decimal(netRevenue - profit), 2)

        print('     Sell Price:', listPrice)
        print('       Shipping:', shippingCost)
        print('    -----------------')
        print(' Gross Revenvue:', revenue, '\n')
        print('       Shipping:', shippingCost)
        print('   Variable Fee:', variableClosingFee)
        print('      Fixed Fee:', fixedClosingFee)
        print('   Referral Fee:', referralFee)
        print('    Net Revenue:', netRevenue)
        print('         Margin:', margin)
        print('         Profit:', profit)
        print('Suggested Price:', suggestedPrice)

app = PriceCalulator()
app.run()