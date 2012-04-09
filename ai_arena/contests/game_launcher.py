from decimal import Decimal
from ai_arena.contests.models import Match, MatchBotResult
from ai_arena import settings
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

    arguments = {'game': game, 'bots': bots}

    gearman_client = PickleClient([settings.GEARMAN_HOST])
    gearman_client.submit_job('single_match', arguments, background=True)

def launch_contest_match(game, bots, contest):
    """
        Launches contest match of given game
        with given list of bots and contest
    """

    arguments = {'game': game, 'bots': bots, 'contest':contest}

    gearman_client = PickleClient([settings.GEARMAN_HOST])
    gearman_client.submit_job('contest_match', arguments, background=True)
