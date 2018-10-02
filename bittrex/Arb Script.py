import unittest
import json
import math
import time
import datetime
import csv

from bittrex import Bittrex

import pyrebase 

config = {
  "apiKey": "AIzaSyD2dKAWUng-VCP24o6MYXy8VblZtdIttvs",
  "authDomain": "arb-bot-b719f.firebaseapp.com",
  "databaseURL": "https://arb-bot-b719f.firebaseio.com/",
  "storageBucket": "arb-bot-b719fappspot.com",
}

firebase = pyrebase.initialize_app(config)

try:
    open("secrets.json").close()
    IS_CI_ENV = False
except Exception:
    IS_CI_ENV = True

class CryptoArb(object):
    """
    Integration tests for the Bittrex Account API.
      * These will fail in the absence of an internet connection or if bittrex API goes down.
      * They require a valid API key and secret issued by Bittrex.
      * They also require the presence of a JSON file called secrets.json.
      It is structured as such:
    {
      "key": "12341253456345",
      "secret": "3345745634234534"
    }
    """

    def setUp(self):
        with open("secrets.json") as secrets_file:
            self.secrets = json.load(secrets_file)
            secrets_file.close()
        self.bittrex = Bittrex(self.secrets['key'], self.secrets['secret'])

    def test(self):
        
        desiredResult = .95
    
        
        ## ETHEREUM

        btcResult = 0
        LoopNumber = 1

        while btcResult < desiredResult:
 
            markets = self.bittrex.get_market_summaries()
            

            marketCount = len(markets["result"])

            print("Start - " + str(LoopNumber))
            btcCount = 0
            ethCount = 0


            ### ~~ Filling the BTC-ALT Matrix ~~ ###

            # Counting the number of BTC Currency Pairs
            btcLoopCount = 0
            while btcLoopCount < marketCount:
                if "BTC-" in markets["result"][btcLoopCount]["MarketName"]:
                    btcCount = btcCount + 1
                btcLoopCount = btcLoopCount + 1

            # Creating the BTC pair-exchange matrix
            btcCol, btcRow = 2, btcCount;
            BTCMatrix = [[0 for x in range(btcCol)] for y in range(btcRow)]

            # Filling the BTC Matrix
            btcLoopCount = 0 
            btcMatrixRowCount = 0

            while btcLoopCount < marketCount:
                if "BTC-" in markets["result"][btcLoopCount]["MarketName"]:

                    BTCMatrix[btcMatrixRowCount][0] = markets["result"][btcLoopCount]["MarketName"]
                    BTCMatrix[btcMatrixRowCount][1] = markets["result"][btcLoopCount]["Ask"]

                    btcMatrixRowCount = btcMatrixRowCount + 1

                btcLoopCount = btcLoopCount + 1

            
            ### ~~ Filling the ETH-ALT Matrix ~~ ###

            # Counting the number of ETH Currency Pairs
            ethLoopCount = 0
            while ethLoopCount < marketCount:
                if "ETH-" in markets["result"][ethLoopCount]["MarketName"]:
                    ethCount = ethCount + 1
                ethLoopCount = ethLoopCount + 1

            # Creating the ETH pair-exchange matrix
            ethCol, ethRow = 2, ethCount;
            ETHMatrix = [[0 for x in range(ethCol)] for y in range(ethRow)]

            # Filling the ETH Matrix
            ethLoopCount = 0
            ethMatrixRowCount = 0

            while ethLoopCount < marketCount:
                if "ETH-" in markets["result"][ethLoopCount]["MarketName"]:

                    ETHMatrix[ethMatrixRowCount][0] = markets["result"][ethLoopCount]["MarketName"]
                    ETHMatrix[ethMatrixRowCount][1] = markets["result"][ethLoopCount]["Bid"]

                    ethMatrixRowCount = ethMatrixRowCount + 1

                ethLoopCount = ethLoopCount + 1
            

            btc_ethTick = self.bittrex.get_ticker("BTC-ETH")
            btc_eth_BTC = btc_ethTick["result"]["Bid"]


            # ~~~ Comparing Bitcoin Arbitrage Returns ~~~ #

            arbBTCPairs = []
            arbBTCReturn = []
            arbBTCTestReturn = []
            arbBTCRow = 0

            for btcAlt in BTCMatrix:
                
                for ethAlt in ETHMatrix:
                    
                    if ethAlt[0][4:] == btcAlt[0][4:]:

                        btcResult = 0

                        #arbBTCPairs.append(str(btcAlt[0]) + " > " + str(ethAlt[0]) + " > BTC_ETH")
                        arbPath = str(btcAlt[0]) + " > " + str(ethAlt[0]) + " > BTC_ETH"

                        btcAltDiff = 0.0000007
                        altEthDiff = -0.0000002
                        ethBtcDiff = -0.000001

                        # Forumla to check returns
                        print("BTC -> Alt: " + str(btcAlt[1]))
                        btc_altX = float(btcAlt[1] + btcAltDiff)
                        print("Alt -> ETH: " + str(ethAlt[1]))
                        eth_altX = float(ethAlt[1] + altEthDiff)
                        print("ETH -> BTC: " + str(btc_eth_BTC))
                        btc_ethX = float(btc_eth_BTC + ethBtcDiff)
                        

                        #test1 = float(btcAlt[1] - 0.00000001)
                        #test2 = float(ethAlt[1] - 0.00000001)
                        #test3 = float(btc_eth_BTC - 0.0000004)

                        print(str(btcAlt[0]) + " > " + str(ethAlt[0]) + " > BTC_ETH")

                        btcUnits = 1
                        print("BTC = " + str(btcUnits))

                        altUnits = round(((btcUnits / 1.0025) / btc_altX), 8)
                        #testaltUnits = round(((btcUnits / 1.0025) / test1), 8)

                        print("Alt Units = " + str(altUnits) + " (" + str(btc_altX) + ")")
                        #print("Test Alt Units = " + str(testaltUnits) + " (" + str(test1) + ")")


                        ethUnits = round(((altUnits - (altUnits * 0.0025)) * eth_altX), 8)
                        #testethUnits = round(((testaltUnits - (testaltUnits * 0.0025)) * test2), 8)

                        print("ETH Units = " + str(ethUnits) + " (" + str(eth_altX) + ")")
                        #print("Test ETH Units = " + str(testethUnits) + " (" + str(test2) + ")")


                        btcResult = round(((ethUnits - (ethUnits * 0.0025)) * btc_ethX), 8)
                        #testbtcResult = round(((testethUnits - (testethUnits * 0.0025)) * test3), 8)

                        print("BTC Result = " + str(btcResult) + " (" + str(btc_ethX) + ")")
                        #print("Test BTC Result = " + str(testbtcResult) + " (" + str(test3) + ")")

                        print("")

                        #arbBTCReturn.append(btcResult)
                        #arbBTCTestReturn.append(testbtcResult)
                        print(btcAlt[0])
                        if(btcResult) >= desiredResult and btcAlt[0] != "BTC-SALT":
                            print("!! Desired Result Reached !!")
                            break

                        arbBTCRow = arbBTCRow + 1
                        

                if(btcResult) >= desiredResult and btcAlt[0] != "BTC-SALT":
                        break


            print("")

            # If desired result is not reached empty the lists to start again
            if btcResult <= desiredResult:
                BTCMatrix[:] = []
                ETHMatrix[:] = []
                arbBTCPairs[:] = []
                arbBTCReturn[:] = []

            LoopNumber = LoopNumber + 1

            # Loops if return isn't good enough i.e. > 1.005



        # Loop has been exited because return is good enough
        # If statement is final check to make sure return is good enough
        if float(btcResult) > desiredResult and btcAlt[0] != "BTC-SALT":

            print("Arb Return = " + str(btcResult))

            print("begin timer")

            startTime = time.time()

            # Path of the arb which yiels return i.e. BTC -> ALT -> ETH -> BTC
            #print(arbPath)

            # Getting name of Alt
            if len(arbPath) == 25:
                alt = arbPath[4:6]
                print("Alt = " + alt)

            elif len(arbPath) == 27:
                alt = arbPath[4:7]
                print("Alt = " + alt)

            elif len(arbPath) == 29:
                alt = arbPath[4:8]
                print("Alt = " + alt)

            elif len(arbPath) == 31:
                alt = arbPath[4:9]
                print("Alt = " + alt)

            else:
                print("Wrong Number Letters " + len(arbPath))

            print("Time elapsed " + str(time.time() - startTime))


            # Begin Buy Process
            
            orderBTCALTBook = self.bittrex.get_orderbook("BTC-" + str(alt), "sell")

            print("")

            #BTCBal = self.bittrex.get_balance("BTC")

            #if str(BTCBal["result"]["Balance"]) == "None":
            #    principle = 0
            #else:
            #    principle = float(BTCBal["result"]["Balance"])

            principle = 0.00065
            print("Principle = " + str(principle))

            AltQuantity = 0
            ETHQuantity = 0
            BTCQuantity = 0
            market = "BTC-" + alt
            print("Market = " + market)
            print("")

            actBtcAltRate = 0
            actAltEthRate = 0
            actEthBtcRate = 0

            btcOrderCount = 0
            while principle > 0:
                
                print("BTC -> " + str(alt) + " Order " + str(btcOrderCount + 1) + ": Principle = " + str(principle))

                askQuantity = orderBTCALTBook["result"][btcOrderCount]["Quantity"]
                askRate = orderBTCALTBook["result"][btcOrderCount]["Rate"]
                askTotal = askQuantity * askRate

                print("-- Order Details: --")
                print("---- Ask Quantity = " + str(askQuantity))
                print("---- Ask Rate = " + str(askRate))
                print("---- Ask Total = " + str(askTotal))
                print("---- Principle = " + str(principle))
                print("")

                if askTotal > principle:
                    print("---- Executing full final trade...")
                    tradeQuantity = math.floor(((principle / 1.0025) / askRate)*100000000)/100000000
                    print("---- Trade Quantity = " + str(tradeQuantity) + " (" + str(principle / 1.0025) + " / " + str(askRate) + ")")
                    # Execute full or remainder of trade
                    AltQuantity = AltQuantity + tradeQuantity
                    print("---- BUY " + str(AltQuantity) + " " + str(alt) +" @ " + str(askRate) + "BTC = " + str( round((AltQuantity * askRate), 8)))
                    
                    altBuy = self.bittrex.buy_limit(market, AltQuantity, askRate)
                    print("---- " + str(altBuy))
                    actBtcAltRate = askRate # I can delete this because I have a more accurate below from get_order_history
                    altBuy = True
                    break
                else:
                    # Execute a portion of the trade
                    print("---- Partial Trade - CANCEL ... ")
                    print("---- BUY " + str(askQuantity) + str(alt) + " @ " + str(askRate) + " BTC = " + str(round((askQuantity * askRate), 8)))
                    AltQuantity = AltQuantity + askQuantity
                    principle = principle - askTotal
                    break
                    #buy = self.bittrex.buy_limit(market, askQuantity, askRate)
                    #print(buy)
                    #principle = (principle * 0.9975) - askTotal
                    # execute trade
                
                btcOrderCount = btcOrderCount + 1

            print("")
            print(str(alt) + " Quantity = " + str(AltQuantity))
            firstTrade = time.time() - startTime
            secondTrade = 0
            finalTrade = 0
            print("Time since arb calc = " + str(firstTrade))

            print("")

            if altBuy == True:

                orderETHALTBook = self.bittrex.get_orderbook("ETH-" + str(alt), "buy")

                market = "ETH-" + alt

                ogAltQuantity = AltQuantity

                altOrderCount = 0
                while AltQuantity > 0:

                    print(str(alt) + " -> ETH Order " + str(altOrderCount + 1) + ": Principle = " + str(AltQuantity))
                    bidQuantity = orderETHALTBook["result"][altOrderCount]["Quantity"]
                    bidRate = orderETHALTBook["result"][altOrderCount]["Rate"]
                    bidTotal = bidQuantity * bidRate

                    print("-- Order Details: --")
                    print("---- Bid Quantity = " + str(bidQuantity))
                    print("---- Bid Rate = " + str(bidRate))
                    print("---- Bid Total = " + str(bidTotal))
                    print("---- Alt Quantity = " + str(AltQuantity))
                    print("")


                    if bidQuantity > AltQuantity:
                        print("Executing full final trade...")
                        tradeQuantity = math.floor(((AltQuantity * 0.9975) * bidRate)*100000000)/100000000
                        print("---- Trade Quantity = " + str(tradeQuantity) + " (" + str(AltQuantity) + " * " + str(bidRate) + ")")
                        # Execute full or remainder of trade 
                        print("---- SELL " + str(ogAltQuantity) + " " + str(alt) +" @ " + str(bidRate) + "ETH = " + str(tradeQuantity))
                        ETHQuantity = ETHQuantity + tradeQuantity

                        altSell = self.bittrex.sell_limit(market, ogAltQuantity, bidRate)
                        print("---- " + str(altSell))
                        actAltEthRate = bidRate # I can delete this because I have a more accurate below from get_order_history
                        altSell = True
                        break
                    else:
                        # Execute a portion of the trade
                        print("---- Executing partial trade... " + str(bidQuantity) + str(alt) +" @ " + str(bidRate) + "ETH = " + str(bidQuantity * bidRate))
                        ETHQuantity = (ETHQuantity + bidTotal) * 0.9975
                        sell = self.bittrex.sell_limit(market, bidQuantity, bidRate)
                        print(sell)
                        AltQuantity = AltQuantity - bidQuantity
                        # execute trade
                    
                    print("")
                    altOrderCount = altOrderCount + 1


                if altSell == True:

                    print("")
                    print("ETH Quantity = " + str(ETHQuantity))
                    secondTrade = time.time() - startTime
                    print("Time since arb calc = " + str(secondTrade))
                    print("")

                    orderBTCETHBook = self.bittrex.get_orderbook("BTC-ETH", "buy")

                    ogETHQuantity = ETHQuantity

                    market = "BTC-ETH"

                    ethOrderCount = 0
                    while ETHQuantity > 0:
                        print("ETH -> BTC Order " + str(ethOrderCount + 1) + ": Principle = " + str(ETHQuantity))
                        bidQuantity = orderBTCETHBook["result"][ethOrderCount]["Quantity"]
                        bidRate = orderBTCETHBook["result"][ethOrderCount]["Rate"]
                        bidTotal = bidQuantity * bidRate

                        print("-- Order Details: --")
                        print("---- Bid Quantity = " + str(bidQuantity))
                        print("---- Bid Rate = " + str(bidRate))
                        print("---- Bid Total = " + str(bidTotal))
                        print("---- ETH Quantity = " + str(ETHQuantity))
                        print("")

                        if bidQuantity > ETHQuantity:
                            print("---- Executing full final trade...")
                            tradeQuantity = math.floor(((ETHQuantity * 0.9975) * bidRate)*100000000)/100000000
                            print("---- Trade Quantity = " + str(tradeQuantity) + " (" + str(ETHQuantity) + " * " + str(bidRate) + ")")
                            # Execute full or remainder of trade 
                            print("---- SELL " + str(ogETHQuantity) + " ETH @ " + str(bidRate) + "BTC = " + str(tradeQuantity))
                            BTCQuantity = BTCQuantity + tradeQuantity

                            sell = self.bittrex.sell_limit(market, ogETHQuantity, bidRate)
                            print("---- " + str(sell))
                            actEthBtcRate = bidRate # I can delete this because I have a more accurate below from get_order_history
                            break
                        else:
                            # Execute a portion of the trade
                            print("---- Executing partial trade... " + str(bidQuantity) + "ETH @ " + str(bidRate) + "BTC = " + str(bidQuantity * bidRate))
                            BTCQuantity = BTCQuantity + bidTotal
                            sell = self.bittrex.sell_limit(market, bidQuantity, bidRate)
                            print(sell)

                            ETHQuantity = ETHQuantity - bidQuantity
                            # execute trade
                        
                        ethOrderCount = ethOrderCount + 1

                    print(BTCQuantity)

                    finalTrade = time.time() - startTime
                    print("Time since arb calc = " + str(finalTrade))


                    btcAltMarket = self.bittrex.get_market_summary("BTC-" + str(alt))
                    btcAltVolume = btcAltMarket["result"][0]["Volume"]

                    altEthMarket = self.bittrex.get_market_summary("ETH-" + str(alt))
                    altEthVolume = altEthMarket["result"][0]["Volume"]

                    ethBtcMarket = self.bittrex.get_market_summary("BTC-ETH")
                    ethBtcVolume = ethBtcMarket["result"][0]["Volume"]

                    #  Grab bittrex Trade Details
                    #  1 - BTC-ALT
                    #tradeDetails = self.bittrex.get_order_history()

                    tradeDetails = self.bittrex.get_order_history()
                    tradeOne = tradeDetails["result"][2]
                    tradeTwo = tradeDetails["result"][1]
                    tradeThree = tradeDetails["result"][0]

                    #  Actual Arb Return
                    tradeOneActualValue = tradeOne["Price"] + tradeOne["Commission"]
                    tradeThreeActualValue = tradeThree["Price"] + tradeThree["Commission"]
                    actualArbReturn = tradeThreeActualValue / tradeOneActualValue

                    # Actual Rates
                    tradeOneActualRate = tradeOne["PricePerUnit"]
                    tradeTwoActualRate = tradeTwo["PricePerUnit"]
                    tradeThreeActualRate = tradeThree["PricePerUnit"]


                    with open('Trade Tracker.csv', 'a', newline='') as csvfile:
                        tracker = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        tracker.writerow([arbPath, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], btcResult, actualArbReturn,
                            str(btcAlt[1]), str(btcAltDiff), btcAlt[1] + btcAltDiff, tradeOneActualRate, str(btcAlt[1] - tradeOneActualRate), str(((btcAlt[1] - tradeOneActualRate)/btcAlt[1])*100), str(firstTrade), str(btcAltVolume),
                            str(ethAlt[1]), str(altEthDiff), str(ethAlt[1] + altEthDiff), tradeTwoActualRate, str(ethAlt[1] - tradeTwoActualRate), str(((ethAlt[1] - tradeTwoActualRate)/ethAlt[1])*100), str(secondTrade), str(altEthVolume),
                            str(btc_eth_BTC), str(ethBtcDiff), str(btc_eth_BTC + ethBtcDiff), tradeThreeActualRate, str(btc_eth_BTC - tradeThreeActualRate), str(((btc_eth_BTC - tradeThreeActualRate)/btc_eth_BTC)*100), str(finalTrade), str(ethBtcVolume)])

                    print("Excel Save Successful")

                    db = firebase.database()

                    data = {
                        "Arb Path": arbPath,
                        "Date Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                        "Principle": principle,
                        "Actual Return": BTCQuantity,
                        "Expected Arb Return": btcResult,
                        "Actual Arb Return": actualArbReturn,
                        "Trade 1 Quoted Rate": str(btcAlt[1]), 
                        "Trade 1 Adjustment": str(btcAltDiff), 
                        "Trade 1 Adjusted Quote": btcAlt[1] + btcAltDiff, 
                        "Trade 1 Actual Rate": tradeOneActualRate, 
                        "Trade 1 Actual-Quote Diff": str(btcAlt[1] - tradeOneActualRate), 
                        "Trade 1 Actual-Quote % Diff":  str(((btcAlt[1] - tradeOneActualRate)/btcAlt[1])*100), 
                        "Trade 1 Time From Quote": str(firstTrade), 
                        "Trade 1 Market Volume": str(btcAltVolume),
                        "Trade 2 Quoted Rate": str(ethAlt[1]), 
                        "Trade 2 Adjustment": str(altEthDiff), 
                        "Trade 2 Adjusted Quote": str(ethAlt[1] + altEthDiff), 
                        "Trade 2 Actual Rate": tradeTwoActualRate, 
                        "Trade 2 Actual-Quote Diff": str(ethAlt[1] - tradeTwoActualRate),
                        "Trade 2 Actual-Quote % Diff": str(((ethAlt[1] - tradeTwoActualRate)/ethAlt[1])*100), 
                        "Trade 2 Time From Quote": str(secondTrade), 
                        "Trade 2 Market Volume": str(altEthVolume),
                        "Trade 3 Quoted Rate": str(btc_eth_BTC), 
                        "Trade 3 Adjustment": str(ethBtcDiff), 
                        "Trade 3 Adjusted Quote": str(btc_eth_BTC + ethBtcDiff), 
                        "Trade 3 Actual Rate": tradeThreeActualRate, 
                        "Trade 3 Actual-Quote Diff": str(btc_eth_BTC - tradeThreeActualRate), 
                        "Trade 3 Actual-Quote % Diff Rate": str(((btc_eth_BTC - tradeThreeActualRate)/btc_eth_BTC)*100), 
                        "Trade 3 Time From Quote": str(finalTrade), 
                        "Trade 3 Market Volume": str(ethBtcVolume)
                    }

                    db.child("Successful Transactions").push(data)

                else:
                    print("ALT -> ETH Fail")

            else:
                print("BTC -> ALT Fail")


if __name__ == '__main__':
    test = CryptoArb()
    test.setUp()
    test.test()
