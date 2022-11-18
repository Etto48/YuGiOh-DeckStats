import argparse
from YuGiOhDeckStats import collection

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=
        "Keep yourself updated about the value of your YuGiOh Collection")
    parser.add_argument("--file",dest="file",required=True,help=
        "The file containing the collection, each line of this file must be in the format <Count> <Card Number> [Conditions]")

    args = parser.parse_args()

    c = collection.Collection.from_file(args.file)
    c.summary()
