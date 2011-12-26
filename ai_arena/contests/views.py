from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from nadzorca import nadzorca

def index(request):
    return render_to_response('index.html')

def send(request):
    return render_to_response('send/send.html',
            context_instance=RequestContext(request))

def results(request):
    try:
        lang1 = request.POST['lang1']
        prog1 = request.POST['prog1']
        lang2 = request.POST['lang2']
        prog2 = request.POST['prog2']

        # Here we can perform a play
        
        i = nadzorca.costam()
    except KeyError:
        return render_to_response('send/send.html',
                {
                    'error_message': 'You must fill all the fields',
                },
                context_instance=RequestContext(request));
    else:
        return render_to_response('send/results.html',
                {
                    'lang1':lang1,
                    'prog1':prog1,
                    'lang2':lang2,
                    'prog2':prog2,
                    'i':i,
                },
                context_instance=RequestContext(request))

from ai_arena.contests.forms import GameSelectForm, BotSelectForm
from ai_arena.contests.models import Game, Bot

def launch_match(request):

    bot_form = None
    game_form = None
    game = None
    bot = None
    if request.method == 'POST':

        if 'game_form' in request.POST:
            game_form = GameSelectForm(request.POST, prefix='game')
            if game_form.is_valid():
                game = game_form.cleaned_data['game_field']
                bot_form = BotSelectForm(game=game)

        if 'bot_form' in request.POST:
            bot_form = BotSelectForm(request.POST, game=game, prefix='bot')
            if bot_form.is_valid():
                bot = bot_form.cleaned_data['bot_field']
                print(bot.name)

    if not game_form:
        game_form = GameSelectForm()

    return render_to_response('gaming/launch_match.html',
            {
                'game_form':game_form,
                'bot_form':bot_form,
            },
            context_instance=RequestContext(request)
        )
