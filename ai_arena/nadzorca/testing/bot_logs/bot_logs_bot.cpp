#include <iostream>
#include <time.h>

using namespace std;

int main(){
    long long int a = 0;
    int move = 1;
    string s;
    while(true){
        getline(cin, s);
        cerr << move;
        cout << move << " <<<\n";
        cerr << move;
        if(move < 10)
            move++;
    }

    return 0;
}
