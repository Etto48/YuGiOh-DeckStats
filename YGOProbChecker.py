import sys
import os
import argparse
import tabulate
from YGOProb import deck
from YGOProb import fetcher

programDir = os.path.dirname(__file__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        "Explore the stats of your Yu-Gi-Oh deck and perform highly customizable statistical tests")
    main_task = parser.add_mutually_exclusive_group(required=True)

    main_task.add_argument("--dir",dest="dir",type=str,required=False,help=
        "The directory where the deck data is stored. "
        "At least a decklist is needed inside it in the "
        "form of a .txt/.ydk file, you can also provide a .toml "
        "file with some statistical tests to run on the starting hand")

    main_task.add_argument("--file",dest="file",type=str,required=False,help=
        "The file (.txt/.ydk) containing the decklist to analyze with the default tests")

    main_task.add_argument("--info",dest="info",type=str,required=False,help=
        "The exact name of the card you want to show information about")
    
    parser.add_argument("--turns",dest="turns",type=int,required=False,default=2,help=
        "How many turns to simulate during the statistical tests (only needed if --dir is used)")
    parser.add_argument("--simulations",dest="simulations",type=int,required=False,default=100000,help=
        "How many instances are simulated during the statistical tests (more are better, and slower) "
        "(only needed if --dir is used)")

    args = parser.parse_args()

    if args.dir is not None or args.file is not None:
        decklist = None
        decktests = None
        deckscripts = None
        if args.dir is not None:
            assert os.path.isdir(args.dir)
            deckFiles = os.listdir(args.dir)    
            for file in deckFiles:
                filepath = args.dir+"/"+file
                if os.path.isfile(filepath):
                    assert len(os.path.splitext(filepath)) == 2
                    if os.path.splitext(filepath)[1] == ".txt" or os.path.splitext(filepath)[1] == ".ydk":
                        decklist = filepath
                    elif os.path.splitext(filepath)[1] == ".toml":
                        decktests = filepath
                elif os.path.isdir(filepath):
                    if os.path.basename(filepath) == "Scripts":
                        deckscripts = filepath
        elif args.file is not None:
            decklist = args.file
        
        loadedDeck = deck.Deck.fromFile(decklist)
        loadedDeck.summary()
        defaultDecktests = programDir+"/Data/DefaultTests/DefaultTests.toml"
        defaultDeckscripts = programDir+"/Data/DefaultTests/DefaultScripts"
        loadedDeck.testsFromFile(defaultDecktests,defaultDeckscripts,args.turns,args.simulations,"Default")
        if decktests is not None:
            loadedDeck.testsFromFile(decktests,deckscripts,args.turns,args.simulations,"Custom")

    elif args.info is not None:
        cardId = int(args.info) if args.info.isdecimal() else args.info
        cardInfo = fetcher.requestCard(cardId)
        tabData = [["Name",cardInfo["name"]]]
        if "monster" in cardInfo["type"].lower():
            tabData.append(["Attribute",cardInfo["attribute"]])
            if "xyz" in cardInfo["type"].lower():
                tabData.append(["Rank",cardInfo["level"]])
            elif "link" in cardInfo["type"].lower():
                tabData.append(["Link Markers",", ".join(cardInfo["linkmarkers"])])
            else:
                tabData.append(["Level",cardInfo["level"]])
            if "pendulum" in cardInfo["type"].lower():
                tabData.append(["Scale",cardInfo["scale"]])
        tabData.append(["Card Type", f"{cardInfo['race']} {cardInfo['type']}"])
        tabData.append(["Description",cardInfo["desc"]])
        if "monster" in cardInfo["type"].lower():
            tabData.append(["ATK",cardInfo["atk"]])
            if "link" not in cardInfo["type"].lower():
                tabData.append(["DEF",cardInfo["def"]])
            else:
                tabData.append(["Link",cardInfo["linkval"]])
        tabData.append(["ID",cardInfo["id"]])
        print(tabulate.tabulate(tabData,tablefmt="rounded_grid",maxcolwidths=[None, 30]))
         

