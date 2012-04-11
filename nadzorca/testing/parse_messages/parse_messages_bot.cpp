#include <iostream>
#include <time.h>

using namespace std;

int main(){
    int move = 1;
    while(move < 1000000000){
        cerr << move;
        cout << move << " <<<\n";
        move++;
    }

    return 0;
}
