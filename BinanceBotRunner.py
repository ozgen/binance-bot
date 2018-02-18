from BinanceAPI import BinanceBot

bot = BinanceBot(short_symbol="OAX", btcOrBnb="BTC", profitPercentage=1, walletPercentage=100, stop_loss_pecentage=6)
# print(bot.client.ping())
##bot.run()

#bot.pumpBuyAndSell(short_symbol="MOD")
