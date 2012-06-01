#include <iostream>
#include <sstream>
#include <time.h>
#include <stdlib.h>

#define MIN_BET 10
#define MAX_BET 200

#define CARD_COUNT 5

#define ROUNDS_COUNT 2

#define CALL 1
#define FOLD 0

using namespace std;

string toSend[3];
int receivedMes[3];
bool communicate = true;

int actualBet = 0;

void error(int pl, string info){
    if(communicate){
        cerr << "ERRRORR: player " << pl << " " << info << "\n";
        cerr << "wys " << "[" << pl << "]KILL\n";
        cout << "[" << pl << "]KILL\n";
        cout << "[0]END\n";
        if(pl == 1)
            cout << "[0, 2]\n";
        else
            cout << "[2, 0]\n";
    }
    communicate = false;
}

void buffer(int pl, int mes){
    stringstream ss;
    ss << mes;
    if(toSend[pl] != "")
        toSend[pl] += " ";
    toSend[pl] += ss.str();
}

void send(int pl){
    string mes, received;
    mes = toSend[pl];
    toSend[pl] = "";
    if(communicate){
        cerr << "wys " << "[" << pl << "]" << mes << "\n";
        cout << "[" << pl << "]" << mes << "\n";
        getline(cin, received);
        cerr << "dost " << received << "\n";
    }
    if(received == "_DEAD_")
        error(pl, "dead");
    else{
        istringstream ss(received);
        int num;
        if((ss >> num).fail())
            error(pl, "NaN");
        else
            receivedMes[pl] = num;
    }            
}

void readMes(int pl, int& mes, int min, int max, bool maybe0){
    int num = receivedMes[pl];
    if(((num >= min) && (num <= max)) || (maybe0 && (num == 0))){
        mes = num;
        receivedMes[pl] = -1;
    }else
        error(pl, "mes out of range");
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

bool readBets(int * bets, bool firstRound){
    for(int pl=1; pl <= 2; pl++)
        if(bets[pl] == 0)
            readMes(pl, bets[pl], MIN_BET, MAX_BET, false);
    for(int pl=1; pl <= 2; pl++)
        buffer(opponent(pl), bets[pl]);
    int dm = decisionMaker(bets);
    if(dm){
        int op = opponent(dm);
            send(dm);
        int response;
        if(firstRound)
            readMes(dm, response, MIN_BET, MAX_BET, true);
        else
            readMes(dm, response, 0, 1, true);
        if(response > 0){
            buffer(op, CALL);
            if(firstRound){
                send(op);
                bets[dm] = response;
            }
            actualBet += bets[op];
            bets[op] = 0;
            bets[0] = 0;
        }else{
            actualBet += bets[dm];
            buffer(op, FOLD);
            bets[0] = op;
        }
    }else{
        actualBet += bets[1];
        bets[0] = 0;
        for(int pl=1; pl <= 2; pl++)
            bets[pl] = 0;
        if(firstRound)
            for(int pl=1; pl <= 2; pl++)
                send(pl);
    }
    return true;
}

int main(){
    for(int i=0; i < 3; i++){
        toSend[i] = "";
        receivedMes[i] = -1;
    }
    int bets[3];
    int scores[3];
    int pl1card=0,
        pl2card=0;
    int decision=0;
    int winner=0;

    int sum1=0, sum2=0;

    scores[0] = scores[1] = scores[2] = 0;

    srand(getpid() + time(NULL));

    for(int i=0; i<ROUNDS_COUNT; i++){
        pl1card = rand() % CARD_COUNT;
        pl2card = rand() % CARD_COUNT;
        for(int i=0; i < 3; i++)
            bets[i] = 0;
        buffer(1, pl1card);
        buffer(2, pl2card);
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
        readBets(bets, true);
        if(bets[0])
            winner = bets[0];
        else{
            cerr << "second BET\n";
            readBets(bets, false);
            if(bets[0])
                winner = bets[0];
            else{
                buffer(1, pl2card);
                buffer(2, pl1card);
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
