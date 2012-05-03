#include <iostream>
#include <sstream>
#include <time.h>

using namespace std;

int main(){
    bool end = false;
    bool firstMoves = true;
    int move = 0;
    string response;

    while(!end){
        cout << (firstMoves ? "[1] " : "[2] ") << "MOVE <<<\n";
        getline(cin, response);
        if(response == "_DEAD_<<<"){
            cerr << "DEAD_BOT";
            usleep(10);
            cout << "[0]END<<<\n";
            cout << "[0, 0]<<<\n";
            end = true;
        }
        else{
            stringstream(response) >> move;
            cerr << move;
        }
        if((move == 5)&&(!end)){
            end = true;
            cout << "[0]END<<<\n";
            if(firstMoves)
                cout << "[1, 0]<<<\n";
            else
                cout << "[0, 1]<<<\n";
        }
        firstMoves = !firstMoves;
    }

    return 0;
}
