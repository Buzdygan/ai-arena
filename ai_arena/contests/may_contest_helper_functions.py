import os
from django.conf import settings
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from ai_arena.utils import get_current_date_time
from ai_arena.contests.models import User, Game, Bot, Contest, Ranking

"""
    This module contains views needed to perform may contest.\n
    The fact that GUI of may contest was slightly different from the final one
    explains why separate views were needed.\n\n

    WARNING: These views shoud not be used after closing may contest!
"""

def create_may_game():
    """
        Function creating instance of may Game.
    """
    try:
        game = Game()
        game.name = settings.MAY_CONTEST_GAME_NAME
        game.min_players = settings.MAY_CONTEST_PLAYERS_NUMBER
        game.max_players = settings.MAY_CONTEST_PLAYERS_NUMBER
        game.judge_lang = settings.MAY_CONTEST_GAME_JUDGE_LANG
        game.judge_source_file.save(game.name + settings.SOURCE_FORMATS[game.judge_lang], File(open(settings.MAY_CONTEST_GAME_JUDGE_PATH)))
        game.rules_file.save(game.name, File(open(settings.MAY_CONTEST_GAME_RULES_PATH)))
        game.save()
        moderator = User.objects.get(username=settings.MAY_MODERATOR_NAME)
        game.moderators.add(moderator)
        game.compile_judge()
        return game
    except Exception as e:
        # If something went wrong, delete the game
        Game.objects.filter(name=settings.MAY_CONTEST_GAME_NAME).delete()
        raise e

def create_may_default_bot():
    """
        Function creating instance of may default Bot, against which other Bots could be tested.
    """
    try:
        bot = Bot()
        bot.name = settings.MAY_CONTEST_DEFAULT_BOT_NAME
        bot.owner = User.objects.get(username=settings.TEST_USER_NAME)
        bot.game = get_may_game()
        bot.bot_lang = settings.MAY_CONTEST_DEFAULT_BOT_LANG
        bot.bot_source_file.save(bot.name + settings.SOURCE_FORMATS[bot.bot_lang], File(open(settings.MAY_CONTEST_DEFAULT_BOT_PATH)))
        bot.ranked = False
        bot.save()
        bot.compile_bot()
        return bot
    except Exception as e:
        # If something went wrong, delete the bot
        Bot.objects.filter(name=settings.MAY_CONTEST_DEFAULT_BOT_NAME).delete()
        raise e

def create_may_contest():
    """
        Creates an instance of may Contest.
    """
    try:
        contest = Contest()
        contest.name = settings.MAY_CONTEST_NAME
        contest.game = get_may_game()
        contest.begin_date = settings.MAY_CONTEST_BEGIN_DATE
        contest.end_date = settings.MAY_CONTEST_END_DATE
        contest.regulations_file.save(contest.name, File(open(settings.MAY_CONTEST_REGULATIONS_PATH)))
        contest.memory_limit = settings.MAY_CONTEST_MEMORY_LIMIT
        contest.time_limit = settings.MAY_CONTEST_TIME_LIMIT

        ranking = Ranking(type=Ranking.TYPE_GROUP)
        ranking.date_updated = get_current_date_time()
        ranking.save()
        contest.ranking = ranking
        contest.save()

        moderator = User.objects.get(username=settings.MAY_MODERATOR_NAME)
        contest.moderators.add(moderator)
        contest.save()
        return contest
    except Exception as e:
        # If something went wrong, delete the contest
        Contest.objects.filter(name=settings.MAY_CONTEST_NAME).delete()
        raise e

def get_may_game():
    """
        Helper function to access instance of may Game. If no such object exist this function creates a new one.
    """
    try:
        return Game.objects.get(name=settings.MAY_CONTEST_GAME_NAME)
    except ObjectDoesNotExist:
        return create_may_game()

def get_default_may_contest_bot():
    """
        Helper function to access instance of default Bot. If no such object exist this function creates a new one. 
    """
    try:
        return Bot.objects.get(name=settings.MAY_CONTEST_DEFAULT_BOT_NAME)
    except ObjectDoesNotExist:
        return create_may_default_bot()

def get_default_may_contest():
    """
        Helper function to access instance of may Contest. If no such object exist this function creates a new one.
    """
    try:
        return Contest.objects.get(name=settings.MAY_CONTEST_NAME)
    except ObjectDoesNotExist:
        return create_may_contest()

def get_picnic_user():
    return User.objects.get(username=settings.MAY_CONTEST_PICNIC_USERNAME)

def get_default_may_ranking():
    """
        Helper function to access instance of Ranking.
    """
    contest = get_default_may_contest()
    if not contest:
        raise Exception("There is no may contest")
    return contest.ranking

def generate_ranking():
    """
        Function used to generate Ranking object to may Contest.
    """
    contest = get_default_may_contest()
    if not contest:
        raise Exception("There is no may contest")
    """
    if contest.ranking:
        if contest.ranking.updated:
            return contest.ranking
    """
    contest.contestants.clear()
    game = get_may_game()
    game_bots = Bot.objects.filter(game=game, invalid=False, ranked=True)
    for bot in game_bots:
        contest.contestants.add(bot)
    contest.generate_group_ranking()
    return contest.ranking

def find_new_name_for_bot(bot_name, owner):
    if not Bot.objects.filter(owner=owner, name=bot_name).count(): 
        return bot_name
    suffix = 2
    while Bot.objects.filter(owner=owner, name=bot_name + str(suffix)).count():
        suffix += 1
    return bot_name + str(suffix)

def create_bot_and_add_to_contest(source_code, owner, contest, bot_language):
    """
        Creates new bot with owner from source code, adds suffix to name if needed
        Returns new name and error_log if something went wrong.
    """

    bot_name = owner.username + '_bot'
    bots_to_delete = Bot.objects.filter(owner=owner, name=bot_name)
    bot_path = settings.PICNIC_BOTS_PATH + bot_name + settings.SOURCE_FORMATS[bot_language]
    bot_file = open(bot_path, 'w')
    bot_file.write(source_code)
    bot_file.close()

    new_bot = Bot(name=bot_name, owner=owner, game=contest.game, bot_lang=bot_language)
    new_bot.bot_source_file.save(new_bot.name + settings.SOURCE_FORMATS[new_bot.bot_lang], File(open(bot_path)))
    new_bot.save()
    exit_status, logs = new_bot.compile_bot()
    print('logs', logs)
    if exit_status != 0:
        new_bot.delete()
        return logs 
    else:
        for bot in bots_to_delete:
            if bot.id != new_bot.id:
                bot.delete_bot_matches()
                bot.delete()
        contest.contestants.add(new_bot)
        return None

def read_code_from_file(filename):
    file = open(filename, 'r')
    code = file.read()
    file.close()
    return code

def get_default_bot_codes():
    """
        Helper function returning templates of bots for may Contest.
    """
    bot_codes = dict()
    bot_codes['bot_code1'] = read_code_from_file(settings.PICNIC_BOT_CODES_FILES['bot_code1']) 
    bot_codes['bot_code2'] = read_code_from_file(settings.PICNIC_BOT_CODES_FILES['bot_code2'])
    bot_codes['bot_code3'] = read_code_from_file(settings.PICNIC_BOT_CODES_FILES['bot_code3'])
    bot_codes['bot_code4'] = read_code_from_file(settings.PICNIC_BOT_CODES_FILES['bot_code4'])
    return bot_codes
