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
import exit_status
import multiprocessing as mp
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
grand_dir = os.path.dirname(current_dir)
os.sys.path.insert(0, current_dir)

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
        Previously used for setting limits of time and memory consumption for the process.
        Currently not in use.
    """
    mem_limit =  memory_limit * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_CPU, (time_limit + 1, time_limit + 1))
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit* 2, mem_limit*2))

def get_stats(pid):
    """
        Reads informaton about time and memory consumption of the process 
        with given pid from the proc folder.
    """
    try:
        proc_stats = open('/proc/{0}/stat'.format(str(pid)))
        line = proc_stats.readline().split()
        return (float(line[13]) + float(line[14]), int(line[22]))
    except:
        return (None, None)

def limiter(pids_list, stop_indicator, proc_info, max_time, max_memory, time_limit, memory_limit):
    """
        Function executed in separate process, that measures memory and time
        consumption of processes with pids in pids_list.
        Reads information from proc folder about all relevant processes, every 0.1 seconds.
    """
    sc_clk_tck_id = os.sysconf_names['SC_CLK_TCK']
    ticks_per_second = os.sysconf(sc_clk_tck_id)
    mem_lmt = memory_limit * 1024 * 1024
    time_lmt = time_limit * ticks_per_second
    while(True):
        judge_pid = pids_list[0]
        if os.path.exists("/proc/{0}/stat".format(judge_pid)):
            time_elapsed, memory = get_stats(judge_pid)
            if time_elapsed > 10*time_lmt:
                judge_proc.kill()
                proc_info[0] = exit_status.BOT_TLE
            elif memory > 10*mem_lmt:
                judge_proc.kill()
                proc_info[0] = exit_status.BOT_MLE
            max_memory[0] = max(max_memory[0], memory)
        for pid_num in range(1,len(pids_list)):
            bot_pid = pids_list[pid_num]
            if os.path.exists("/proc/{0}/stat".format(bot_pid)):
                time_elapsed, memory = get_stats(bot_pid)
                if time_elapsed > time_lmt:
                    os.kill(bot_pid, signal.SIGKILL)
                    proc_info[proc_num] = exit_status.BOT_TLE
                elif memory > mem_lmt:
                    os.kill(bot_pid, signal.SIGKILL)
                    proc_info[proc_num] = exit_status.BOT_MLE
                max_memory[pid_num] = max(max_memory[pid_num], memory)
                max_time[pid_num] = max(max_time[pid_num], float(time_elapsed)/ticks_per_second)
        time.sleep(0.1)
        if stop_indicator[0]:
            break;

C_LANGUAGE = 'C'
CPP_LANGUAGE = 'CPP'
JAVA_LANGUAGE = 'JAVA'
PYTHON_LANGUAGE = 'PYTHON'

def get_run_command(program_name, program_lang):
    return [current_dir + "/syscall_trace" , program_name ,   program_lang]
    #if program_lang == C_LANGUAGE:
    #    command = C_RUN_COMMAND + program_name
    #if program_lang == CPP_LANGUAGE:
    #    command = CPP_RUN_COMMAND + program_name
    #if program_lang == JAVA_LANGUAGE:
    #    command = JAVA_RUN_COMMAND + program_name
    #if program_lang == PYTHON_LANGUAGE:
    #    command = PYTHON_RUN_COMMAND + program_name
    return command

def play(judge_file, judge_lang, players, time_limit, memory_limit):
    """
        judge_file - file containing judge program
        players - list of bots binaries
        memory_limit (in MB) - maximum memory for one bot
        time_limit (in sec) - maximum time limit for one bot
    """

    players_num = len(players)
    supervisor_log = []

    to_execute = get_run_command(judge_file, judge_lang)
    judge_process = subprocess.Popen(
            to_execute,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds = True,
            #preexec_fn = lambda : set_limits(10*time_limit, 10*memory_limit),
            )
    judge_pid = int(judge_process.stdout.readline())
    log(supervisor_log, "Started judge succesfully\n")

    bots_process_list = []
    bots_pids = []
    for (bot_program, bot_lang) in players:
        arg_to_execute = get_run_command(bot_program, bot_lang)
        bot_process = subprocess.Popen(
                arg_to_execute,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                close_fds = True,
                #preexec_fn = lambda : set_limits(time_limit, memory_limit),
                )
        bots_process_list.append(bot_process)
        bots_pids.append(int(bot_process.stdout.readline()))
    log(supervisor_log, "Started all bots succesfully\n")

    log_map = {}
    run_thread = dict([('val', True)])
    log_thread = threading.Thread(None, read_logs, None, (judge_process, bots_process_list, log_map, run_thread), {})
    log_thread.start()

    manager = mp.Manager()
    pids_list = manager.list()
    pids_list.append(judge_pid)
    pids_list.extend(bots_pids)
    max_memory = manager.list([0.0 for x in range(players_num+1)])
    max_time = manager.list([0.0 for x in range(players_num+1)])
    stop_indicator = manager.dict([(0, False)])
    proc_info = manager.list([exit_status.BOT_OK for x in range(players_num+1)])
    
    limiter_proc = mp.Process(target=limiter, args=(pids_list, stop_indicator, proc_info, max_time, max_memory, time_limit, memory_limit))
    limiter_proc.start()

    bots = []
    message = ''
    
    results = {'exit_status' : exit_status.SUPERVISOR_OK, 'time' : {}, 'memory' : {}, 
            'supervisor_log' : supervisor_log, 'bots_exit' : {}, }
    
    game_in_progress = True

    while (game_in_progress):
        try:
            judge_mes = readout(judge_process.stdout, time_limit*10)
        except TimeoutException:
            results['exit_status'] = exit_status.JUDGE_TIMEOUT
            os.kill(judge_pid, signal.SIGKILL)
            log(supervisor_log, "Timeout reached while waiting for judge message.")
            break
        except EOFException:
            results['exit_status'] = exit_status.JUDGE_EOF
            try:
                os.kill(judge_pid, signal.SIGKILL)
            except:
                pass
            log(supervisor_log, "EOF reached while reading message from judge.")
            break
        try:
            (bots, message) = parse_message(judge_mes)
        except:
            results['exit_status'] = exit_status.JUDGE_WRONG_MESSAGE
            log(supervisor_log, "Wrong message format from judge.")
            os.kill(judge_pid, signal.SIGKILL)
            break
        if bots == [0]:
            bots = range(1,players_num + 1)
        if message == 'END':
            try:
                res = readout(judge_process.stdout, time_limit * 10)
            except TimeoutException:
                results['exit_status'] = exit_status.JUDGE_SCORES_TIMEOUT
                log(supervisor_log, "Timeout reached while waiting for scores from judge.")
                break
            except EOFException:
                results['exit_status'] = exit_status.JUDGE_SCORES_EOF
                log(supervisor_log, "EOF reached while waiting for scores from judge.")
                break
            try:
                (scores, empty_mes) = parse_message(res)
                results['results'] = dict(enumerate(scores))
            except:
                results['exit_status'] = exit_status.JUDGE_WRONG_SCORES
                log(supervisor_log, "Wrong scores message from judge.")
            break
        elif message == 'KILL':
            for bnum in bots:
                if bnum > 0 and bnum <= players_num:
                    try:
                        os.kill(bots_pids[bnum-1], signal.SIGKILL)
                        #bots_process_list[bnum-1].kill()
                        proc_info[bnum] = exit_status.BOT_KILLED
                    except:
                        pass
                else:
                    results['exit_status'] = exit_status.NOT_EXISTING_KILL
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
                            os.kill(bot_pids[bnum-1], signal.SIGKILL)
                        except:
                            pass
                    except EOFException:
                        response = '_DEAD_\n'
                        try:
                            os.kill(bot_pids[bnum-1], signal.SIGKILL)
                        except:
                            pass
                    except:
                        response = '_DEAD_\n'
                    finally:
                        try:
                            judge_process.stdin.write(response)
                        except:
                            results['exit_status'] = exit_status.JUDGE_WRITE
                            log(supervisor_log, "Failed to send message to judge")
                            break
                else:
                    results['exit_status'] = exit_status.NOT_EXISTING_MESSAGE
                    log(supervisor_log, "Tried to send a message to an unexsiting bot.")
                    game_in_progress = False
                    break
    
    # Stop the log thred
    run_thread['val'] = False
    # Kill all the processes
    try:
        os.kill(judge_pid, signal.SIGKILL)
        judge_process.kill()
    except:
        pass
    for bot_num in range(len(bots_pids)):
        try:
            os.kill(bots_pids[bot_num], signal.SIGKILL)
        except Exception as inst:
            pass
    log_thread.join()

    # Stop the limiter
    stop_indicator[0] = True
    limiter_proc.join()

    final_times = {}
    final_memory = {}
    
    for i in range(len(bots_process_list)):
        bot_process = bots_process_list[i]
        #wait_info = os.wait4(bot_process.pid, 0)
        final_times[i] = float(max_time[i+1])
        final_memory[i] = float(max_memory[i+1])/(1024*1024)
        results['bots_exit'][i] = proc_info[i+1]

    #judge_wait_info = os.wait4(judge_process.pid, 0)
    final_times['judge'] = float(max_time[0])
    final_memory['judge'] = float(max_memory[0])/(1024*1024)
    
    results['judge_exit'] = proc_info[0]

    results['time'] = final_times
    results['memory'] = final_memory
    results['logs'] = log_map
    results['supervisor_log'] = supervisor_log
    
    return results
