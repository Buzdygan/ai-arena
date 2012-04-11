all: bot_logs_judge bot_logs_bot

timeout_judge: bot_logs_judge.cpp
	g++ bot_logs_judge.cpp -O0 -o bot_logs_judge

timeout_bot: bot_logs_bot.cpp
	g++ bot_logs_bot.cpp -O0 -o bot_logs_bot

clean:
	rm bot_logs_judge bot_logs_bot

