#!/usr/bin/python
# Filename: nadzorca.py

import subprocess
import os
import tempfile
import sys
import threading
import Queue
import time

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
    l = to_send.split(']')
    if len(l) == 1:
        return l[0]
    else:
        return to_send.split(']')[1]

def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()


def readout(pipe):
    mes = ''
    while mes[len(mes)-3:] != 'END':
#        print mes
        mes = mes + pipe.read(1)
    pipe.read(1)
    return mes[:len(mes)-3]

"""
	ListOfBots is a list of objects of class Bot.
	Bots are meant to know where is theirs executable file is located.

	Game, according to the description above knows its limits and the judge, 
	which is an executable file
"""
def play(list_of_bots, game):
    jp = subprocess.Popen(
            game.judge_path,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
#            stderr=subprocess.PIPE,
            shell=True,
            )
    
    bots_process_list = []
    for bot in list_of_bots:
#        arg_to_execute = "ulimit -v %d -t %d ; ./%s" % (game.memory_limit * 1024, game.time_limit, bot.filepath)
        bot_process = subprocess.Popen(
                bot.filepath,
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
        message = get_message(to_send)
        if message == '':
            print 'Ending game'
            end_game = True
            break
        list_players_to_send = get_players(to_send)
        list_of_responses = []
        for player in list_players_to_send:
            message = message + '\n'
            bots_process_list[player-1].stdin.write(message)
            response = readout(bots_process_list[player-1].stdout)
            list_of_responses.append(response)
        for response in list_of_responses:
            response += '\n'
            jp.stdin.write(response)
    
    
