#include <stdio.h>
#include <time.h>

#define false 0
#define true 1

#define CONFIRM printf("0\n");fflush(stdout)
#define WAIT scanf("%d", &trash)

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
    while(true){
        scanf("%d", &card);
        fprintf(stderr, "CARD %d\n", card);
        my1bet = firstBet(card);
        printf("%d\n",my1bet);
        fflush(stdout);
        scanf("%d",&op1bet);
        fprintf(stderr,"op1bet %d\n", op1bet);
        if(op1bet > my1bet){
            decision1 = decision(my1bet, op1bet, card);
            fprintf(stderr, "making decision %d\n", decision1);
            if(decision1 == 0){
                printf("%d\n", decision1);
                fflush(stdout);
                continue;
            }
        }
        if(my1bet > op1bet){
            scanf("%d", &decision1);
            fprintf(stderr, "op made decision %d\n", decision1);
            if(decision1 == 0){
                continue;
            }
        }
        if(my1bet == op1bet){
            fprintf(stderr,"equal 1bet\n");
        }

        //SECOND BET
        fprintf(stderr, "second round\n");
        my2bet = secondBet(my1bet, op1bet, card);
        printf("%d\n", my2bet);
        fflush(stdout);
        scanf("%d", &op2bet);
        fprintf(stderr, "op2bet %d\n", op2bet);
        if(op2bet > my2bet){
            decision2 = decision(my1bet+my2bet, op1bet+op2bet, card);
            fprintf(stderr, "making decision %d\n", decision2);
            printf("%d\n", decision2);
            fflush(stdout); 
            if(decision2 == 0)
                continue;
        }
        if(my2bet > op2bet){
            scanf("%d", &decision2);
            fprintf(stderr, "op made decision %d\n", decision2);
            if(decision2 == 0)
                continue;
        }
        if(my2bet == op2bet){
            fprintf(stderr, "equal 2bet\n");
        }
        scanf("%d", &opCard);
    }

    return 0;
}
