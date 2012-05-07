#include <iostream>
#include <sstream>
#include <time.h>
#include <stdlib.h>

#define MIN_BET 10
#define MAX_BET 200

#define CARD_COUNT 5

#define ROUNDS_COUNT 200

#define CHECK 1
#define FOLD 0

using namespace std;

string toSend1, toSend2;
istringstream received1, received2;

int actualBet=0;

void toSend(int pl, int mes){
    stringstream ss;
    ss << mes;
    if(pl == 1){
        if(toSend1 != "")
            toSend1 += " ";
        toSend1 += ss.str();
    }
    if(pl == 2){
        if(toSend2 != "")
            toSend2 += " ";
        toSend2 += ss.str();
    }
}

//TODO obsluga DEAD i return
bool send(int pl){
    string toSend, received;
    if(pl == 1){
        toSend = toSend1;
        toSend1 = "";
    }
    if(pl == 2){
        toSend = toSend2;
        toSend2 = "";
    }
    cerr << "wys " << "[" << pl << "]" << toSend << "\n";
    cout << "[" << pl << "]" << toSend << "\n";
    getline(cin, received);
    cerr << "dost " << received << "\n";
    if(pl == 1){
        received1.clear();
        received1.str(received);
    }
    if(pl == 2){
        received2.clear();
        received2.str(received);
    }
    return true;
}

//TODO obsluga return
bool readMes(int pl, int * mes){
    if(pl == 1)
        return (received1 >> *mes);
    if(pl == 2)
        return (received2 >> *mes);
}

bool readBet(int player, int message, int * bet){
    toSend(player, message);
    send(player);
    return readMes(player, bet);
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

bool readBets(int * bets, bool secondRound){
    if(bets[1] == 0)
        readMes(1, bets+1);
    if(bets[2] == 0)
        readMes(2, bets+2);
    int dm = decisionMaker(bets);
    if(dm){
        int op = opponent(dm);
        toSend(op, bets[dm]);
        readBet(dm, bets[op], bets);
        if(bets[0] > 0){
            bets[dm] = bets[0];
            actualBet += bets[op];
            toSend(op, CHECK);
            if(!secondRound)
            send(op);
            bets[op] = 0;
            bets[0] = 0;
        }else{
            actualBet += bets[dm];
            toSend(op, FOLD);
            bets[0] = op;
        }
    }else{
        actualBet += bets[1];
        bets[0] = 0;
        toSend(1, bets[2]);
        toSend(2, bets[1]);
        bets[1] = bets[2] = 0;
        if(!secondRound){
        send(1);
        send(2);
        }
    }
    return true;
}

int main(){
    int bets[3];
    int scores[3];
    int pl1card=0,
        pl2card=0;
    int decision=0;
    int winner=0;

    int sum1=0, sum2=0;

    scores[0] = scores[1] = scores[2] = 0;

    for(int i=0; i<ROUNDS_COUNT; i++){
        pl1card = rand() % CARD_COUNT;
        pl2card = rand() % CARD_COUNT;
        bets[0] = bets[1] = bets[2] = 0;
        //pl1card = 0;
        //pl2card = 1;
        toSend(1, pl1card);
        toSend(2, pl2card);
        cerr << "sending CARDS " << pl1card << " " << pl2card << "\n";
        send(1);
        send(2);
        sum1 += pl1card;
        sum2 += pl2card;
        winner = 0;
        actualBet = 0;
        if(pl1card > pl2card)
            winner = 1;
        if(pl2card > pl1card)
            winner = 2;
        //cerr << "first BET\n";
        readBets(bets, false);
        if(bets[0])
            winner = bets[0];
        else{
            cerr << "second BET\n";
            readBets(bets, true);
            if(bets[0])
                winner = bets[0];
            else{
                toSend(1, pl2card);
                toSend(2, pl1card);
            }
        }
        cerr << "winner " << winner << " actBet " << actualBet << "\n";
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
