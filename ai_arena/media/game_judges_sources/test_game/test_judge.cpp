#include <iostream>
#include <string>
#include <stdio.h>

using namespace std;

int main(){

    const int BOARD_SIZE = 5;
    string message, board = string(BOARD_SIZE, '0');
    int move = 0;
    bool player1 = false;

    do
    {
        player1 = !player1;

        if (player1)
            message = "[1]";
        else
            message = "[2]";
        message += board;

        cerr << "sending message " << message << endl;
        cout << message << "END" << endl;

        cin >> move;
        cerr << "received move " <<  move << endl;

        if (player1)
            board[move] = '1';
        else
            board[move] = '2';

    } while (board[BOARD_SIZE-1] == '0');

    cout << "[0] END" << endl;

    if(player1) {
        cerr << "player 1 won " << endl;
        cout << "[1, 0] END" << endl;
    }
    else {
        cerr << "player 2 won" << endl;
        cout << "[0, 1] END" << endl;
    }
    return 0;
}
