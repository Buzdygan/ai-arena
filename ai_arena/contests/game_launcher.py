from nadzorca import nadzorca

def launch_single_match(game, bots):
    """
        Launches single match of given game
        with given list of bots
    """

    judge_program = game.judge_bin_file.path
    time_limit = 2
    memory_limit = 32
    bots_programs = [bot.bot_bin_file.path for bot in bots]

    nadzorca.play(judge_file=judge_program, players=bots_programs,
                    memory_limit=memory_limit, time_limit=time_limit)
