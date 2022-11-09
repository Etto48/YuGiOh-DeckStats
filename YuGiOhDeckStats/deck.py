import os 
import tabulate
from typing import Callable
import tomllib
import random
from importlib.machinery import SourceFileLoader

from . import fetcher

TABLE_FMT = "rounded_outline"

class Deck:
    def __init__(self,name:str):
        self.name = name
        self.mainDeck:dict[str,int] = {}
        self.extraDeck:dict[str,int] = {}
        self.sideDeck:dict[str,int] = {}
    def fromFile(file:str):
        deckName,ext = os.path.splitext(os.path.basename(file))
        ret = Deck(deckName)
        mainDeckLine = "#main" if ext == ".ydk" else "Main Deck:"
        extraDeckLine = "#extra" if ext == ".ydk" else "Extra Deck:"
        sideDeckLine = "!side" if ext == ".ydk" else "Side Deck:"


        with open(file,"r") as f:
            lines = f.readlines()
        writeTo = "main"
        for l in lines:
            if mainDeckLine in l:
                writeTo = "main"
            elif extraDeckLine in l:
                writeTo = "extra"
            elif sideDeckLine in l:
                writeTo = "side"
            elif l[0] == "-" or l[0] == "#" or l.strip() == "\n":
                pass
            else:
                if ext == ".ydk":
                    id = l.split()[0]
                    try:
                        cardInfo = fetcher.requestCard(int(id))
                    except ValueError:
                        raise
                    if writeTo == "main":
                        if cardInfo["name"]  in ret.mainDeck:
                            ret.mainDeck[cardInfo["name"]] += 1
                        else:
                            ret.mainDeck[cardInfo["name"]] = 1
                    elif writeTo == "extra":
                        if cardInfo["name"] in ret.extraDeck:
                            ret.extraDeck[cardInfo["name"]] += 1
                        else:
                            ret.extraDeck[cardInfo["name"]] = 1
                    elif writeTo == "side":
                        if cardInfo["name"] in ret.sideDeck:
                            ret.sideDeck[cardInfo["name"]] += 1
                        else:
                            ret.sideDeck[cardInfo["name"]] = 1
                else:
                    n = l.split()[0]
                    n = n.strip("x")
                    cardName = " ".join(l.split()[1:])
                    try:
                        cardInfo = fetcher.requestCard(cardName)
                    except ValueError:
                        raise 
                    if writeTo == "main":
                        ret.mainDeck[cardInfo["name"]] = int(n)
                    elif writeTo == "extra":
                        ret.extraDeck[cardInfo["name"]] = int(n)
                    elif writeTo == "side":
                        ret.sideDeck[cardInfo["name"]] = int(n)
        return ret   

    def save(self,filename:str):
        ext = os.path.splitext(filename)[1]
        with open(filename,"w") as f:
            if ext == ".ydk":
                f.write("#main \n")
                for name, count in self.mainDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    for i in range(count):
                        f.write(f"{cardInfo['id']}\n")
                f.write("#extra \n")
                for name, count in self.extraDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    for i in range(count):
                        f.write(f"{cardInfo['id']}\n")
                f.write("!side \n")
                for name, count in self.sideDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    for i in range(count):
                        f.write(f"{cardInfo['id']}\n")
            else:
                f.write("Main Deck:\n")
                for name, count in self.mainDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    f.write(f"{count}x {cardInfo['name']}\n")
                f.write("Extra Deck:\n")
                for name, count in self.extraDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    f.write(f"{count}x {cardInfo['name']}\n")
                f.write("Side Deck:\n")
                for name, count in self.sideDeck.items():
                    cardInfo = fetcher.requestCard(name)
                    f.write(f"{count}x {cardInfo['name']}\n")



    def mainCount(self):
        ret = 0
        for k,v in self.mainDeck.items():
            ret += v
        return ret
    
    def extraCount(self):
        ret = 0
        for k,v in self.extraDeck.items():
            ret += v
        return ret
    
    def sideCount(self):
        ret = 0
        for k,v in self.sideDeck.items():
            ret += v
        return ret
    
    def totalCount(self):
        return self.mainCount() + self.extraCount() + self.sideCount()

    def __str__(self):
        return f"Name: {self.name}, Main: {self.mainCount()}, Extra: {self.extraCount()}, Side: {self.sideCount()}"

    def archetypes(self):
        archetypes:dict[str,int] = {}
        archetypes["Generic"] = 0
        for cardName, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(cardName)
            if "archetype" in cardInfo:
                if cardInfo["archetype"] in archetypes:
                    archetypes[cardInfo["archetype"]] += count
                else:
                    archetypes[cardInfo["archetype"]] = count
            else:
                archetypes["Generic"] += count               
        for cardName, count in self.extraDeck.items():
            cardInfo = fetcher.requestCard(cardName)
            if "archetype" in cardInfo:
                if cardInfo["archetype"] in archetypes:
                    archetypes[cardInfo["archetype"]] += count
                else:
                    archetypes[cardInfo["archetype"]] = count
            else:
                archetypes["Generic"] += count
        for cardName, count in self.sideDeck.items():
            cardInfo = fetcher.requestCard(cardName)
            if "archetype" in cardInfo:
                if cardInfo["archetype"] in archetypes:
                    archetypes[cardInfo["archetype"]] += count
                else:
                    archetypes[cardInfo["archetype"]] = count
            else:
                archetypes["Generic"] += count
        
        return archetypes

    def summary(self):
        tabData = [
            ["Main",self.mainCount()],
            ["Extra",self.extraCount()],
            ["Side",self.sideCount()]]
        print(tabulate.tabulate(tabData,headers=["Deck","Cards"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {"Monster":0,"Spell":0,"Trap":0}
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "monster" in cardInfo["type"].lower():
                dictData["Monster"] += count
            elif "spell" in cardInfo["type"].lower():
                dictData["Spell"] += count
            elif "trap" in cardInfo["type"].lower():
                dictData["Trap"] += count
        mainDeckSize = self.mainCount()
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/mainDeckSize*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Category","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        monsterCount = 0
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "monster" in cardInfo["type"].lower():
                monsterCount += count
                if cardInfo["attribute"] in dictData:
                    dictData[cardInfo["attribute"]] += count
                else:
                    dictData[cardInfo["attribute"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/monsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Monster Attribute","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        monsterCount = 0
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "monster" in cardInfo["type"].lower():
                monsterCount += count
                if cardInfo["race"] in dictData:
                    dictData[cardInfo["race"]] += count
                else:
                    dictData[cardInfo["race"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/monsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Monster Type","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {"Toon":0,"Spirit":0,"Union":0,"Gemini":0,"Flip":0}
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "monster" in cardInfo["type"].lower():
                for k in dictData.keys():
                    if k.lower() in cardInfo["type"].lower():
                        dictData[k] += count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/monsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Monster Ability","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {"Normal":0,"Effect":0,"Tuner":0,"Pendulum":0}
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "monster" in cardInfo["type"].lower():
                for k in dictData.keys():
                    if k.lower() in cardInfo["type"].lower():
                        dictData[k] += count
                if "normal" not in cardInfo["type"].lower() and "effect" not in cardInfo["type"].lower():
                    dictData["Effect"] += count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/monsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Monster Classification","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        spellCount = 0
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "spell" in cardInfo["type"].lower():
                spellCount += count
                if cardInfo["race"] in dictData:
                    dictData[cardInfo["race"]] += count
                else:
                    dictData[cardInfo["race"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/spellCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Spell Type","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        trapCount = 0
        for card, count in self.mainDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "trap" in cardInfo["type"].lower():
                trapCount += count
                if cardInfo["race"] in dictData:
                    dictData[cardInfo["race"]] += count
                else:
                    dictData[cardInfo["race"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/trapCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Main Deck Trap Type","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {"Fusion":0,"Synchro":0,"XYZ":0,"Link":0}
        for card, count in self.extraDeck.items():
            cardInfo = fetcher.requestCard(card)
            if "fusion" in cardInfo["type"].lower():
                dictData["Fusion"] += count
            elif "synchro" in cardInfo["type"].lower():
                dictData["Synchro"] += count
            elif "xyz" in cardInfo["type"].lower():
                dictData["XYZ"] += count
            elif "link" in cardInfo["type"].lower():
                dictData["Link"] += count
        extraDeckSize = self.extraCount()
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/extraDeckSize*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Extra Deck Category","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        extraMonsterCount = 0
        for card, count in self.extraDeck.items():
            cardInfo = fetcher.requestCard(card)
            extraMonsterCount += count
            if cardInfo["attribute"] in dictData:
                dictData[cardInfo["attribute"]] += count
            else:
                dictData[cardInfo["attribute"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/extraMonsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Extra Deck Monster Attribute","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        dictData = {}
        extraMonsterCount = 0
        for card, count in self.extraDeck.items():
            cardInfo = fetcher.requestCard(card)
            extraMonsterCount += count
            if cardInfo["race"] in dictData:
                dictData[cardInfo["race"]] += count
            else:
                dictData[cardInfo["race"]] = count
        for category, count in dictData.items():
            tabData.append([category,count,f"{count/extraMonsterCount*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Extra Deck Monster Type","Cards","Percentage"],tablefmt=TABLE_FMT))

        tabData = []
        archetypes = self.archetypes()
        sorted_archetypes = list(archetypes.items())
        sorted_archetypes.sort(key=lambda k:k[1],reverse=True)
        for aName, count in sorted_archetypes:
            tabData.append([aName,count,f"{count/self.totalCount()*100:.1f}%"])
        print(tabulate.tabulate(tabData,headers=["Archetype","Cards","Percentage"],tablefmt=TABLE_FMT))

    def approximateDrawProbability(self,checkFunction:Callable[[list[str]],bool],drawSize:int = 5,tests:int = 100000):
        successCount = 0
        for _ in range(tests):
            sampleDeck = []
            for name, count in self.mainDeck.items():
                for _ in range(count):
                    sampleDeck.append(name)
            output = []
            for _ in range(drawSize):
                drawOutput = random.choice(sampleDeck)
                output.append(drawOutput)
                sampleDeck.remove(drawOutput)
            if checkFunction(output):
                successCount += 1
        
        return successCount/tests

    def atLeastOneOf(hand:list[str],cardList:list[str]) -> bool:
        for card in cardList:
            if card in hand:
                return True
        return False
    
    def onlyOf(hand:list[str],cardList:list[str]) -> bool:
        for card in hand:
            if card not in cardList:
                return False
        return True
    
    #MONSTER
    def atLeastOneOfAttribute(hand:list[str],attributeList:list[str]) -> bool:
        for card in hand:
            cardInfo = fetcher.requestCard(card)
            if "attribute" in cardInfo and cardInfo["attribute"] in attributeList:
                return True
        return False

    def atLeastOneOfCardType(hand:list[str],cardTypeList:list[str]) -> bool:
        for card in hand:
            cardInfo = fetcher.requestCard(card)
            for cardType in cardTypeList:
                if "type" in cardInfo and cardType in cardInfo["type"].split():
                    return True
        return False

    def testsFromFile(self,file:str,scriptDir:str|None=None,turns:int = 2,simulations:int = 100000,testCategory:str = "") -> dict[str,list[float]]:
        retDict:dict[str,float] = {}
        tabData = []
        with open(file,"rb") as f:
            tests = tomllib.load(f)
        testNumber = 0
        for testName, checklists in tests.items():
            displayName = displayName = checklists["display_name"] if "display_name" in checklists else testName

            testNumber += 1
            testScript:Callable[[list[str]],bool] = None
            if "python_script" in checklists:
                customScript = SourceFileLoader(checklists["python_script"],scriptDir+"/"+checklists["python_script"]+".py").load_module()
                testScript = customScript.test
            else:
                def checkHandFunction(hand:list[str]) -> bool:
                    checkRes = []
                    if "at_least_one_of" in checklists:
                        checkRes.append(Deck.atLeastOneOf(hand,checklists["at_least_one_of"]))
                    if "none_of" in checklists:
                        checkRes.append(not Deck.atLeastOneOf(hand,checklists["none_of"]))
                    if "only_of" in checklists:
                        checkRes.append(Deck.onlyOf(hand,checklists["only_of"]))
                    if "at_least_one_of_attribute" in checklists:
                        checkRes.append(Deck.atLeastOneOfAttribute(hand,checklists["at_least_one_of_attribute"]))
                    if "none_of_attribute" in checklists:
                        checkRes.append(not Deck.atLeastOneOfAttribute(hand,checklists["none_of_attribute"]))
                    if "at_least_one_of_card_type" in checklists:
                        checkRes.append(Deck.atLeastOneOfCardType(hand,checklists["at_least_one_of_card_type"]))
                    if "none_of_card_type" in checklists:
                        checkRes.append(not Deck.atLeastOneOfCardType(hand,checklists["none_of_card_type"]))
                    
                    if checklists["join_type"] == "and":
                        return not (False in checkRes)
                    elif checklists["join_type"] == "or":
                        return True in checkRes
                testScript = checkHandFunction
                
            newTabDataLine = []
            for turn in range(turns):
                print(f"\r\033[KTesting... {testNumber}/{len(tests)} ({displayName}, Turn {turn+1})",end="")
                probability = self.approximateDrawProbability(testScript,5+turn,simulations)
                newTabDataLine.append(f"{probability*100:.1f}%")

            

            tabData.append([displayName]+newTabDataLine)
            retDict[testName] = newTabDataLine
        print("\r\033[K",end="")
        print(tabulate.tabulate(tabData,headers=[f"{testCategory} Test"]+[f"Turn {i+1}" for i in range(turns)],tablefmt=TABLE_FMT))
        return retDict

    def testHands(self,turns:int = 2,simulations:int = 100000):
        outcomes:dict[str,list[int]] = {}
        for card in self.mainDeck.keys():
            outcomes[card] = [0 for i in range(turns)]
        for turn in range(turns):
            print(f"\r\033[KTesting opening hands... Turn {turn+1}",end="")
            drawSize = 5+turn
            for _ in range(simulations):
                sampleDeck = []
                for name, count in self.mainDeck.items():
                    for _ in range(count):
                        sampleDeck.append(name)
                thisHand = set()
                for _ in range(drawSize):
                    drawOutput = random.choice(sampleDeck)
                    sampleDeck.remove(drawOutput)
                    thisHand.add(drawOutput)
                for card in thisHand:
                    outcomes[card][turn] += 1
        tabData = []
        for card, countList in outcomes.items():
            tabData.append([card]+[f"{x*100/(simulations):.1f}%" for i,x in enumerate(countList)])
        tabData.sort(key=lambda x:x[turns],reverse=True)
        print("\r\033[K",end="")
        print(tabulate.tabulate(tabData,headers=["Card Name"]+[f"Turn {t+1}" for t in range(turns)],tablefmt=TABLE_FMT))
        return outcomes
            
            


            

            
                    
                

