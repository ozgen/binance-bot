from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceWithdrawException
from binance.websockets import BinanceSocketManager
import config
import json
from collections import namedtuple
import DateUtil

asset = "asset"
coin_qty = "free"


class BinanceBot:
    client = Client(config.api_key, config.api_secret)
    buying_price = 0.0
    selling_price = 0.0
    profit = 30  # percentages
    interval = Client.KLINE_INTERVAL_1MINUTE

    def __init__(self):
        pass

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
    def getHistoricDatafromCoin(self, short_symbol, btcOrBnb="BTC", limit=500):
        params = {}
        params["symbol"] = self.getSymbol(short_symbol, btcOrBnb)
        params["limit"] = limit
        params["interval"] = self.interval
        return self.client.get_klines(**params)

    def sellOrder(self, short_symbol, percentage, btcOrBnb="BTC"):

        pass

    def buyOrder(self, short_symbol, btcOrBnb="BTC"):
        pass


bot = BinanceBot()
# print(bot.client.ping())
print(bot.getHistoricDatafromCoin(short_symbol="XRP", limit=1))
print(DateUtil.interval_to_milliseconds(1517093460000))