all: pok_judge pok_bot

timeout_judge: pok_judge.cpp
	g++ pok_judge.cpp -O0 -o pok_judge

timeout_bot: bot_logs_bot.cpp
	g++ pok_bot.cpp -O0 -o pok_bot

clean:
	rm pok_judge pok_bot

