# binance-bot

Python Dependency: 3.6

Go API Center, Create New Api Key

 [✓] Read Info [✓] Enable Trading [X] Enable Withdrawals
Rename config.sample.py to config.py 

Get an API and Secret Key, insert into config.py

 API key for account access
 api_key = ''
 Secret key for account access
 api_secret = ''

 [API Docs](https://www.binance.com/restapipub.html) 


In order to run pump bot  : 

```sh
git clone https://github.com/ozgen/binance-bot.git
cd binance-bot
python3 PumpRunner.py --symbol iost (the coin symbol to pump)
```

In order to run trade bot :

```sh
git clone https://github.com/ozgen/binance-bot.git
cd binance-bot
python3 BinanceBotRunner.py --symbol xrp --profit 5 --wallet 100 (example of sample script)

```



