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
import resource


def read_logs(judge_process, bots_process_list, log_map, run_thread):
    """
        Function that runs in a separate thread
        It polls stderrs of judge and bots, reads them and remembers the outputs
        in a map that is shared with the main thread (log_map argument)
        Later stderrs are returned as a form of logs
    """
    pipes = [judge_process.stderr]
    stderr_to_proc_num = {}
    stderr_to_proc_num[judge_process.stderr] = 'judge'
    logs = {}
    logs[judge_process.stderr] = []
    for i in range(len(bots_process_list)):
        pipes.append(bots_process_list[i].stderr)
        stderr_to_proc_num[bots_process_list[i].stderr] = i
        logs[bots_process_list[i].stderr] = []
    while (run_thread['val']):
        (rlist, wlist, xlist) = select.select(pipes, [], [], 1)
        for pipe in rlist:
            readp = read_whole_pipe(pipe)
            if readp != '':
                log(logs[pipe], readp)
    (rlist, wlist, xlist) = select.select(pipes, [], [], 1)
    for pipe in rlist:
        readp = read_whole_pipe(pipe)
        if readp != '':
            log(logs[pipe], readp)
    for pipe in logs.keys():
       log_map[stderr_to_proc_num[pipe]] = logs[pipe]


def read_whole_pipe(pipe):
    """
        Reads the pipe untill it's empty
        Used for reading stderrs
    """
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

# Exception thrown when timeout while waiting for output is reached
class TimeoutException(Exception):
    pass

# Exception thrown when EOF is found before proper end of message ('<<<\n')
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

def readout(pipe, timeout):
    """
        This function reads communicates.
        The assumption is that every communicate ends with char '\n'
        In addition every '\n' is considered to be end of a communicate
    """
    mes = ''
    while mes[len(mes)-1:] != '\n':
        (rl, wl, xl)  = select.select([pipe], [], [], timeout)
        if (rl != []):
            letter = pipe.read(1)
            if (letter == ''):
                raise EOFException()
            else:
                mes = mes + letter
        else:
            raise TimeoutException()
    return mes[:-1]

def log(log_list, log_message):
    """
        A convenience function for readability purposes
    """
    log_list.append(log_message)

def set_limits(time_limit, memory_limit):
    """
        A function that is run in forked processes before exec
        (see subprocess.Popen constructor preexec_fn argument)
        Used for setting limits of time and memory consumption for the process
    """
    mem_limit = memory_limit * 1024
    resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))

def get_stats(pid):
    """
        Reads informaton about time and memory consumption of the process 
        with given pid from the proc folder.
        Currently not in use
    """
    proc_stats = open('/proc/{0}/stat'.format(str(pid)))
    line = proc_stats.readline().split()
    return (float(line[13]) + float(line[14]), int(line[22]))

def play(judge_file, players, time_limit, memory_limit):
    """
        judge_file - file containing judge program
        players - list of bots binaries
        memory_limit (in MB) - maximum memory for one bot
        time_limit (in sec) - maximum time limit for one bot
    """

    players_num = len(players)
    supervisor_log = []

    to_execute = "%s" % judge_file
    judge_process = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds = True,
            preexec_fn = lambda : set_limits(10*time_limit, 10*memory_limit),
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
                preexec_fn = lambda : set_limits(time_limit, memory_limit),
                )
        bots_process_list.append(bot_process)
    log(supervisor_log, "Started all bots succesfully\n")

    log_map = {}
    run_thread = dict([('val', True)])
    log_thread = threading.Thread(None, read_logs, None, (judge_process, bots_process_list, log_map, run_thread), {})
    log_thread.start()

    bots = []
    message = ''
    
    results = {'exit_status' : 0, 'time' : {}, 'memory' : {}, 
            'supervisor_log' : supervisor_log}
    
    game_in_progress = True

    while (game_in_progress):
        try:
            judge_mes = readout(judge_process.stdout, time_limit*10)
        except TimeoutException:
            results['exit_status'] = 14
            judge_process.kill()
            log(supervisor_log, "Timeout reached while waiting for judge message.")
            break
        except EOFException:
            results['exit_status'] = 15
            try:
                judge_process.kill()
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
                res = readout(judge_process.stdout, time_limit * 10)
            except TimeoutException:
                results['exit_status'] = 16
                log(supervisor_log, "Timeout reached while waiting for scores from judge.")
                break
            except EOFException:
                results['exit_status'] = 17
                log(supervisor_log, "EOF reached while waiting for scores from judge.")
                break
            try:
                (scores, empty_mes) = parse_message(res)
                results['results'] = scores
            except:
                results['exit_status'] = 12
                log(supervisor_log, "Wrong scores message from judge.")
            break
        elif message == 'KILL':
            for bnum in players:
                if bnum > 0 and bnum <= players_num:
                    try:
                        bots_process_list[bnum-1].kill()
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
                    message = message + '\n'
                    try:
                        bot_process.stdin.write(message)
                        response = readout(bot_process.stdout, time_limit) + '\n'
                    except TimeoutException:
                        response = '_DEAD_\n'
                        try:
                            bot_process.kill()
                        except:
                            pass
                    except EOFException:
                        response = '_DEAD_\n'
                        try:
                            bot_process.kill()
                        except:
                            pass
                    except:
                        response = '_DEAD_\n'
                    finally:
                        try:
                            judge_process.stdin.write(response)
                        except:
                            result['exit_status'] = 104
                            log(supervisor_log, "Failed to send message to judge")
                            break
                else:
                    results['exit_status'] = 13
                    log(supervisor_log, "Tried to send a message to an unexsiting bot.")
                    game_in_progress = False
                    break
    
    # Stop the log thred
    run_thread['val'] = False
    # Kill all the processes
    try:
        judge_process.kill()
    except:
        pass
    for bot in bots_process_list:
        try:
            bot.kill()
        except:
            pass
    log_thread.join()

    final_times = {}
    final_memory = {}
    
    # Wait for dead bots and judge using wait4
    # Save information about their time usage in final_times
    for i in range(len(bots_process_list)):
        bot_process = bots_process_list[i]
        wait_info = os.wait4(bot_process.pid, 0)
        final_times[i] = wait_info[2].ru_utime + wait_info[2].ru_stime

    judge_wait_info = os.wait4(judge_process.pid, 0)
    final_times['judge'] = judge_wait_info[2].ru_utime + judge_wait_info[2].ru_stime
    
    results['time'] = final_times
    results['memory'] = final_memory
    results['logs'] = log_map
    results['supervisor_log'] = supervisor_log
    
    return results