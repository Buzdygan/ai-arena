#!/usr/bin/puthon
# Filename: nadzorca.py

import subprocess
import shlex
import os

class Game:
    memory_limit = 50  # Memory limit in MB
    time_limit = 600	# Time limit in seconds
    judge_path = None	# The binary file of the judge 
	
    def __init__(self, mem_limit=None, t_limit=None, j_path=None):
        if mem_limit:
            self.memory_limit = mem_limit
        if t_limit:
            self.time_limit = t_limit
        if j_path:
            self.judge_path = j_path

    def set_limits(self, mem_limit=None, t_limit=None):
        if mem_limit:
            self.memory_limit = mem_limit
        if t_limit:
            self.time_limit = t_limit

    def set_judge(self, j):
        self.judge_path = j

class Bot:
    filepath = None

    def __init__(self, fpath=None):
        if fpath:
            self.filepath = fpath

    def set_filepath(self, fpath):
        self.filepath = fpath


def parse_response(response, player):
    return "[" + str(player) + "]" + response

def get_players(to_send):
    return map(lambda x:int(x), to_send[1:].split(']')[0].split(','))

def get_message(to_send):
    return to_send.split(']')[1]


"""
	ListOfBots is a list of objects of class Bot.
	Bots are meant to know where is theirs executable file is located.

	Game, according to the description above knows its limits and the judge, 
	which is an executable file
"""
def play(list_of_bots, game):
    print('cos')
    judge_process = subprocess.Popen(
            args=game.judge_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
	
    print("przed")
    l = judge_process.stdout.read()
    print l
    
    bots_process_list = []
    mem_lim = "ulimit -v %d" % (game.memory_limit)
    time_lim = "ulimit -t %d" % (game.time_limit)
    for bot in list_of_bots:
        arg_to_execute = "ulimit -v %d -t %d ; ./%s" % (game.memory_limit * 1024, game.time_limit, bot.filepath)
        bot_process = subprocess.Popen(
                args = arg_to_execute,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell=True,
                )
        bot_process_out = bot_process.stdout.read()
        bots_process_list.append(bot_process)
    print("alamakota")
    end_game = False;
    while not end_game:
        to_send = judge_process.stdout.read()
        list_players_to_send = get_players(to_send)
        message = get_message(to_send)
        print(message)
        if message == "END GAME":
            end_game = True
            break
        for player in list_players_to_send:
            list_of_bots[player].stdin.write(message)
            response = list_of_bots[player].stdout.read()
            list_of_responses.append(parse_response(response, player))
        for response in list_of_responses:
            judge_process.stdin.write(response)
		"""
			komunikacja od Botow idzie do sedziego
			Komunikacja od sedziego trzeba sparsowac i rozeslac do odpowiednich ziomow
		"""
