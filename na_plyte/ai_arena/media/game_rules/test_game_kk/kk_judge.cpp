#include <iostream>
#define N 3
#define M 3
#define K 3
#define DEBUG

using namespace std;

int endGame(void);
void makeMove(int, int);
void printBoard(void);

char board[N][M];
bool ruch;
string TAG = "Sedzia: ";

