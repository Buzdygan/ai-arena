#include <iostream>
#define N 3
#define M 3
#define K 3
#define DEBUG

using namespace std;

void printBoard(void);
int endGame(void);


char board[N][M];
bool ruch;
void makeMove(void);

int main(){
    string com;
    bool end = false;

    for(int i = 0; i < N; ++i)
        for(int j = 0; j < M; ++j)
            board[i][j] = '.';

    while(!end){
        cin>>com;
        int X, Y;

        if(com == "MOVE"){
            cin >>X>>Y>>com;
            board[X][Y] = 'O';
            if(endGame() == 0){
                ruch = true;
                makeMove();
            }
        }

        if(com == "START"){
            board[1][1] = 'X';
            cout << "MOVE 1 1 <<<\n";
        }

        if(com == "END"){
            cin >> com;
            end = true;
        }
    }

    return 0;
}

int ocenStan(){
    int endG = endGame();
    if(endG == 0) return 0;
    if(endG == 1) return 1;
    if(endG == 2) return -1;
    if(endG == 3) return 0;
    return 0;
}

int minimax(int depth){
    int ocena = ocenStan();
    if(depth == 0 || ocena != 0){
        return ocena;
    }

    int min = 2, max = -2, temp, X, Y;
    for(int i = 0; i < N; ++i)
        for(int j = 0; j < M; ++j){
            if(board[i][j] == '.'){
                if(ruch)
                    board[i][j] = 'X';
                else
                    board[i][j] = 'O';

                ruch = !ruch;
                temp = minimax(depth-1);
                ruch = !ruch;
                board[i][j] = '.';
                
                if(ruch && temp > max){
                    if(temp == 1){
                        if(depth == 9){
                            cout<<"MOVE "<<i<<" "<<j<<" <<<\n";
                            board[i][j] = 'X';
                        }
                        return 1;
                    }
                    max = temp;
                    X = i; Y = j;
                }
                else if(!ruch && temp < min){
                    if(temp == -1){
                        return -1;
                    }
                    min = temp;
                    X = i; Y = j;
                }
                
            }
        }
    if(min == 2) min = 0;
    if(max == -2) max = 0;
    if(depth == 9){
        cout<<"MOVE "<<X<<" "<<Y<<" <<<\n";
        board[X][Y] = 'X';
    }
    return (ruch)?max:min;
}

void makeMove(){
    int depth = 9;
    minimax(depth);
}

int endGame(){
    bool x[8], y[8];
    for(int i = 0; i < 8; ++i){
        x[i] = true; y[i] = true;
    }

    for(int i = 0; i < N; ++i)
        for(int j = 0; j < N; ++j)
            if(board[i][j] == '.'){
                x[i] = false;
                y[i] = false;
                x[j+N] = false;
                y[j+N] = false;
                if(i == j){
                    x[2*N] = false;
                    y[2*N] = false;
                }
                if(i+j == N-1){
                    x[2*N+1] = false;
                    y[2*N+1] = false;
                }
            }
            else if(board[i][j] == 'X'){
                y[i] = false;
                y[j+N] = false;
                if(i == j) y[2*N] = false;
                if(i+j == N-1) y[2*N+1] = false;
            }
            else{
                x[i] = false;
                x[j+N] = false;
                if(i == j) x[2*N] = false;
                if(i+j == N-1) x[2*N+1] = false;
            }

    for(int i = 0; i < 8; ++i){
        if(x[i]) return 1;
        if(y[i]) return 2;
    }

    for(int i = 0; i < N; ++i)
        for(int j = 0; j < M; ++j)
            if(board[i][j] == '.')
                return 0;
    return 3;
}

void printBoard(){
    for(int i = 0; i < N; ++i){
        for(int j = 0; j < M; ++j)
            cout << board[i][j];
        cout<<endl;
    }
}
