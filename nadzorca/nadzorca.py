#!/usr/bin/python
# Filename: nadzorca.py
import subprocess
import os
import tempfile
import sys
import threading
import Queue
import time
import select
import threading

def read_logs(judge, bots, log_map):
    processes = [judge]
    processes.extend(bots)
    pipes = [judge.stderr]
    stderr_to_proc_num = {}
    stderr_to_proc_num[judge.stderr] = 'judge'
    logs = {}
    logs[judge.stderr] = []
    for i in range(len(bots)):
        pipes.append(bots[i].stderr)
        stderr_to_proc_num[bots[i].stderr] = i
        logs[bots[i].stderr] = []
    # Below line menas "While judge or any bot is alive"
    while (reduce (lambda x, y: x or y, (map(lambda x : x.poll() == None, processes)), False)):
        (rlist, wlist, xlist) = select.select(pipes, [], [], 1000)
        for pipe in rlist:
            readp = read_whole_pipe(pipe)
            log(logs[pipe], readp)
    for pipe in logs.keys():
       log_map[stderr_to_proc_num[pipe]] = logs[pipe]
    

def read_whole_pipe(pipe):
    res = ''
    while True:
        (rl, wl, xl) = select.select([pipe],[],[], 0)
        if rl != []:
            read_letter = pipe.read(1)
            if read_letter != '':
                res += read_letter
            else:
                break
        else:
            break
    return res

class TimeoutException(Exception):
    pass

class EOFException(Exception):
    pass

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
def readout(pipe, timeout=10000):
    """
        This function reads communicates.
        The assumption is that every communicate ends with chars '<<<\n' not case-sensitive
        In addition every '<<<\n' frase is considered to be end of a communicate
    """
    mes = ''
    while mes[len(mes)-4:] != '<<<\n':
        (rl, wl, xl)  = select.select([pipe], [], [], timeout)
        if (rl != []):
            letter = pipe.read(1)
            if (letter == ''):
                raise EOFException()
            else:
                mes = mes + letter
        else:
            raise TimeoutException()
    return mes[:-4]

# A convenience function for readability purposes
def log(log_list, log_message):
    log_list.append(log_message)

def play(judge_file, players, memory_limit, time_limit):
    """
        judge_file - file containing judge program
        players - list of bots binaries
        memory_limit (in MB) - maximum memory for one bot
        time_limit (in sec) - maximum time limit for one bot
    """
    players_num = len(players)
    supervisor_log = []

    to_execute = "%s" % judge_file
    jp = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds = True,
            )
    log(supervisor_log, "Started judge succesfully\n")

    bots_process_list = []
    for bot_program in players:
        arg_to_execute = "%s" % (bot_program,)
        bot_process = subprocess.Popen(
                arg_to_execute,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                close_fds = True,
                )
        bots_process_list.append(bot_process)
    log(supervisor_log, "Started all bots succesfully\n")
    
    log_map = {}
    log_thread = threading.Thread(None, read_logs, None, (jp, bots_process_list, log_map), {})
    log_thread.start()

    times = []
    memory = []
    for i in range(players_num):
        times.append(time_limit)
        memory.append(memory_limit)

    bots = []
    message = ''
    
    results = {'exit_status' : 0, 'times' : times, 'memory' : memory, 
            'supervisor_log' : supervisor_log}
    
    game_in_progress = True

    while (game_in_progress):
        try:
            judge_mes = readout(jp.stdout)
        except TimeoutException:
            results['exit_status'] = 14
            log(supervisor_log, "Timeout reached while waiting for judge message.")
            break
        except EOFException:
            results['exit_status'] = 15
            log(supervisor_log, "EOF reached while reading message from judge.")
            break
        try:
            (bots, message) = parse_message(judge_mes)
        except:
            results['exit_status'] = 11
            log(supervisor_log, "Wrong message format from judge.")
            break
        if bots == [0]:
            b = range(players_num + 1)
            del(b[0])
            bots = b
        if message == 'END':
            print 'Ending game'
            try:
                res = readout(jp.stdout)
            except TimeoutException:
                result['exit_status'] = 16
                log(supervisor_log, "Timeout reached while waiting for scores from judge.")
                break
            except EOFException:
                result['exit_status'] = 17
                log(supervisor_log, "EOF reached while waiting for scores from judge.")
                break
            try:
                (scores, empty_mes) = parse_message(res)
                results['results'] = scores
            except:
                results['exit_status'] = 12
                log(supervisor_log, "Wrong scores message from judge.")
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
                    log(supervisor_log, "Tried to kill an unexsisting bot.")
                    game_in_progress = False
                    break
        else:
            for bnum in bots:
                if bnum > 0 and bnum <= players_num:
                    bot_process = bots_process_list[bnum-1]
                    if bot_process.poll() == None:
                        message = message + '<<<\n'
                        bot_process.stdin.write(message)
                        try :
                            response = readout(bot_process.stdout) + '<<<\n'
                        except TimeoutException:
                            response = '_DEAD_<<<\n'
                            bot_process.kill()
                        except EOFException:
                            response = '_DEAD_<<<\n'
                            bot_process.kill()
                        jp.stdin.write(response)
                    else:
                        response = '_DEAD_<<<\n'
                        jp.stdin.write(response)
                else:
                    results['exit_status'] = 13
                    log(supervisor_log, "Tried to send a message to an unexsiting bot.")
                    game_in_progress = False
                    break
    jp.kill()
    log_thread.join()

    results['logs'] = log_map
    results['supervisor_log'] = supervisor_log
    return results
