import time
import requests
import os
import json

API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
CACHE_DIR = os.path.dirname(__file__) + "/../Data/Cache/"

cacheDict:dict[str,None] = {}

idCache:dict[int,str] = {}

def getCardName(filename:str) -> str:
    ret = os.path.basename(filename)
    ret = os.path.splitext(ret)[0]
    ret = ret.replace("%2F","/").replace("%5C","\\").replace("%3A",":")
    return ret

#load cache
for file in os.listdir(CACHE_DIR):
    with open(CACHE_DIR+"/"+file) as f:
        name = getCardName(file)
        cardInfo = json.load(f)['data'][0]
        cacheDict[name] = cardInfo
        idCache[cardInfo["id"]]=name

def getFileName(name:str) -> str:
    ret = name.lower()
    ret = ret.replace("/","%2F").replace("\\","%5C").replace(":","%3A")
    return ret+".json"

def getNameFromId(id:int) -> str:
    if id in idCache:
        return idCache[id]
    else:
        for cardName, cardInfo in cacheDict.items():
            if cardInfo["id"]==id:
                idCache[id] = cardName
                return cardName
        return None



lastAPIRequestTime = 0
requestsThisSecond = 0
MAX_REQUESTS_PER_SECOND = 20

def waitForTimeout():
    global requestsThisSecond
    global lastAPIRequestTime
    if time.time() - lastAPIRequestTime < 1: #same second
        if requestsThisSecond >= MAX_REQUESTS_PER_SECOND:
            time.sleep(1-(time.time()-lastAPIRequestTime))
            lastAPIRequestTime = time.time()
            requestsThisSecond = 1
        else:
            requestsThisSecond += 1

def requestCard(card:str|int):
    
    if type(card)==str:
        name = card.lower()
        filename = CACHE_DIR+getFileName(name)
        if name in cacheDict: #file in fast cache (slow cache loaded at the start)
            return cacheDict[name]
        else:
            waitForTimeout()
            response = requests.get(API_URL,params={"name":name})
    elif type(card)==int:
        name = getNameFromId(card)
        if name is not None:
            return cacheDict[name]
        else:
            waitForTimeout()
            response = requests.get(API_URL,params={"id":card})

    if "error" in response.json():
        raise ValueError(response.json()["error"])
    name = response.json()['data'][0]["name"].lower()
    filename = CACHE_DIR+getFileName(name)
    with open(filename,"x") as f:
        f.write(response.text)
    ret = response.json()['data'][0]
    cacheDict[name] = ret
    return ret