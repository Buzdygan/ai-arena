from nadzorca import nadzorca
from decimal import Decimal
from contests.models import Match, MatchBotResult 

def launch_single_match(game, bots):
    """
        Launches single match of given game
        with given list of bots
    """

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


