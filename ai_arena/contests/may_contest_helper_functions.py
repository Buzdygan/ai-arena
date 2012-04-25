from ai_arena.contests.models import Game, Bot, Contest, Ranking

# TODO: change it when judge for may contest is ready
def getMayGame():
    return Game.objects.get(name='test_game_kk')


# TODO: change it when sample bot for may contest is ready
def getDefaultMayContestBot():
    return Bot.objects.get(id=1)

# TODO: Change it when may contest object will be created
def getDefaultMayContest():
    return Contest.objects.all()[0]

# TODO: change it when may contest object will be created
def getDefaultMayRanking():
    return Ranking.objects.all()[0]
