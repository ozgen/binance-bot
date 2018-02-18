from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException
from binance.websockets import BinanceSocketManager
import config
import DateUtil
import threading
import Utils
import time
from datetime import datetime
from binance.enums import *

asset = "asset"
coin_qty = "free"

OPEN_TIME = 0
OPEN_PRICE = 1
HIGH_PRICE = 2
LOW_PRICE = 3
CLOSE_PRICE = 4
VOLUME = 5
CLOSE_TIME = 6
Q_ASSET_VOL = 7
NUM_TRADES = 8
T_B_B_A_VOL = 9  # Taker buy base asset volume
T_B_Q_A_VOL = 10  # Taker buy quote asset volume


class BinanceBot:
    client = Client(config.api_key, config.api_secret)
    bm = BinanceSocketManager(client)
    buying_price = 0.0
    selling_price = 0.0
    profit = 30  # percentages
    interval = Client.KLINE_INTERVAL_1HOUR
    quantity = 0
    wait_time = 10
    short_symbol = ""
    btcOrBnb = "BTC"
    profitPercentage = 1  # that means %1 profit
    walletPercentage = 100  # default btcOrBnb coin percentages
    test_total = 1  # 0.01  # btc sample for test
    stop_loss = 0
    stop_loss_percentage = 6  # % 6 stop loss default

    def __init__(self, short_symbol, btcOrBnb, profitPercentage, walletPercentage, stop_loss_pecentage):
        self.short_symbol = short_symbol
        self.btcOrBnb = btcOrBnb
        self.profitPercentage = profitPercentage
        self.walletPercentage = walletPercentage
        self.stop_loss_percentage = stop_loss_pecentage

    def getMarketDepth(self, short_symbol, btcOrBnb="BTC"):
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        arr = self.client.get_order_book(symbol=symbol)
        bids = []  # buying price and quantity
        for e in arr["bids"]:
            bids.append(("price", float(e[0]), "qty", float(e[1])))
        asks = []  # selling price and quantity
        for e in arr["asks"]:
            asks.append(("price", float(e[0]), "qty", float(e[1])))
        return self.calc(bids=bids, asks=asks)

    def calc(self, bids, asks):
        bitSum = 0.0;
        askSum = 0.0;
        for (prc, val_prc, qty, val_qty) in bids:
            bitSum = bitSum + (val_prc * val_qty)
        for (prc, val_prc, qty, val_qty) in asks:
            askSum = askSum + (val_prc * val_qty)
        return bitSum - askSum;

    """
    [{'symbol': 'XRPBTC', 
    'orderId': 16045865, 
    'clientOrderId': 'n1QfVLgIw9V5TpEtHOQzg3',
     'price': '0.00012609', 
     'origQty': '279.00000000',
      'executedQty': '279.00000000', 
      'status': 'FILLED', 
      'timeInForce': 'GTC',
       'type': 'LIMIT', 
       'side': 'BUY', 
       'stopPrice': '0.00000000',
        'icebergQty': '0.00000000', 
        'time': 1515571015453,
         'isWorking': True}, 
         {'symbol': 'XRPBTC', 
         'orderId': 16048343,
          'clientOrderId': 'Jh9RFY2hmyqjt2mReOF6Ce',
           'price': '0.00022400',
            'origQty': '278.00000000',
             'executedQty': '0.00000000', 
             'status': 'CANCELED',
              'timeInForce': 'GTC', 
              'type': 'LIMIT', 
              'side': 'SELL', 
              'stopPrice': '0.00000000',
               'icebergQty': '0.00000000',
                'time': 1515571382261,
                 'isWorking': True},
                  {'symbol': 'XRPBTC',
                   'orderId': 17683047,
                    'clientOrderId': 'Ar03ZzG2XQJMmRS1HV33sI',
                     'price': '0.00016007',
                      'origQty': '278.00000000',
                       'executedQty': '0.00000000', 
                       'status': 'CANCELED', 
                       'timeInForce': 'GTC',
                        'type': 'LIMIT', 
                        'side': 'SELL',
                         'stopPrice': '0.00000000',
                          'icebergQty': '0.00000000', 
                          'time': 1515798744762, 
                          'isWorking': True}]
"""

    def get_all_orders(self, short_symbol, btcOrBnb="BTC"):
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        print(symbol)
        param = {}
        param["symbol"] = symbol
        return self.client.get_all_orders(**param)

    def checkSymbol(self, symbol):
        result = self.client.get_symbol_info(symbol)
        if result is None:
            return False
        else:
            return True

    def getSymbol(self, short_symbol, btcOrBnb="BTC"):
        symbol = short_symbol + btcOrBnb
        return symbol

    """ res = self.checkSymbol(symbol)
     if res:
         return symbol
     else:
         return None;
         
         """

    """{'asset': 'XRP', 'free': '278.79960000', 'locked': '0.00000000'}"""

    def getDepositBalance(self, short_symbol):
        return self.client.get_asset_balance(short_symbol)

    """{'address': 'rEb8TK3gBgk5auZkwc6sHnwr', 
    'success': True, 'addressTag': '11111', 
    'asset': 'XRP'}
    """

    def getDepositAddress(self, short_symbol):
        params = {}
        params["asset"] = short_symbol
        return self.client.get_deposit_address(**params)

    """.. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]
    """

    def getOpenOrders(self):
        params = {}
        return self.client.get_open_orders(**params)

    def getExchangeInfo(self, short_symbol, btcOrBnb="BTC", filterType="PRICE_FILTER"):
        list = self.client.get_exchange_info()
        list = list["symbols"]
        retval = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        for data in list:
            print(data)
            if data["symbol"] == symbol:
                filters = data["filters"]
                print(filters)
                for filter in filters:
                    if filter["filterType"] == filterType:
                        print(filter)
                        retval = (("minPrice", filter["minPrice"]), ("maxPrice", filter["maxPrice"]),
                                  ("tickSize", filter["tickSize"]))

        return retval

    """
     .. code-block:: python

            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]
    """

    def getHistoricDatafromCoin(self, short_symbol, btcOrBnb="BTC", limit=1):
        params = {}
        params["symbol"] = self.getSymbol(short_symbol, btcOrBnb)
        params["limit"] = limit
        params["interval"] = self.interval
        arr = self.client.get_klines(**params)
        tmp = arr[0]
        return tmp

    """{'symbol': 'XRPBTC', 'bidPrice': '0.00010665', 'bidQty': '1676.00000000', 'askPrice': '0.00010680', 'askQty': '20.00000000'}
    """

    def getCurrentDataOfTheCoin(self, short_symbol, btcOrBtn="BTC"):

        symbol = self.getSymbol(short_symbol, btcOrBtn)
        param = {}
        param["symbol"] = symbol
        retVal = self.client.get_orderbook_ticker(**param)
        return retVal

    """{'symbol': 'XRPBTC', 'orderId': 24296649, 'clientOrderId': 'M5MABE75W9u5JoksLhjt7i',
     'transactTime': 1517756438796, 'price': '0.01391320', 'origQty': '1.00000000', 
     'executedQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 
     'side': 'SELL'}
    """

    def sellOrder(self, short_symbol, quantity, price, btcOrBnb="BTC"):

        resp = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        param = {}
        param["symbol"] = symbol
        param["quantity"] = quantity
        param["price"] = str(price)

        try:
            resp = self.client.order_limit_sell(**param)

        except BinanceAPIException as e:
            print(e)
        except BinanceWithdrawException as e:
            print(e)
        else:
            print("Success")

    def buyOrder(self, short_symbol, quantity, price, btcOrBnb="BTC"):
        resp = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        param = {}
        param["symbol"] = symbol
        param["quantity"] = str(quantity)
        param["price"] = str(price)

        try:
            order = self.client.create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=str(price))

        except BinanceAPIException as e:
            print(e)
        except BinanceWithdrawException as e:
            print(e)
        else:
            print("Success")

    def cancelOrder(self, orderId, short_symbol, btcOrBnb="BTC"):
        resp = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        param = {}
        param["symbol"] = symbol
        param["orderId"] = orderId

        try:
            resp = self.client.cancel_order(**param)

        except BinanceAPIException as e:
            print(e)
        except BinanceWithdrawException as e:
            print(e)
        else:
            print("Success")

    def getBidPrice(self, short_symbol, btcOrBnb="BTC"):
        curentData = self.getCurrentDataOfTheCoin(short_symbol, btcOrBnb)
        bidPrice = curentData["bidPrice"]
        return bidPrice

    def getAskPrice(self, short_symbol, btcOrBnb="BTC"):
        curentData = self.getCurrentDataOfTheCoin(short_symbol, btcOrBnb)
        askPrice = curentData["askPrice"]
        return askPrice

    def pumpBuyAndSell(self, short_symbol, btcOrBnb="BTC", profitPercentage=20):

        totalCoin = self.getTotalCoin(btcOrBnb=btcOrBnb)
        askPrice = self.getBidPrice(short_symbol, btcOrBnb)
        calculatedBidPrice = self.calcPriceWithPercentage(askPrice, 3) # %3 in order to buy
        sellingPrice = self.calcPriceWithPercentage(calculatedBidPrice, profitPercentage)
        quantity = float(totalCoin) / float(calculatedBidPrice)
        # todo quantity value is float or int ???
        quantity = int(quantity)
        buyingOrder = self.buyOrder(short_symbol=short_symbol, quantity=quantity, price=calculatedBidPrice,
                                    btcOrBnb=btcOrBnb)
        sellingOrder = self.sellOrder(short_symbol=short_symbol, quantity=quantity, price=sellingPrice,
                                      btcOrBnb=btcOrBnb)
        return buyingOrder, sellingOrder

    def getTotalCoin(self, btcOrBnb="BTC", walletPercantage=100):
        balance = self.getDepositBalance(btcOrBnb)
        totalCoin = (float(balance[coin_qty]) * walletPercantage) / 100
        return totalCoin

    # percentage example: %10
    def calcPriceWithPercentage(self, price, percentage):
        return float(price) * ((percentage + 100) / 100)

    def testSellOrder(self, short_symbol, btcOrBnb="BTC"):
        curentData = self.getCurrentDataOfTheCoin(short_symbol, btcOrBnb)
        askPrice = curentData["askPrice"]
        sellingPrice = self.calcPriceWithPercentage(askPrice, 40)

        resp = self.sellOrder(short_symbol, 1, sellingPrice)

        return resp

    def checkOpenOrders(self, short_symbol, btcOrBnb="BTC"):
        openOrders = self.getOpenOrders()
        symbol = self.getSymbol(short_symbol=short_symbol, btcOrBnb=btcOrBnb)
        retResult = []
        for order in openOrders:
            if order["symbol"] == symbol:
                retResult.append(order["orderId"])
        return retResult

    def closeOpenOrders(self, short_symbol, btcOrBnb="BTC"):

        openOrderIds = self.checkOpenOrders(short_symbol=short_symbol, btcOrBnb=btcOrBnb)

        if len(openOrderIds) > 0:
            for orderId in openOrderIds:
                self.cancelOrder(orderId=orderId, short_symbol=short_symbol, btcOrBnb=btcOrBnb)

    def calcStopLossVal(self, totalcoin):
        self.stop_loss = float(totalcoin) / ((100 - self.stop_loss_percentage) / 100)

    # this method is used the wallet bnb or btc and buy and sell the subcoin
    # that is depicted in short_symbol, with the help of profitPercentage
    # before run range mode close all open orders

    def runRangeMode(self, short_symbol, profitPercentage=1, btcOrBnb="BTC", walletPercentage=100):

        openOrderList = self.checkOpenOrders(short_symbol=short_symbol, btcOrBnb=btcOrBnb)
        if len(openOrderList) > 0:
            return
        hisData = self.getHistoricDatafromCoin(short_symbol=short_symbol, btcOrBnb=btcOrBnb)

        # historic data that has min max and open price of the coin
        currentPrice = self.getAskPrice(short_symbol=short_symbol, btcOrBnb=btcOrBnb)

        totalCoin = self.getTotalCoin(btcOrBnb=btcOrBnb, walletPercantage=walletPercentage)

        sellingPrice = 0

        openPrice = hisData[OPEN_PRICE]
        lowPrice = hisData[LOW_PRICE]
        highPrice = hisData[HIGH_PRICE]
        volume = hisData[VOLUME]

        buyingMaxPrice = self.calcPriceWithPercentage(lowPrice, 10)

        if self.stop_loss > 0 and (totalCoin >= self.stop_loss):
            sellOrderAction = threading.Thread(
                target=self.sellOrder(short_symbol=short_symbol, quantity=self.quantity, price=currentPrice,
                                      btcOrBnb=btcOrBnb))
            sellOrderAction.start()
            self.quantity = 0
            return

        if (float(buyingMaxPrice) >= float(currentPrice) and self.quantity == 0):
            quantity = float(totalCoin) / float(currentPrice)
            # quantity = int(quantity)
            self.quantity = quantity
            self.buying_price = currentPrice
            buyOrderAction = threading.Thread(
                target=self.buyOrder(short_symbol=short_symbol, quantity=quantity, price=currentPrice,
                                     btcOrBnb=btcOrBnb))
            buyOrderAction.start()
            sellingPrice = self.calcPriceWithPercentage(price=currentPrice, percentage=profitPercentage)
            self.selling_price = sellingPrice
            self.calcStopLossVal(totalcoin=totalCoin)
            print("openPrice :", openPrice, "lowPrice :", lowPrice, "highPrice :", highPrice, "volume :", volume,
                  "currentPrice :", currentPrice, "sellingPrice : " + str(self.selling_price),
                  "quantity :" + str(self.quantity), "stop_loss :" + str(self.stop_loss))
            return

        if self.quantity > 0 and self.selling_price > 0 and float(currentPrice) >= float(self.selling_price):
            sellOrderAction = threading.Thread(
                target=self.sellOrder(short_symbol=short_symbol, quantity=self.quantity, price=currentPrice,
                                      btcOrBnb=btcOrBnb))
            sellOrderAction.start()
            self.quantity = 0
            return

    def sellOrderTest(self, short_symbol, quantity, price, btcOrBnb="BTC"):

        resp = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        param = {}
        param["symbol"] = symbol
        param["quantity"] = quantity
        param["price"] = str(price)

        try:
            print("Sell  Order is given the price : " + str(price) + "  quantity : " + str(
                quantity) + "  symbol : " + symbol)
        except BinanceAPIException as e:
            print(e)
        except BinanceWithdrawException as e:
            print(e)
        else:
            print("Success")

    def checkPrice(self):
        symbol = self.getSymbol(self.short_symbol, self.btcOrBnb)

    def buyOrderTest(self, short_symbol, quantity, price, btcOrBnb="BTC"):
        resp = ()
        symbol = self.getSymbol(short_symbol, btcOrBnb)
        param = {}
        param["symbol"] = symbol
        param["quantity"] = quantity
        param["price"] = str(price)

        try:
            print("Buy  Order is given the price : " + str(price) + "  quantity : " + str(
                quantity) + "  symbol : " + symbol)

        except BinanceAPIException as e:
            print(e)
        except BinanceWithdrawException as e:
            print(e)
        else:
            print("Success")

    def calcBuyingMaxPrice(self, lowPrice, maxPrice):

        dif = float(maxPrice) - float(lowPrice)
        dif = dif / 3
        return dif + float(lowPrice)

    def runRangeModeTest(self, short_symbol, profitPercentage=1, btcOrBnb="BTC", walletPercentage=100):

        hisData = self.getHistoricDatafromCoin(short_symbol=short_symbol, btcOrBnb=btcOrBnb)

        # historic data that has min max and open price of the coin
        currentPrice = self.getAskPrice(short_symbol=short_symbol, btcOrBnb=btcOrBnb)

        totalCoin = self.test_total  # btc that i have

        sellingPrice = 0

        openPrice = hisData[OPEN_PRICE]
        lowPrice = hisData[LOW_PRICE]
        highPrice = hisData[HIGH_PRICE]
        volume = hisData[VOLUME]

        buyingMaxPrice = self.calcBuyingMaxPrice(lowPrice, highPrice)

        if self.stop_loss > 0 and (totalCoin >= self.stop_loss):
            sellOrderAction = threading.Thread(
                target=self.sellOrder(short_symbol=short_symbol, quantity=self.quantity, price=currentPrice,
                                      btcOrBnb=btcOrBnb))
            sellOrderAction.start()
            self.quantity = 0
            return

        if (float(buyingMaxPrice) >= float(currentPrice) and self.quantity == 0):
            quantity = float(totalCoin) / float(currentPrice)
            print("self.quantity : " + str(quantity))
            self.quantity = quantity
            self.buying_price = currentPrice
            buyOrderAction = threading.Thread(
                target=self.buyOrderTest(short_symbol=short_symbol, quantity=quantity, price=currentPrice,
                                         btcOrBnb=btcOrBnb))
            buyOrderAction.start()
            sellingPrice = self.calcPriceWithPercentage(price=currentPrice, percentage=profitPercentage)
            self.selling_price = sellingPrice
            self.calcStopLossVal(totalcoin=totalCoin)
            print("openPrice :", openPrice, "lowPrice :", lowPrice, "highPrice :", highPrice, "volume :", volume,
                  "currentPrice :", currentPrice, "sellingPrice : " + str(self.selling_price),
                  "quantity :" + str(self.quantity), "stop_loss :" + str(self.stop_loss))
            return

        if self.quantity > 0 and self.selling_price > 0 and float(currentPrice) >= float(self.selling_price):
            sellOrderAction = threading.Thread(
                target=self.sellOrderTest(short_symbol=short_symbol, quantity=self.quantity, price=currentPrice,
                                          btcOrBnb=btcOrBnb))
            sellOrderAction.start()
            self.test_total = self.quantity * float(currentPrice)
            print("total price : " + str(self.test_total))
            self.quantity = 0
            return

    def run(self):
        actions = []
        cnt = 0
        while True:
            startTime = time.time()
            actionTrader = threading.Thread(
                target=self.runRangeModeTest(short_symbol=self.short_symbol, profitPercentage=self.profitPercentage,
                                             btcOrBnb=self.btcOrBnb, walletPercentage=self.walletPercentage))
            actions.append(actionTrader)
            actionTrader.start()

            endTime = time.time()

            if endTime - startTime < self.wait_time:
                time.sleep(self.wait_time - (endTime - startTime))
            cnt = cnt + 1
            if cnt % 6 == 0:
                print(datetime.utcnow())
