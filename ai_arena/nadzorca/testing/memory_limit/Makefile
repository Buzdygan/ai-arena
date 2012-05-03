all: memory_limit_judge memory_limit_bot

timeout_judge: memory_limit_judge.cpp
	g++ memory_limit_judge.cpp -O0 -o memory_limit_judge

timeout_bot: memory_limit_bot.cpp
	g++ memory_limit_bot.cpp -O0 -o memory_limit_bot

clean:
	rm memory_limit_judge memory_limit_bot

