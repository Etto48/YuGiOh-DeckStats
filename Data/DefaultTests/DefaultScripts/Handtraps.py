from YuGiOhDeckStats import handtraps as ht

def test(hand:list[str]) -> bool:
    for card in hand:
        if card in ht.handtraps:
            return True
    return False