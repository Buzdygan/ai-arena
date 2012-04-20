from ai_arena.contests.models import Game, Bot

# TODO: change it when judge for may contest is ready
def getMayGame():
    return Game.objects.get(name='test_game_kk')


# TODO: change it when sample bot for may contest is ready
def getDefaultMayContestBot():
    return Bot.objects.get(id=1)


