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
import signal

# Global variables for watching over judges and bots time and memory usage.
# They have to be global, because it's impossible to pass arguments to signal handler

# A dictionary {pid : CPU + sys time used so far by process}
time_usage = {}
# A dictionary {pid : memory used by process}
memory_usage = {}
# A dictionary {pid : limits to be enforced on process in form (time_limit (seconds) , memory limit (Kb))}
process_limits = {}

stopped_pids = set()
log_map = {}
judge_process = None
bots_process_list = []

def enforce_limits(signum, frame):
    global stopped_pids
    global time_usage
    global memory_usage
    global processes_limits
    global judge_process
    global bots_process_list
    watched_processes = set(bots_process_list)
    watched_processes.add(judge_process)
    for proc in watched_processes:
        try:
            pid = proc.pid
            stat_file = open('/proc/' + str(pid) + '/stat')
            line = (stat_file.readline()).split()
            time_usage[pid] = (float(line[13]) + float(line[14]))/(os.sysconf(2))
            memory_usage[pid] = (int(line[22]) + 1023)/1024
            if (memory_usage[pid]  > (process_limits[pid][1])) or (time_usage[pid] > process_limits[pid][0]):
                proc.kill()
                stopped_pids.add(pid)
                if (memory_usage[pid] > process_limits[pid][1]):
                    memory_usage[pid] = 'LIMIT EXCEEDED'
                if (time_usage[pid] > process_limits[pid][0]):
                    time_usage[pid] = 'LIMIT EXCEEDED'
        except:
            pass

def read_logs():
    global judge_process
    global bots_process_list
    global stopped_pids
    pipes = [judge_process.stderr]
    stderr_to_proc_num = {}
    stderr_to_proc_num[judge_process.stderr] = 'judge'
    logs = {}
    logs[judge_process.stderr] = []
    for i in range(len(bots_process_list)):
        pipes.append(bots_process_list[i].stderr)
        stderr_to_proc_num[bots_process_list[i].stderr] = i
        logs[bots_process_list[i].stderr] = []
    # Below line menas "While judge or any bot is alive"
    #while (reduce (lambda x, y: x or y, (map(lambda x : x.poll() == None, bots_process_list)), (judge_process.poll() == None))):
    while (len(stopped_pids) < len(bots_process_list) + 1):
        (rlist, wlist, xlist) = select.select(pipes, [], [], 10)
        for pipe in rlist:
            readp = read_whole_pipe(pipe)
            log(logs[pipe], readp)
    for pipe in logs.keys():
       log_map[stderr_to_proc_num[pipe]] = logs[pipe]

def get_logs_once():
    global judge_process
    global bots_process_list
    pipes = [judge_process.stderr]
    stderr_to_proc_num = {}
    stderr_to_proc_num[judge_process.stderr] = 'judge'
    logs = {}
    logs[judge_process.stderr] = []
    for i in range(len(bots_process_list)):
        pipes.append(bots_process_list[i].stderr)
        stderr_to_proc_num[bots_process_list[i].stderr] = i
        logs[bots_process_list[i].stderr] = []
    (rlist, wlist, xlist) = select.select(pipes, [], [], 0.1)
    for pipe in rlist:
        readp = read_whole_pipe(pipe)
        log(logs[pipe], readp)
    for pipe in logs.keys():
       log_map[stderr_to_proc_num[pipe]].extend(logs[pipe])

   

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

