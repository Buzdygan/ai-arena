#!/usr/bin/python
# Filename: nadzorca.py
import subprocess
import os
import tempfile
import sys
import threading
import Queue
import time

def parse_response(response, player):
        return "[" + str(player) + "]" + response


def parse_message(to_send):
    """
        This function parses a message from judge returning list of players as a first of pair
        and an actual message as a second of pair

        Every message coming here must comtain a list of players in brackets like these: '[' and ']'.
        It can contain multiple of any of them, in this case the first pair is treated as a list of players.
    """
    l = to_send.split(']')
    players = map(lambda x:int(x), l[0][1:].split(','))
    mes = l[1]
    for t in l[2:]:
        mes += ']' + t
    return (players,mes)

# TODO: Add timeout!
def readout(pipe, timeout=0):
    """
        This function reads communicates.
        The assumption is that every communicate ends with chars 'END\n' not case-sensitive
        In addition every 'END\n' frase is considered to be end of a communicate
    """
    mes = ''
    while mes[len(mes)-3:].upper() != 'END':
        mes = mes + pipe.read(1)
    pipe.read(1)
    return mes[:len(mes)-3]

def play(judge_file, players, memory_limit, time_limit):
    """
        judge_file - file containing judge program
        players - list of bots binaries
        memory_limit (in MB) - maximum memory for one bot
        time_limit (in sec) - maximum time limit for one bot
    """
    to_execute = "%s" % judge_file
    jp = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
#            stderr=subprocess.PIPE,
            shell=True,
            )
    
    bots_process_list = []
    for bot_program in players:
        arg_to_execute = "ulimit -v %d; ulimit -t %d ; %s" % (memory_limit * 1024, time_limit, bot_program)
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
        try:
            (players, message) = parse_message(to_send)
        except:
            print 'Ending game'
            end_game = True
            break
        if message == ' ':
            print 'Ending game'
            end_game = True
            break
        for bot_process in bots_process_list:
            message = message + '\n'
            bot_process.stdin.write(message)
            response = readout(bot_process.stdout) + '\n'
            jp.stdin.write(response)
    return 11
    
def costam():
    return 5
