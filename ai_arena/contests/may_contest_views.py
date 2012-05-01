from datetime import datetime
from os import system
from django.core.files import File
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from contests.forms import MayContestSendBotForTest

from ai_arena.contests.models import Bot, Game, Match
from ai_arena import settings
from ai_arena.contests.compilation import compile
from ai_arena.contests.bot_views import create_bot_from_request, send_bot
from ai_arena.contests.game_launcher import launch_single_match
from ai_arena.contests.may_contest_helper_functions import *

def downloads(request):
    """

    """
    return render_to_response('index.html',
            context_instance=RequestContext(request))

@login_required
def my_results(request):
    matches = []#Match.objects.all() #[]
    for match in Match.objects.all():
        for mbr in match.players_results.all():
            if mbr.bot.owner == request.user:
                matches.append(match)

    return render_to_response('may_contest/results.html',
            {
                'matches': matches,
            },
            context_instance=RequestContext(request))

@login_required
def match_details(request, match_id):
    match = Match.objects.get(id=match_id)
    return render_to_response('may_contest/match_details.html',
            {
                'match': match,
#                'player1': match.objects.all()[0],
#                'player2': match.objects.all()[1],
            },
            context_instance=RequestContext(request))


def show_ladder(request):
    ranking = get_default_may_ranking()
    ladder = sorted(ranking.botranking_set.all(), key=lambda botranking: botranking.position)
    return render_to_response('may_contest/show_ranking.html',
            {
                'ranking': ranking,
                'ladder': ladder,
            },
            context_instance=RequestContext(request))

@login_required
def may_contest_send_bot(request):
    """
        This view is used when user wants to send bot from game details view.
        It is different from simple send bot view, because game is known, so there is
        no need to pick it form list.
    """

    game_id = get_may_game().id
    return send_bot(request, game_id)

@login_required
def testing(request):
    if request.method == 'POST':
        form = MayContestSendBotForTest(request.POST, request.FILES)
        if not form.is_valid():
            return render_to_response('may_contest/testing.html',
                    {
                        'form': form,
                    },
                    context_instance=RequestContext(request))
        else:
            # Handle a bot
            (exit_status, bot) = create_bot_from_request(request, get_may_game())
            if exit_status != 0:
                return render_to_response('error.html',
                        {
                            'error_details': bot,
                        },
                        context_instance = RequestContext(request))

            # Check is user uploaded also an opponent
            # If so - handle it
            if 'opponent_source' in request.FILES:
                (exit_status, opp) = create_bot_from_request(request, get_may_game(), bot_field='opponent_source')
                if exit_status != 0:
                    # error occured
                    return render_to_response('error.html',
                            {
                                'error_details': opp,
                            },
                            context_instance = RequestContext(request))
            # otherwise - use default bot as an opponent
            else: 
                opp = get_default_may_contest_bot()
            
            launch_single_match(get_may_game(), [bot, opp])
            
            return HttpResponseRedirect('/testing/uploaded/')

    else:
        form = MayContestSendBotForTest()
        return render_to_response('may_contest/testing.html',
            {
                'form': form,
            },
            context_instance=RequestContext(request))

def uploaded_for_tests(request):
    return render_to_response('may_contest/uploaded_for_testing.html',
            context_instance=RequestContext(request))

def contact(request):
    return render_to_response('may_contest/contact.html',
            context_instance=RequestContext(request))
        
