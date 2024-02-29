#from telegram.ext import * 
from binance import Client
import ccxt
import requests
import pandas as pd
import regex
import time
import emoji

api_key = ApiKey
api_secret = ApiSecret
tapi_key = telegram bot api

#Veriables and lists

database = pd.DataFrame(columns=["Coin","Entry","Stop","TP"])

#BINANCE API
client = Client(api_key, api_secret, {"verify": False, "timeout": 20})

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future'}
})
exchange.enableRateLimit = True #Rate limit on

#Get futures pairs
futures_exchange_info = client.futures_exchange_info()  # request info on all futures symbols
trading_pairs = [info['symbol'] for info in futures_exchange_info['symbols']]

#Get messages in channel
URL = 'https://api.telegram.org/bot' + "<Bot Token>" + '/'
global last_update_id
last_update_id = 0

#CHECK SAME SIGNALS
    
beforeSignal = ''
beforeEntry = ''
beforeTP = ''
beforeStop = ''
while True:

    url = URL + 'getupdates'
    r = requests.get(url)
    data = r.json()

   

    last_object = data['result'][-1]
    current_update_id = last_object['update_id']

    if last_update_id != current_update_id:
        last_update_id = current_update_id

        chat_id = last_object['message']['chat']['id'] #'channel_post'
        message_text = last_object['message']['text']
        message = {
        'chat_id': chat_id, 
        'text': message_text
                }
            #print(message['chat_id'], message['text'])
    channel_id = message['chat_id']
    text = message['text']        
    
###### COD STARTING #####
    #CHECKING SAME SIGNALS
    if beforeSignal != text:
        beforeSignal = text

        
        oldlst = text.upper()
        oldlst = oldlst.split(' ')

        lst = []
        for i in oldlst:
            y = i.split('\n')
            for z in y:
                if z != "":
                    lst.append(z)

            regex.sub("\n", "", i)
        print("LST ISSSSSSSSSSSSS: ",lst)

        if channel_id == Chanel_Id
            if "#BOT" in lst:
                #Search in text
                ticker = "-"
                coin_name = ""
                coinPairName = ""
                for i in lst:
                    try:
                        try:
                            ticker = exchange.fetch_ticker(i+"/USDT")
                            if ticker != "-":
                                coin_name = i
                                coinPairName = i+"USDT"
                                break
                        except:
                            ticker = exchange.fetch_ticker(i+"/BUSD")
                            if ticker != "-":
                                coin_name = i
                                coinPairName = i+"BUSD"
                                break

                    except:
                        print("not found")
                print(ticker)
                Entry = []
                Tp = []
                Stop = ""
                Position = ""
                if ticker != "-":
                    Entry.append(lst[lst.index(coin_name)+1])
                    Entry.append(lst[lst.index(coin_name)+2])
                    
                    for i in lst:
                        for k in range(20):
                            if i == "TP"+str(k):
                                Tp.append(lst[lst.index(i)+1])
                        
                        if i == "STOP":
                            Stop = lst[lst.index(i)+1]
                        
                    if float(Stop) < float(Entry[0]):
                        Position = "LONG"
                    else:
                        Position = "SHORT"

                    database = database.append({'Coin' : coinPairName, 'Entry' : Entry, 'Position' : Position, 'Stop' : Stop, "TP" : Tp, "Status" : "None", "TP Status" : "TP IS NONE"},
                    ignore_index = True)


