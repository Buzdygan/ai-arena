from sys import stdin, stdout, stderr

def firstBet(card):
    bet = 10
    if card > 1:
        bet = 100
    if card == 4:
        bet = 200
    return bet

def secondBet(my1bet, op1bet, card):
    if card == 4:
        return 200
    if card > 1:
        return 100
    if op1bet > my1bet:
        return 10
    return 50

def decision(myBet, opBet, card):
    if card < 2:
        return 0
    if (card == 2) and (2*myBet > opBet):
        return 1
    if card > 2:
        return 1
    return 0

receivedInts = []

def takeInt():
    global receivedInts
    if len(receivedInts) == 0:
        receivedInts = map(int, raw_input().split())
    return receivedInts.pop(0)


while True:
    card = takeInt()
    stderr.write("CARD " + str(card) + "\n")
    my1bet = firstBet(card)
    stdout.write("" + str(my1bet) + "\n")
    stdout.flush()
    op1bet = takeInt()
    stderr.write("op1bet " + str(op1bet) + "\n")
    if op1bet > my1bet:
        decision1 = decision(my1bet, op1bet, card)
        stderr.write("making decision " + str(decision1) + "\n")
        if decision1 == 0:
            stdout.write(str(decision1) + "\n")
            stdout.flush()
            continue
    if my1bet > op1bet:
        decision1 = takeInt()
        stderr.write("op made decision " + str(decision1) + "\n")
        if decision1 == 0:
            continue
    if my1bet == op1bet:
        stderr.write("equal 1bet\n")

        # Second bet
    stderr.write("Second round \n")
    my2bet = secondBet(my1bet, op1bet, card)
    stdout.write(str(my2bet) + "\n")
    stdout.flush()
    op2bet = takeInt()
    stderr.write("op2bet " + str(op2bet) + "\n")
    if op2bet > my2bet:
        decision2 = decision(my1bet+my2bet, op1bet + op2bet, card)
        stderr.write("making decision " + str(decision2) + "\n")
        stdout.write(str(decision2) + "\n")
        stdout.flush()
        if decision2 == 0:
            continue
    if my2bet > op2bet:
        decision2 = takeInt()
        stderr.write("op made decision " + str(decision2) + "\n")
        if decision2 == 0:
            continue
    if my2bet == op2bet:
        stderr.write("equal 2bet\n")
    opCard = takeInt()

