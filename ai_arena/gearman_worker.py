import gearman
import pickle
from nadzorca import nadzorca
from decimal import Decimal
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
    if len(scores) < len(bots) or len(time_used) < len(bots) + 1:
        return

    log = ''.join(results['supervisor_log'])
    print(results)
    match.log = log
    for (i, bot) in enumerate(bots):
        bot_result = MatchBotResult(score=scores[i], bot=bot, time_used=time_used[i], memory_used=0) 
        bot_result.save()
        match.players_results.add(bot_result)
    match.save()

gearman_worker.register_task("single_match", single_match)
gearman_worker.work()
