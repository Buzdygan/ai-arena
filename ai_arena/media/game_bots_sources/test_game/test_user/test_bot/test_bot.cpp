#include <iostream>
#include <string>

using namespace std;

int main(){
    string board;
    int i = 0;

    while (true){
//        cerr << "oczekiwanie na input" <<endl;
        cin >> board;
//        cerr << "otrzymano input" << endl;
        i = 0;
        while (i < board.length() && board[i] != '0')
            i++;
        if(i >= board.length())
            return 0;
        cout << i << "<<<" << endl;
    }

    return 0;
}
