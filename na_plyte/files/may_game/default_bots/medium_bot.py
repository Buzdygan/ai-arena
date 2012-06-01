from sys import stdin, stdout, stderr
from random import *


def firstBet(myCard):

    stake1 = 0
    if myCard == 0: 
        if randint (0,100) < 15:
            # blef
            stake1 = 120 + randint(0,20)
        else:
            stake1 = 20 + randint(0,5)
    elif myCard == 1: 
        stake1 = 45 + randint(0,10)
    elif myCard == 2: 
        stake1 = 60 + randint(0,20)
    elif myCard == 3: 
        stake1 = 80 + randint (0,25)
    elif myCard == 4: 
        stake1 = 100 + randint (0,30)
    else: assert False
    stake1 = min(stake1, 200)
    return stake1

def secondBet(stake1, minStake2, myCard):
    if myCard == 0: stake2 =  min(stake1 + randint(0,12), 200)
    if myCard == 1: stake2 =  min(stake1 + randint(0,25), 200)
    if myCard == 2: stake2 =  min(stake1 + randint(0,50), 200)
    if myCard == 3: stake2 =  min(stake1 + randint(0,100), 200)
    if myCard == 4: stake2 =  200 - randint(0,20)
    stake2 = min(200, stake2)
    stake2 = max(minStake2, stake2)
    return stake2

def firstDecision(stake1, otherStake1, myCard):
    stake1 = max(stake1, otherStake1)
    if otherStake1 <= stake1: 
        return 1 
    if myCard == 0: return int(otherStake1 <= stake1 + 10)
    if myCard == 1: return int(otherStake1 <= stake1 + 20)
    if myCard == 2: return int(otherStake1 <= stake1 + 40)
    if myCard == 3: return int(otherStake1 <= stake1 + 80)
    if myCard == 4: return 1 
    assert False

def secondDecision(stake1, otherStake2, myCard):
    if myCard == 0: return int(otherStake2 <= stake1 * 1.2)
    if myCard == 1: return int(otherStake2 <= stake1 * 1.3)
    if myCard == 2: return int(otherStake2 <= stake1 * 1.5)
    if myCard == 3: return int(otherStake2 <= stake1 * 2)
    if myCard == 4: return 1
    assert False

receivedInts = []
total_score = 0

def takeInt():
    global receivedInts
    if len(receivedInts) == 0:
        receivedInts = map(int, raw_input().split())
    return receivedInts.pop(0)

def log(message):
    stderr.write(message)

def won(stake):
    global total_score
    total_score += stake
    log("Won %d " % stake)
    log("Total score: %d " % total_score)

def lost(stake):
    global total_score
    total_score -= stake
    log("Lost %d " % stake)
    log("Total score: %d " % total_score)

def send(decision):
    stdout.write(str(decision) + "\n")
    stdout.flush()


while True:

    """ First Round """ 

    # Draw card
    card = takeInt()

    # Make first bet
    my1bet = firstBet(card)
    send(my1bet)

    # Learn opponent bet
    op1bet = takeInt()

    # If my bet was lower
    if op1bet > my1bet:
        decision1 = firstDecision(my1bet, op1bet, card)
        # Pass
        if decision1 == 0:
            send(decision1)
            lost(my1bet)
            continue

    # If my bet was higher
    if my1bet > op1bet:
        decision1 = takeInt()
        # Opponent passed
        if decision1 == 0:
            won(op1bet)
            continue

    stake1 = max(my1bet, op1bet)

    """ Second Round """

    # Make second bet
    my2bet = secondBet(my1bet, op1bet, card)
    send(my2bet)

    # Learn opponent bet
    op2bet = takeInt()

    # If my bet was lower
    if op2bet > my2bet:
        decision2 = secondDecision(my1bet+my2bet, op1bet + op2bet, card)
        send(decision2)
        # Pass
        if decision2 == 0:
            lost(stake1 + my2bet)
            continue

    # If my bet was higher
    if my2bet > op2bet:
        decision2 = takeInt()
        # Opponent passed
        if decision2 == 0:
            won(stake1 + op2bet)
            continue

    stake2 = max(my2bet, op2bet)
    final_stake = stake1 + stake2

    # learn opponent card
    opCard = takeInt()
    if opCard == card:
        log('Draw ')
    if opCard > card:
        lost(final_stake)
    if opCard < card:
        won(final_stake) 
