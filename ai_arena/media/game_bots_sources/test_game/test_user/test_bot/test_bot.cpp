#include <iostream>
#include <string>
#include <sstream>

using namespace std;

int main(){
    string board;
    int i = 0;
    ostringstream ss;
    string str;

    while (true){
//        cerr << "oczekiwanie na input" <<endl;
        cin >> board;
        i = 0;
        while (i < board.length()-3 && board[i] != '0')
            i++;
        if(i >= board.length()-3)
            return 0;
        cerr << "send move " << i << '\n';
        ss << i;
        str = ss.str();
        cout << i << "<<<\n";
    }

    return 0;
}
