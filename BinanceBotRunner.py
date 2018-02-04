from BinanceAPI import BinanceBot

bot = BinanceBot(short_symbol="VIBE", btcOrBnb="BTC", profitPercentage=0.1, walletPercentage=100, stop_loss_pecentage=6)
# print(bot.client.ping())
bot.run()
