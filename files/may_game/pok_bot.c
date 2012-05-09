#include <stdio.h>
#include <time.h>

#define CONFIRM printf("0\n");
#define WAIT scanf("%d", &trash);

int firstBet(int card){
    int bet = 10;
    if(card > 1)
        bet = 100;
    if(card == 4)
        bet = 200;
    return bet;
}

int secondBet(int my1bet, int op1bet, int card){
    if(card == 4)
        return 200;
    if(card > 1)
        return 120;
    if(op1bet > my1bet)
        return 10;
    return 50;
}

int decision(int myBet, int opBet, int card){
    if(card < 2)
        return 0;
    if((card == 2)&&(2*myBet > opBet))
        return 1;
    if(card > 2)
        return 1;
    return 0;
}

int main(){
    int card, my1bet, op1bet, bet1, my2bet, op2bet, decision1, decision2, opCard;
    int trash;
    while(1){
        scanf("%d", &card);
        //cerr << "CARD " << card << "\n";
        my1bet = firstBet(card);
        printf("%d\n", my1bet);
        scanf("%d", &op1bet);
        //cerr << "op1bet " << op1bet << "\n";
        if(op1bet > my1bet){
            decision1 = decision(my1bet, op1bet, card);
            //cerr << "making decision " << decision1 << "\n";
            printf("%d\n", decision1);
            if(decision1 == 0)
                continue;
        }
        if(my1bet > op1bet){
            CONFIRM;
            scanf("%d", &decision1);
            //cerr << "op made decision " << decision1 << "\n";
            CONFIRM;
            if(decision1 == 0){
                continue;
            }
        }
        if(my1bet == op1bet){
            CONFIRM;
            //cerr << "equal 1bet\n";
        }

        //SECOND BET
        scanf("%d", &bet1);
        //cerr << "1bet for " << bet1 << "\n";
        my2bet = secondBet(my1bet, op1bet, card);
        printf("%d\n", my2bet);
        scanf("%d", &op2bet);
        if(op2bet > my2bet){
            decision2 = decision(my1bet+my2bet, op1bet+op2bet, card);
            printf("%d\n", decision2);
            if(decision2 == 0)
                continue;
        }
        if(my2bet > op2bet){
            CONFIRM;
            scanf("%d", &decision2);
            CONFIRM;
            if(decision2 == 0)
                continue;
        }
        if(my2bet == op2bet){
            CONFIRM;
            //cerr << "equal 2bet\n";
        }
        scanf("%d", &opCard);
        CONFIRM;
    }

    return 0;
}
