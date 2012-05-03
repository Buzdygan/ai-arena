#include <iostream>
#include <sstream>
#include <time.h>
#include <stdlib.h>

#define MIN_BET 10
#define MAX_BET 200

#define CARD_COUNT 5

#define ROUNDS_COUNT 200

using namespace std;

bool readBet(int player, int message, int * bet){
    string line;
    //cerr << "sending " << "[" << player << "] " << message << "\n";
    cout << "[" << player << "] " << message << "\n";
    getline(cin, line);
    //cerr << "received " << line << "\n";
    return (stringstream(line) >> *bet);
}

int decisionMaker(int * bets){
    if(bets[1] < bets[2])
        return 1;
    if(bets[2] < bets[1])
        return 2;
    return 0;
}

int opponent(int player){
    return 3 - player;
}

bool readBets(int mes1, int mes2, int * bets, bool secondRound){
    readBet(1, mes1, bets+1);
    readBet(2, mes2, bets+2);
    //cerr << "BETS1 " << bets[1] << " " << bets[2] << "\n";
    int dm = decisionMaker(bets);
    int trash;
    if(dm){
        int op = opponent(dm);
        readBet(dm, bets[op], bets);
        if(bets[0]){
            readBet(op, bets[dm], &trash);
            readBet(op, 1, &trash);
            bets[dm] = bets[op];
            bets[0] = 0;
        }else{
            readBet(op, bets[dm], &trash);
            readBet(op, 0, &trash);
            bets[0] = op;
        }
    }else{
        bets[0] = 0;
        readBet(1, bets[2], &trash);
        readBet(2, bets[1], &trash);
    }
    return true;
}

int main(){
    int bets[3];
    int scores[3];
    int actualBet=0,
        pl1card=0,
        pl2card=0;
    int decision=0;
    int trash=0;
    int winner=0;

    int sum1=0, sum2=0;

    bets[0] = bets[1] = bets[2] = 0;
    scores[0] = scores[1] = scores[2] = 0;

    for(int i=0; i<ROUNDS_COUNT; i++){
        pl1card = rand() % CARD_COUNT;
        pl2card = rand() % CARD_COUNT;
        sum1 += pl1card;
        sum2 += pl2card;
        //cerr << "CARDS " << pl1card << " " << pl2card << "\n";
        winner = 0;
        actualBet = 0;
        if(pl1card > pl2card)
            winner = 1;
        if(pl2card > pl1card)
            winner = 2;
        //cerr << "first BET\n";
        readBets(pl1card, pl2card, bets, false);
        actualBet = min(bets[1], bets[2]);
        if(bets[0])
            winner = bets[0];
        else{
            //cerr << "second BET\n";
            readBets(bets[2], bets[1], bets, true);
            actualBet += min(bets[1], bets[2]);
            if(bets[0])
                winner = bets[0];
            else{
                readBet(1, pl2card, bets);
                readBet(2, pl1card, bets);
            }
        }

        if(winner)
            scores[winner] += actualBet;
    }

    cerr << "sum of cards " << sum1 << " " << sum2 << "\n";
    cerr << "scores " << scores[1] << " " << scores[2] << "\n";

    cout << "[0]END\n";
    if(scores[1] > scores[2])
        cout << "[2, 0]\n";
    if(scores[2] > scores[1])
        cout << "[0, 2]\n";
    if(scores[1] == scores[2])
        cout << "[1, 1]\n";

    return 0;
}
