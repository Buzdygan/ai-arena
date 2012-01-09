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
    bots = arguments['bots']

    bots2 = bots
    bots = bots[:-1]
    judge_program = game.judge_bin_file.path
    time_limit = 2
    memory_limit = 32
    bots_programs = [bot.bot_bin_file.path for bot in bots]

    results = nadzorca.play(judge_file=judge_program, players=bots_programs,
                    memory_limit=memory_limit, time_limit=time_limit)

    """
    bot_results = [MatchBotResult(score=res, bot=bot, time_used=10, memory_used=5) \
                for score, res in zip(results, bots)]
                """

    match = Match(ranked_match=False, game=game, match_log="", time_limit=1000, memory_limit=32)
    match.save()
    results = results[1:-2].split(',')
    print(results)
    bots = bots2
    for res, bot in zip(results, bots):
        bot_result = MatchBotResult(score=Decimal(res), bot=bot, time_used=10, memory_used=5) 
        bot_result.save()
        match.players_results.add(bot_result)
    match.save()

gearman_worker.register_task("single_match", single_match)
gearman_worker.work()
