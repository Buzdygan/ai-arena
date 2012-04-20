all: timeout_judge timeout_bot

timeout_judge: timeout_judge.cpp
	g++ timeout_judge.cpp -O0 -o timeout_judge

timeout_bot: timeout_bot.cpp
	g++ timeout_bot.cpp -O0 -o timeout_bot

clean:
	rm timeout_judge timeout_bot

