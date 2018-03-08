from BinanceAPI import BinanceBot
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: XVG - ETH)', required=True)
    parser.add_argument('--btcorbnb', type=str, help='Market Symbol (Ex: BNB - BTC)', required=False)
    parser.add_argument('--profit', type=int, help='Market Symbol (Ex: 3 - 10)', required=False)
    parser.add_argument('--wallet', type=int, help='Market Symbol (Ex: 50 - 100)', required=False)
    parser.add_argument('--stoploss', type=int, help='Market Symbol (Ex: 3 - 6)', required=False)

    args = parser.parse_args()
    btcOrBnb = 'BTC'
    profitPercentage = 2
    walletPercentage = 100
    stop_loss_pecentage = 5

    short_symbol = str(args.symbol).upper()
    if args.btcorbnb:
        btcOrBnb = str(args.btcorbnb).upper()
    if args.profit:
        profitPercentage = args.profit
    if args.wallet:
        walletPercentage = args.wallet
    if args.stoploss:
        stop_loss_pecentage = args.stoploss

    bot = BinanceBot(short_symbol=short_symbol, btcOrBnb=btcOrBnb, profitPercentage=profitPercentage,
                     walletPercentage=walletPercentage, stop_loss_pecentage=stop_loss_pecentage)
    print(bot.client.ping())
    bot.run()
