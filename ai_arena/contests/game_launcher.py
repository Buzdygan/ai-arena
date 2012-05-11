from decimal import Decimal
from ai_arena.contests.models import Match, MatchBotResult
from ai_arena import settings
from nadzorca.exit_status import *
import gearman
import pickle

class PickleDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return pickle.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return pickle.loads(decodable_string)

class PickleClient(gearman.GearmanClient):
    data_encoder = PickleDataEncoder

def launch_single_match(game, bots):
    """
        Launches single match of given game
        with given list of bots
    """

    match = Match(ranked_match=False, game=game, contest=None,
            time_limit=game.time_limit, memory_limit=game.memory_limit,
            status=MATCH_NOT_PLAYED)
    match.save()
    bot_results = dict()
    for bot in bots:
        bot_result = MatchBotResult(score=0, bot=bot, time_used=0, memory_used=0) 
        bot_result.save()
        match.players_results.add(bot_result)
        bot_results[bot] = bot_result
    arguments = {'game': game, 'bots': bots, 'match': match, 'bot_results': bot_results}

    gearman_client = PickleClient([settings.GEARMAN_HOST])
    gearman_client.submit_job('single_match', arguments, background=True)

def launch_contest_match(game, bots, contest):
    """
        Launches contest match of given game
        with given list of bots and contest
    """

    match = Match(ranked_match=True, game=game, contest=contest,
            time_limit=contest.time_limit, memory_limit=contest.memory_limit,
            status=MATCH_NOT_PLAYED)
    match.save()
    bot_results = dict()
    for bot in bots:
        bot_result = MatchBotResult(score=0, bot=bot, time_used=0, memory_used=0) 
        bot_result.save()
        match.players_results.add(bot_result)
        bot_results[bot] = bot_result
    arguments = {'game': game, 'bots': bots, 'match': match, 'bot_results': bot_results}

    gearman_client = PickleClient([settings.GEARMAN_HOST])
    gearman_client.submit_job('single_match', arguments, background=True)
