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

int main(){
    string com;
    bool end = false;
    int X, Y;

    for(int i = 0; i < N; ++i)
        for(int j = 0; j < N; ++j)
            board[i][j] = '.';

    ruch = true;
    cout << "[1] START <<<\n";
    cerr << TAG << "[1] START <<<\n";

    while(!end){
        cin >> com;
        if(com == "MOVE"){
            cin >> X >> Y >> com;
            makeMove(X, Y);
            if(endGame() == 0){
                (ruch)?cout<<"[2] ":cout<<"[1] ";
                cout<<"MOVE " << X << " " << Y << " <<<\n";
                cerr << TAG << ((ruch)?"[2] ":"[1] ") << "MOVE "<<X<<" "<<Y<<" <<<\n";
            }
        }

        int endg = endGame();
        if(endg != 0){//end game
            cout << "[0]END<<<\n";
            cerr << TAG <<"[0]END<<<\n";
            if(endg == 3){
                cout << "[0, 0] <<<\n";
                cerr<<TAG << "[0, 0] <<<\n";
            }
            if(endg == 2){
                cout << "[0, 1] <<<\n";
                cerr << TAG << "[0, 1] <<<\n";
            }
            if(endg == 1){
                cout << "[1, 0] <<<\n";
                cerr << TAG << "[1, 0] <<<\n";
            }
            end = true;
        }

        ruch = !ruch;
//        printBoard();
    }

    return 0;
}

void makeMove(int i, int j){
    if(ruch){
        board[i][j] = 'X';
    }else{
        board[i][j] = 'O';
    }
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
        cout << endl;
    }
}
