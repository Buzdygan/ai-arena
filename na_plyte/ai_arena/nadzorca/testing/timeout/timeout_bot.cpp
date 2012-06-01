#include <iostream>
#include <time.h>

using namespace std;

int main(){
    long long int a = 0;
    int move = 1;
    string s;
    while(true){
        //sleep(10);
        getline(cin, s);
        if(move == 3)
            while(a < 1000000000){
                a++;
            }
        cout << move << " <<<\n";
        if(move < 10)
            move++;
    }

    return 0;
}
