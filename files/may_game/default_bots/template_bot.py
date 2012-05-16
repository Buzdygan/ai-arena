from sys import stdin, stdout, stderr


def firstBet(myCard):
    return 10 

def secondBet(my1bet, op1bet, card):
    return 50

def firstDecision(myBet, opBet, card):
    return 1

def secondDecision(myBet, opBet, card):
    return 1

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

