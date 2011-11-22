#include <iostream>
#include <string>
#include <stdio.h>

using namespace std;

int main(){

    string message, board = "00000";
    int move = 0;

    bool player1 = true;
    do{
        if (player1)
            message = "[1]";
        else
            message = "[2]";
        message += board;

        fprintf(stderr, "sending message %s\n", message.c_str());
        cout << message;

        cin >> move;
        fprintf(stderr, "received move %d\n", move);

        if (player1)
            board[move] = '1';
        else
            board[move] = '2';

        player1 = !player1;
    } while (board[4] == '0');

    if (board[4] == '1')
        fprintf(stderr, "player 1 won\n");

    if (board[4] == '2')
        fprintf(stderr, "player 2 won\n");

    cout << "[0] END GAME";

    return 0;
}