def readout(proc, timeout):
    """
        This function reads communicates.
        The assumption is that every communicate ends with chars '<<<\n' not case-sensitive
        In addition every '<<<\n' frase is considered to be end of a communicate
    """
    pipe = proc.stdout
    mes = ''
    while mes[len(mes)-4:] != '<<<\n':
        if proc.pid in stopped_pids:
            raise TimeoutException()
        try:
            (rl, wl, xl)  = select.select([pipe], [], [], timeout)
            if (rl != []):
                letter = pipe.read(1)
                if (letter == ''):
                    raise EOFException()
                else:
                    mes = mes + letter
            else:
                raise TimeoutException()
        except EOFException:
            raise EOFException()
        except TimeoutException():
            raise TimeoutException()
        except:
            pass
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
    global time_usage
    global memory_usage
    global process_limits
    global judge_process
    global bots_process_list
    global log_map
    global stopped_pids

    players_num = len(players)
    supervisor_log = []

    to_execute = "%s" % judge_file
    judge_process = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds = True,
            )
    time_usage[judge_process.pid] = 0.0
    memory_usage[judge_process.pid] = 0
    process_limits[judge_process.pid] = (10 * float(time_limit) , 10 * int(memory_limit))
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
        time_usage[bot_process.pid] = 0.0
        memory_usage[bot_process.pid] = 0
        process_limits[bot_process.pid] = (float(time_limit), int(memory_limit))
    log(supervisor_log, "Started all bots succesfully\n")

    signal.signal(signal.SIGALRM, enforce_limits)
    signal.setitimer(signal.ITIMER_REAL, 0.0001, 0.1)

    log_map = {}
    log_thread = threading.Thread(None, read_logs, None)
    log_thread.start()

    bots = []
    message = ''
    
    results = {'exit_status' : 0, 'time' : {}, 'memory' : {}, 
            'supervisor_log' : supervisor_log}
    
    game_in_progress = True

    while (game_in_progress):
        try:
            judge_mes = readout(judge_process, time_limit*10)
        except TimeoutException:
            results['exit_status'] = 14
            try:
                stopped_pids.add(judge_process.pid)
                judge_process.send_singal(signal.SIGSTOP)
            except:
                pass
            log(supervisor_log, "Timeout reached while waiting for judge message.")
            break
        except EOFException:
            results['exit_status'] = 15
            try:
                stopped_pids.add(judge_process.pid)
                judge_process.send_signal(signal.SIGSTOP)
            except:
                pass
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
            try:
                res = readout(judge_process, time_limit * 10)
            except TimeoutException:
                results['exit_status'] = 16
                log(supervisor_log, "Timeout reached while waiting for scores from judge.")
                try:
                    stopped_pids.add(judge_process.pid)
                    judge_process.send_signal(signal.SIGSTOP)
                except:
                    pass
                break
            except EOFException:
                results['exit_status'] = 17
                log(supervisor_log, "EOF reached while waiting for scores from judge.")
                try:
                    stopped_pids.add(judge_process.pid)
                    judge_process.send_signal(signal.SIGSTOP)
                except:
                    pass
                break
            try:
                (scores, empty_mes) = parse_message(res)
                results['results'] = scores
            except:
                results['exit_status'] = 12
                log(supervisor_log, "Wrong scores message from judge.")
            # Pause judge and bots and get their times and memory usage one last time
            for bot_process in bots_process_list:
                try:
                    stopped_pids.add(bot_process.pid)
                    bot_process.send_signal(signal.SIGSTOP)
                except:
                    pass
            try:
                stopped_pids.add(judge_process.pid)
                judge_process.send_signal(signal.SIGSTOP)
            except:
                pass
            game_in_progress = False
            break
        elif message == 'KILL':
            for bnum in players:
                if bnum > 0 and bnum <= players_num:
                    try:
                        stopped_pids.add(bots_process_list[bnum-1].pid)
                        bots_process_list[bnum-1].send_signal(signal.SIGSTOP)
                    except:
                        pass
                else:
                    results['exit_status'] = 13
                    log(supervisor_log, "Tried to kill an unexsisting bot.")
                    game_in_progress = False
                    break
        else:
            for bnum in bots:
                if bnum > 0 and bnum <= players_num:
                    bot_process = bots_process_list[bnum-1]
                    if bot_process.poll() == None and (bot_process.pid not in stopped_pids):
                        message = message + '<<<\n'
                        bot_process.stdin.write(message)
                        try :
                            response = readout(bot_process, time_limit) + '<<<\n'
                        except TimeoutException:
                            response = '_DEAD_<<<\n'
                            stopped_pids.add(bot_process.pid)
                            try:
                                bot_process.send_signal(signal.SIGSTOP)
                            except:
                                pass
                        except EOFException:
                            response = '_DEAD_<<<\n'
                            stopped_pids.add(bot_process.pid)
                            try:
                                bot_process.send_signal(signal.SIGSTOP)
                            except:
                                pass
                        judge_process.stdin.write(response)
                    else:
                        response = '_DEAD_<<<\n'
                        judge_process.stdin.write(response)
                else:
                    results['exit_status'] = 13
                    log(supervisor_log, "Tried to send a message to an unexsiting bot.")
                    game_in_progress = False
                    break

    signal.setitimer(signal.ITIMER_REAL, 0)
    enforce_limits(None, None)
    try:
        stopped_pids.add(judge_process.pid)
        judge_process.kill()
    except:
        pass
    for bot in bots_process_list:
        try:
            stopped_pids.add(bot.pid)
            bot.kill()
        except:
            pass
    log_thread.join()
    get_logs_once()

    final_times = {}
    final_memory = {}
    final_times['judge'] = time_usage[judge_process.pid]
    final_memory['judge'] = memory_usage[judge_process.pid]
    for i in range(len(bots_process_list)):
        bot_process = bots_process_list[i]
        final_times[i] = time_usage[bot_process.pid]
        final_memory[i] = memory_usage[bot_process.pid]
    
    results['time'] = final_times
    results['memory'] = final_memory
    results['logs'] = log_map
    results['supervisor_log'] = supervisor_log
    
    return results
