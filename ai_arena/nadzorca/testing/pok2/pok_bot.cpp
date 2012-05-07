#include <iostream>
#include <time.h>

#define CONFIRM cout << "0\n"
#define WAIT cin >> trash

using namespace std;

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
        cin >> card;
        cerr << "CARD " << card << "\n";
        my1bet = firstBet(card);
        cout << my1bet << "\n";
        cin >> op1bet;
        cerr << "op1bet " << op1bet << "\n";
        if(op1bet > my1bet){
            decision1 = decision(my1bet, op1bet, card);
            cerr << "making decision " << decision1 << "\n";
            if(decision1 == 0){
                cout << decision1 << "\n";
                continue;
            }
        }
        if(my1bet > op1bet){
            cin >> decision1;
            cerr << "op made decision " << decision1 << "\n";
            if(decision1 == 0){
                continue;
            }
        }
        if(my1bet == op1bet){
            cerr << "equal 1bet\n";
        }

        //SECOND BET
        cerr << "second round\n";
        my2bet = secondBet(my1bet, op1bet, card);
        cout << my2bet << "\n";
        cin >> op2bet;
        cerr << "op2bet " << op2bet << "\n";
        if(op2bet > my2bet){
            decision2 = decision(my1bet+my2bet, op1bet+op2bet, card);
            cerr << "making decision " << decision2 << "\n";
            cout << decision2 << "\n";
            if(decision2 == 0)
                continue;
        }
        if(my2bet > op2bet){
            cin >> decision2;
            cerr << "op made decision " << decision2 << "\n";
            if(decision2 == 0)
                continue;
        }
        if(my2bet == op2bet){
            cerr << "equal 2bet\n";
        }
        cin >> opCard;
    }

    return 0;
}
