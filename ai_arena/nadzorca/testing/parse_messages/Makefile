all: parse_messages_judge parse_messages_bot

timeout_judge: parse_messages_judge.cpp
	g++ parse_messages_judge.cpp -O0 -o parse_messages_judge

timeout_bot: parse_messages_bot.cpp
	g++ parse_messages_bot.cpp -O0 -o parse_messages_bot

clean:
	rm parse_messages_judge parse_messages_bot

