#!/usr/bin/python
# Filename: nadzorca.py
import subprocess
import os
import tempfile
import sys
import threading
import Queue
import time

class Game2:
    memory_limit = 50  # Memory limit in MB
    time_limit = 600	# Time limit in seconds
    judge_path = None	# The binary file of the judge 
	
    def __init__(self, j_path=None, mem_limit=None, t_limit=None):
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


def parse_response(response, player):
        return "[" + str(player) + "]" + response


"""
This function parses a message from judge returning list of players as a first of pair
and an actual message as a second of pair

Every message coming here must comtain a list of players in brackets like these: '[' and ']'.
It can contain multiple of any of them, in this case the first pair is treated as a list of players.
"""
def parse_message(to_send):
    l = to_send.split(']')
    players = map(lambda x:int(x), l[0][1:].split(','))
    mes = l[1]
    for t in l[2:]:
        mes += ']' + t
    return (players,mes)

"""
This function reads communicates.
The assumption is that every communicate ends with chars 'END\n' not case-sensitive
In addition every 'END\n' frase is considered to be end of a communicate
"""
# TODO: Add timeout!
def readout(pipe, timeout=0):
    mes = ''
    while mes[len(mes)-3:].upper() != 'END':
        mes = mes + pipe.read(1)
    pipe.read(1)
    return mes[:len(mes)-3]

"""
	ListOfBots is a list of objects of class Bot.
	Bots are meant to know where is theirs executable file is located.

	Game, according to the description above knows its limits and the judge, 
	which is an executable file
"""
def play(match):
    to_execute = "./%s" % match.game.judge_file
    jp = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
#            stderr=subprocess.PIPE,
            shell=True,
            )
    
    bots_process_list = []
    for bot in match.players.all():
        arg_to_execute = "ulimit -v %d; ulimit -t %d ; ./%s" % (match.memory_limit * 1024, match.time_limit, bot.bot_file)
        bot_process = subprocess.Popen(
                arg_to_execute,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
                shell=True,
                )
        bots_process_list.append(bot_process)

    for bot in bots_process_list:
        print bot.pid
    
     
    end_game = False;
    while not end_game:
        to_send = readout(jp.stdout)
        (players, message) = parse_message(to_send)
        if message == ' ':
            print 'Ending game'
            end_game = True
            break
        for player in players:
            message = message + '\n'
            bots_process_list[player-1].stdin.write(message)
            response = readout(bots_process_list[player-1].stdout) + '\n'
            jp.stdin.write(response)
    return 11
    
def costam():
    return 5
