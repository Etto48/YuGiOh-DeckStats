import time
import tabulate
import os
import requests
from . import cardmarket

TABLE_FMT = "rounded_outline"

class CollectionEntry:
    def __init__(self,count:int,card_number:str,conditions:str):
        self.count = count
        conservation_levels = ["MT","NM","EX","GD","LP","PL","PO"]
        if conditions not in conservation_levels:
            raise ValueError("conditions must be one of MT, NM, EX, GD, LP, PL, PO")
        self.conditions = conditions
        self.code = card_number
        self.price = None
        self.card_name = None
    def getPriceAndName(self,session:requests.Session=None) -> tuple[float,float,str]:
        if self.price is None:
            min_price, avg_price, name = cardmarket.requestCard(card_number=self.code,conservation=self.conditions,session=session)
            self.price = (min_price, avg_price)
            self.card_name = name
        else:
            (min_price, avg_price, name) = (self.price[0], self.price[1], self.card_name)
        return self.count*min_price, self.count*avg_price, name



class Collection:
    def __init__(self):
        self.cards:list[CollectionEntry] = []
    def from_file(file:str):
        ret = Collection()
        lines:list[str] = []
        with open(file,"r") as f:
            lines = f.readlines()
        for i,l in enumerate(lines):
            try:
                if l[0] == "#" or l[0] == "\n":
                    continue
                count = int(l.split()[0])
                card_number = l.split()[1].upper()
                conditions = "NM"
                if len(l.split()) == 3:
                    conditions = l.split()[2]
                ret.cards.append(CollectionEntry(count,card_number,conditions))
            except Exception as e:
                e.add_note(f"File \"{os.path.abspath(file)}\", line {i+1}")
                raise e
        return ret
    def summary(self):
        tabData:list[tuple[str,str,float,float]] = []
        min_sum = 0
        avg_sum = 0

        current_card = 0
        session = requests.Session()
        for card in self.cards:
            print(f"\r\033[K{current_card}/{len(self.cards)}, ETA: {max((len(self.cards)-current_card)/15*60,0):.1f}s",end="")
            min_price, avg_price, name = card.getPriceAndName(session)
            min_sum += min_price
            avg_sum += avg_price
            tabData.append([name,card.count,card.code,card.conditions,min_price,avg_price])
            current_card+=1
        tabData.sort(key=lambda x:x[-1]/x[1],reverse=True)
        print("\r\033[K",end="")
        print(tabulate.tabulate(tabData,headers=["Name","Count","Card Number","Conditions","Min Price","Avg Price"],tablefmt=TABLE_FMT))
        print(tabulate.tabulate([["Min Price",min_sum],["Avg Price",avg_sum]],headers=["Total","Price"],tablefmt=TABLE_FMT))
    
