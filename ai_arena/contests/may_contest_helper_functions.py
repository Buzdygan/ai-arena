from django.conf import settings
from ai_arena.contests.models import Game, Bot, Contest, Ranking

# TODO: change it when judge for may contest is ready
def getMayGame():
    return Game.objects.get(name=settings.MAY_CONTEST_GAME_NAME)

# TODO: change it when sample bot for may contest is ready
def getDefaultMayContestBot():
    return Bot.objects.get(name=settings.MAY_CONTEST_DEFAULT_BOT_NAME)

def getDefaultMayContest():
    return Contest.objects.get(name=settings.MAY_CONTEST_NAME)

def getDefaultMayRanking():
    contest = getDefaultMayContest()
    return contest.ranking
