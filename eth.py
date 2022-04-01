import requests
from MetaSingleton import MetaSingleton

WEI_TO_ETH = 1000000000000000000

class ETHBlockchain():

    ethPrice = None

    def __init__(self, token):
        self.token = token

    # Get last ETH price
    async def getETHPrice(self):
        global ethPrice
        url ="https://api.etherscan.io/api?module=stats&action=ethprice&apikey=" + self.token
        response = requests.get(url)
        ethPrice = float(response.json()["result"]["ethusd"])
        return response.json()["result"]["ethusd"]

    # Get ETH balance for address
    async def getETHBalance(self, address):
        url ="https://api.etherscan.io/api?module=account&action=balance&address=" + address + "&tag=latest&apikey=" + self.token
        response = requests.get(url)
        return float(response.json()["result"]) / WEI_TO_ETH
    
    # ETH to USD
    async def ethToUSD(self, eth):
        global ethPrice
        return eth * float(ethPrice)

    # ETH to EUR with api.coingecko.com
    async def ethToEUR(self, eth):
        global ethPrice
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=eur&include_market_cap=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false"
        response = requests.get(url)
        return eth * float(response.json()["ethereum"]["eur"])

    # Varify if address is valid and has 42 characters
    async def isValidAddress(self, address):
        url ="https://api.etherscan.io/api?module=account&action=balance&address=" + address + "&tag=latest&apikey=" + self.token
        response = requests.get(url)
        if (response.json()["message"] == "OK" and len(address) == 42):
            return True
        else:
            return False