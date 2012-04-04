from os import system

from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from ai_arena import settings
from ai_arena.contests.compilation import compile
from ai_arena.contests.forms import SendBotForm, SendBotWithGameForm
from ai_arena.contests.models import Game, Bot

@login_required
def send_bot(request, game_id):
    """
        Displays form to send bot for a game with id equal to game_id.
        If game_id is nto given or there is no Game object with id equal to game_id
        then Exception is thrown
    """
    if not game_id:
        raise Exception("In game_details: No game_id given")

    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In game_details: Wrong game_id given")
    
    if request.method == 'POST':
        form = SendBotForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            bot = Bot()
            bot.name = request.POST['bot_name']
            bot.bot_source_file = request.FILES['bot_source']
            bot.bot_lang = request.POST['bot_language']

            # Add game and owner info
            bot.game = game
            bot.owner = request.user
            bot.save()

            # Compile source file to directory with source file
            src = settings.MEDIA_ROOT + bot.bot_source_file.name
            target = settings.MEDIA_ROOT + bot.bot_source_file.name + '.bin' 
            lang = bot.bot_lang
            compile(src, target, lang)

            # Use compiled file in object bot
            f = File(open(target))
            bot.bot_bin_file.save(bot.name, f)

            # Save changes made to bot object
            bot.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/')
    else:
        form = SendBotForm()
    
    return render_to_response('gaming/send_bot.html',
            {
                'form': form,
                'game_id': game_id,
            },
            context_instance=RequestContext(request))

@login_required
def send_bot_with_game(request):
    """
        This view is used when user wants to send bot from game details view.
        It is different from simple send bot view, because game is known, so there is
        no need to pick it form list.
    """
    if request.method == 'POST':
        form = SendBotWithGameForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            bot = Bot()
            bot.name = request.POST['bot_name']
            bot.bot_source_file = request.FILES['bot_source']
            bot.bot_lang = request.POST['bot_language']
            game = Game.objects.get(id = request.POST['game'])
            if game is None:
                raise Exception("In send_bot_with_game: Wrong game_id given")
            bot.game = game

            # Add owner info
            bot.owner = request.user
            bot.save()

            # Compile source file to directory with source file
            src = settings.MEDIA_ROOT + bot.bot_source_file.name
            target = settings.MEDIA_ROOT + bot.bot_source_file.name + '.bin' 
            lang = bot.bot_lang
            compile(src, target, lang)

            # Use compiled file in object bot
            f = File(open(target))
            bot.bot_bin_file.save(bot.name, f)

            # Save changes made to bot object
            bot.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/')
    else:
        form = SendBotWithGameForm()
    
    return render_to_response('gaming/send_bot.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))

