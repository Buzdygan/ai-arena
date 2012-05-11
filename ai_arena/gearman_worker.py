import gearman
import pickle
from nadzorca import nadzorca
from decimal import Decimal
from django.conf import settings
from ai_arena.contests.models import Match, MatchBotResult

class PickleDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return pickle.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return pickle.loads(decodable_string)

class PickleWorker(gearman.GearmanWorker):
    data_encoder = PickleDataEncoder

gearman_worker = PickleWorker(['localhost'])

def single_match(gearman_worker, gearman_job):
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
    if len(scores) < len(bots) or len(time_used) < len(bots) + 1:
        return

    log = ''.join(results['supervisor_log'])
    print(log)
    for (i, bot) in enumerate(bots):
        bot_result = bot_results[bot]
        bot_result.score = scores[i]
        # convert from seconds to miliseconds
        bot_result.time_used = int(1000.0 * time_used[i])
        bot_result.memory_used = memory_used[i]
        bot_result.status = bots_exit[i]
        bot_result.save()
    match.log = log
    match.status = settings.MATCH_PLAYED
    match.save()

gearman_worker.register_task("single_match", single_match)
gearman_worker.work()
