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

        fprintf(stderr, "sending message %s\n", message.c_str());
        cout << message;

        cin >> move;
        fprintf(stderr, "received move %d\n", move);

        if (player1)
            board[move] = '1';
        else
            board[move] = '2';

    } while (board[BOARD_SIZE-1] == '0');

    if(player1)
        fprintf(stderr, "player 1 won\n");
    else
        fprintf(stderr, "player 2 won\n");

    cout << "[0] END GAME";

    return 0;
}
