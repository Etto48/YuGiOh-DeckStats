from YGOProb import handtraps as ht

def test(hand:list[str]) -> bool:
    for card in hand:
        if card not in ht.handtraps:
            return False
    return True