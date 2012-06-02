import gearman
import pickle
from nadzorca import nadzorca
from nadzorca.exit_status import *
from decimal import Decimal
from django.conf import settings
from ai_arena.contests.models import Match, MatchBotResult

def single_match(gearman_worker, gearman_job):
    """
        Gearman worker main function.\n
        It's responsible for getting argunemts from Gearman server, parsing them and finally
        calling Nadzorca's play function (which performs Match between given Bots).\n
        Then it stores results in match object (received from Gearman server) and saves changes to database.
    """
    print "lets play single match\n"
    arguments = gearman_job.data
    game = arguments['game']
    match = arguments['match']
    bots = arguments['bots']
    bot_results = arguments['bot_results']
    memory_limit = match.memory_limit 
    # convert miliseconds to seconds
    time_limit = match.time_limit / 1000.0 

    judge_program = game.judge_bin_file.path
    judge_lang = game.judge_lang
    bots_programs = [(bot.bot_bin_file.path, bot.bot_lang) for bot in bots]

    results = nadzorca.play(judge_file=judge_program, judge_lang=judge_lang, players=bots_programs,
                    memory_limit=memory_limit, time_limit=time_limit)

    scores = results['results']
    time_used = results['time']
    memory_used = results['memory']
    bots_exit = results['bots_exit']
    bot_logs = results['logs']
    if len(scores) < len(bots) or len(time_used) < len(bots) + 1:
        return

    log = ''.join(results['supervisor_log'])
    print(results)
    match.status = results['exit_status']
    for (i, bot) in enumerate(bots):
        bot_result = bot_results[bot]
        bot_result.score = scores[i]
        # convert from seconds to miliseconds
        bot_result.time_used = int(1000.0 * time_used[i])
        bot_result.memory_used = memory_used[i]
        bot_result.status = bots_exit[i]
        if (bot_result.status != BOT_OK) & (match.status == SUPERVISOR_OK):
            match.status = MATCH_WALKOVER
        bot_result.logs = ''.join(bot_logs[i])
        bot_result.save()
    match.log = log
    match.save()
