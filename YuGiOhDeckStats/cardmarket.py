import time
import requests
import bs4

BASE_URL = "https://www.cardmarket.com"
SEARCH_URL = BASE_URL+"/en/YuGiOh/Products/Search"
FAIL_TEXT = "Sorry, no matches for your query"

def splitCardCode(card_number:str) -> tuple[str,int,str]:
    langs = [["EN"],["FR"],["DE"],["S"],["IT","I"],["P"]]
    set_code, lang_and_position = card_number.split("-")
    language = 0
    position = 0
    done = False
    for i,l in enumerate(langs):
        for l_code in l:
            if l_code in lang_and_position:
                language = i
                position = lang_and_position.removeprefix(l_code)
                done = True
                break
        if done:
            break
    return (set_code,language+1,position)

def priceToFloat(price_eur:str) -> float:
    split_data = price_eur.split()
    num = split_data[0].replace(",",".")
    price = float(num)
    return price

def requestCard(card_number:str,conservation:str,session:requests.Session=None) -> tuple[float,float]:
    conservation_levels = ["MT","NM","EX","GD","LP","PL","PO"]
    headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
    if session is None:
        session = requests.Session()
    while True:
        response = session.get(url=SEARCH_URL,params={"searchString":card_number},headers=headers,allow_redirects=False)
        if response.status_code == 200: #not found
            raise ValueError(FAIL_TEXT+f" ({card_number})")
        if response.status_code == 429: #too many requets
            time.sleep(int(response.headers["retry-after"]))
        else:
            break
    try:
        set_code, language, position = splitCardCode(card_number)
        condition = conservation_levels.index(conservation)+1
        final_res = session.get(url=BASE_URL+response.headers["location"],params={"language":language,"minCondition":condition},headers=headers)
        bs = bs4.BeautifulSoup(final_res.text,features="html.parser")
        price_table = bs.find(name="dl")
        min_price = price_table.find(name="dt",text="From").find_next_sibling(name="dd").contents[0]
        avg_price = price_table.find(name="dt",text="30-days average price").find_next_sibling(name="dd").find(name="span").contents[0]
        name = bs.find("h1").contents[0]
    except Exception as e:
        e.add_note(f"HTTP response:{final_res.status_code}, CN:{card_number}")
        raise e
    return priceToFloat(min_price), priceToFloat(avg_price), name

if __name__ == "__main__":
    card = input()
    print(requestCard(card,"NM"))
    