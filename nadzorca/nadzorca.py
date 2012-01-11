#!/usr/bin/python
# Filename: nadzorca.py
import subprocess
import os
import tempfile
import sys
import threading
import Queue
import time

def parse_message(to_send):
    """
        This function parses a message from judge returning list of players as a first of pair
        and an actual message as a second of pair

        Every message coming here must contain a list of players in brackets like these: '[' and ']'.
        It can contain multiple of any of them, in this case the first pair is treated as a list of players.
    """
    l = to_send.split(']')
    players = map(lambda x:int(x), l[0][1:].split(','))
    mes = '' 
    for k in l[1:]:
        mes = mes + k + ']'
    return (players,mes[:-1])

# TODO: Add timeout!
def readout(pipe, timeout=0):
    """
        This function reads communicates.
        The assumption is that every communicate ends with chars '<<<\n' not case-sensitive
        In addition every '<<<\n' frase is considered to be end of a communicate
    """
    mes = ''
    while mes[len(mes)-4:] != '<<<\n':
        mes = mes + pipe.read(1)
    return mes[:-4]

def play(judge_file, players, memory_limit, time_limit):
    """
        judge_file - file containing judge program
        players - list of bots binaries
        memory_limit (in MB) - maximum memory for one bot
        time_limit (in sec) - maximum time limit for one bot
    """
    players_num = len(players)

    to_execute = "%s" % judge_file
    jp = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
#            stderr=subprocess.PIPE,
            )
    
    bots_process_list = []
    for bot_program in players:
        arg_to_execute = "%s" % (bot_program,)
        bot_process = subprocess.Popen(
                arg_to_execute,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
                close_fds = True,
                )
        bots_process_list.append(bot_process)
    
    times = []
    memory = []
    for i in range(players_num):
        times.append(time_limit)
        memory.append(memory_limit)
    
    bots = []
    message = ''
    
    results = {'exit_status' : 0, 'times' : times, 'memory' : memory}
    
    game_in_progress = True

    while (game_in_progress):
        judge_mes = readout(jp.stdout)
        try:
            (bots, message) = parse_message(judge_mes)
        except:
            results['exit_status'] = 11
            break
        if bots == [0]:
            b = range(players_num + 1)
            del(b[0])
            bots = b
        if message == 'END':
            print 'Ending game'
            res = readout(jp.stdout)
            try:
                (scores, empty_mes) = parse_message(res)
                results['results'] = scores
            except:
                results['exit_status'] = 12
            for bot_process in bots_process_list:
                bot_process.kill()
                #Zebranie informacji o czasach i pamieci
            jp.terminate()
            game_in_progress = False
            break
        elif message == 'KILL':
            for bnum in players:
                if bnum > 0 and bnum <= players_num:
                    bots_process_list[bnum-1].terminate()
                else:
                    results['exit_status'] = 13
                    game_in_progress = False
                    break
        else:
            for bnum in bots:
                if bnum > 0 and bnum <= players_num:
                    bot_process = bots_process_list[bnum-1]
                    if bot_process.poll() == None:
                        message = message + '<<<\n'
                        bot_process.stdin.write(message)
                        response = readout(bot_process.stdout) + '<<<\n'
                        jp.stdin.write(response)
                    else:
                        response = '_DEAD_<<<\n'
                        jp.stdin.write(response)
                else:
                    results['exit_status'] = 13
                    game_in_progress = False
                    break
        for bot_process in bots_process_list:
            message = message + '\n'
            bot_process.stdin.write(message)
            response = readout(bot_process.stdout) + '\n'
            jp.stdin.write(response)

    for bot in bots_process_list:
        bot.kill()

    jp.kill()

    print(results)
    return results
