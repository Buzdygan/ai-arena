#include <iostream>
#include <string>

using namespace std;

int main(){
    string board;
    int i = 0;

    while (true){
        cin >> board;
        i = 0;
        while (board[i] != '0')
            i++;
        cout << i;
    }

    return 0;
}
