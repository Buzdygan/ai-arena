from os import system

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.files import File
from django.contrib.auth.decorators import login_required

from ai_arena import settings
from ai_arena.contests.forms import NewGameForm
from ai_arena.contests.models import Game
from ai_arena.contests.compilation import compile

@login_required
def create_new_game(request):
    """
        Prepares a form to render for creating new game.
        Later it checks results, and if everything is OK it saves
        new Game object to database
    """
    if request.method == 'POST':
        form = NewGameForm(request.POST, request.FILES)
        if form.is_valid():
            # Save known fields
            game = Game()
            game.name = request.POST['game_name']
            game.rules_file = request.FILES['game_rules']
            game.judge_source_file = request.FILES['game_judge']
            game.judge_lang = request.POST['judge_language']
            game.save()
            
            # Compile source file to directory with source file
            src = settings.MEDIA_ROOT + game.judge_source_file.name
            target = settings.MEDIA_ROOT + game.judge_source_file.name + '.bin' 
            lang = game.judge_lang
            compile(src, target, lang)

            # Use compiled file in object game
            f = File(open(target))
            game.judge_bin_file.save(request.POST['game_name'], f)

            # Save changes made to game object
            game.save()

            # Remove compiled file from directory with source
            system('rm ' + target)
            
            return HttpResponseRedirect('/')
    else:
        form = NewGameForm()
    return render_to_response('gaming/new_game.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))

def game_list(request):
    """
        Displays list of available games
    """
    games = Game.objects.all()
    return render_to_response('gaming/game_list.html',
            {
                'games': games,
            },
            context_instance=RequestContext(request))

def game_details(request, game_id):
    """
        Displays detailed information about game with id equal to game_id
        If game_id is not given or there is no Game object with id equal to game_id
        then Exception is thrown
    """
    if not game_id:
        raise Exception("In game_details: No game_id given")

    game = Game.objects.get(id=game_id)
    if game is None:
        raise Exception("In game_details: Wrong game_id given")

    return render_to_response('gaming/game_details.html',
            {
                'game': game,
            },
            context_instance=RequestContext(request))