####Price Tracer#####
    for i in database["Coin"]:
        priceData = client.futures_historical_klines(i, Client.KLINE_INTERVAL_1MINUTE, "1 Minutes ago UTC")
        #priceData = priceData.values.tolist()
        print(priceData)
        print(float(priceData[0][3]))
        index = database[database['Coin'] == i].index.values #index finder

        if database.loc[index[0]]["Position"] == "LONG":

            #Check Is there an ENTRY price? FOR LONG
            if float(priceData[0][3]) <= float(database.loc[index[0]]["Entry"][0]) or float(priceData[0][3]) <= float(database.loc[index[0]]["Entry"][1]):
                database.loc[index[0]]["Status"] = "in the process"

                #Check Stop value:
                if float(database.loc[index[0]]["Stop"][0]) > float(priceData[0][3]):
                    database.loc[index[0]]["Status"] = "STOP Position"

                #Check Is there an TP price? FOR LONG
                if database.loc[index[0]]["Status"] != "STOP Position":
                    tpReachedList = []
                    for i in range(0, len(database.loc[index[0]]["TP"])-1):
                        if float(priceData[0][2]) >= float(database.loc[index[0]]["TP"][i]):

                            tpReachedList.append("TP "+str(i)+" "+float(database.loc[index[0]]["TP"][i])+" Başarıyla Ulaşıldı")

                    database.loc[index[0]]["TP Status"] = tpReachedList

        if database.loc[index[0]]["Position"] == "SHORT":

            #Check Is there an ENTRY price? FOR SHORT
            if float(priceData[0][2]) >= float(database.loc[index[0]]["Entry"][0]) or float(priceData[0][2]) >= float(database.loc[index[0]]["Entry"][1]):
                database.loc[index[0]]["Status"] = "in the process"

                #Check Stop value:
                if float(database.loc[index[0]]["Stop"]) < float(priceData[0][3]):
                    database.loc[index[0]]["Status"] = "STOP Position"
                
                #Check Is there an TP price? FOR SHORT
                if database.loc[index[0]]["Status"] != "STOP Position":
                    tpReachedList = []
                    for i in range(len(database.loc[index[0]]["TP"])-1):
                        if float(priceData[0][3]) <= float(database.loc[index[0]]["TP"][i]):

                            tpReachedList.append("TP "+str(i)+" "+float(database.loc[index[0]]["TP"][i])+" Başarıyla Ulaşıldı")
                            

                        database.loc[index[0]]["TP Status"] = tpReachedList

        print(database)
        # TELEGRAM SEND MESSAGE
        if database.loc[index[0]]["Status"] == "in the process":
            
            #TP RED DOTS
            entval = ""
            tpval = ""
            for i in (database.loc[index[0]]["TP"]):
                #entry
                entval2 = emoji.emojize(':red_circle:') + " TP " + i + "\n"
                entval = entval + entval2

                #tp
                if i in database.loc[index[0]]["TP Status"]:
                    tpval2 = emoji.emojize(':red_circle:') + " TP " + i + "\n"
                    tpval = tpval + tpval2
                else:
                    tpval2 = emoji.emojize(':green_circle:') + " TP " + i + "\n"
                    tpval = tpval + tpval2
            print(database.loc[index[0]]["Status"])
            
            
            #ENTRY   
            entryMessage = emoji.emojize(':green_circle:') +" "+ database.loc[index[0]]["Coin"] + " " + database.loc[index[0]]["Position"] + " GİRİŞE GELMİŞTİR EFM" + "\n" + entval
            if entryMessage != beforeEntry:
                beforeEntry = entryMessage
                requests.post(url="https://api.telegram.org/<Bot Token>/sendMessage",data={"chat_id":chat_id,"text":entryMessage}).json

            #TP
            if database.loc[index[0]]["TP Status"] != []:
                tpMessage = emoji.emojize(':green_circle:') +" "+ database.loc[index[0]]["Coin"] + " " + database.loc[index[0]]["Position"] + " TP DEĞERİNE GELMŞTİR EFM" + "\n" + tpval
                if beforeTP != database.loc[index[0]]["TP Status"][len(database.loc[index[0]]["TP Status"])-1]:

                    beforeTP = database.loc[index[0]]["TP Status"][len(database.loc[index[0]]["TP Status"])-1]

                    requests.post(url="https://api.telegram.org/<Bot Token>/sendMessage",data={"chat_id":chat_id,"text":database[index[0]]["TP Status"][len(database[index[0]]["TP Status"])-1]}).json
        """
        tpMessage = len(database.loc[index[0]]["TP"][(len(database.loc[index[0]]["TP"])-1)])
        stopMessage = database.loc[index[0]]["Status"]
        entryMessage = 
        """

        time.sleep(2)

    print(database)
    
    #LONG SHORT DETECT
    

    #COD STARTING...
    



"""
def search_futures(liste):
    for i in liste:
        i = i + "/USDT"
        if i in trading_pairs:
            coiname = i
    return coiname
print(trading_pairs)
get_updates()
text = get_message()[1].lower()


"""
"""
if get_message()[0] == channel_id:
    #Search in text
    lst = text.split(' ')

    whatchlist = pd.DataFrame(columns=["Coin","Position","Entry","TP"])
"""
