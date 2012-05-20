from datetime import datetime
from os import system
from django.core.files import File
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from contests.forms import MayContestSendBotForTest, OnlineBotCreationForm

from ai_arena.contests.models import Bot, Game, Match
from ai_arena import settings
from ai_arena.contests.compilation import compile
from ai_arena.contests.bot_views import create_bot_from_request, send_bot_without_name
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
            if (mbr.bot.owner == request.user) & (match not in matches):
                matches.append(match)
    
    ranked_matches = []
    test_matches = []
    for match in matches:
        if match.ranked_match:
            ranked_matches.append(match)
        else:
            test_matches.append(match)

    return render_to_response('may_contest/results.html',
            {
                'ranked_matches': ranked_matches,
                'test_matches': test_matches,
            },
            context_instance=RequestContext(request))

@login_required
def match_details(request, match_id):
    match = Match.objects.get(id=match_id)
    return render_to_response('may_contest/match_details.html',
            {
                'match': match,
                'user': request.user,
#                'player1': match.objects.all()[0],
#                'player2': match.objects.all()[1],
            },
            context_instance=RequestContext(request))


def show_ladder(request):
    ranking = generate_ranking() 
    if ranking:
        ladder = sorted(ranking.botranking_set.all(), key=lambda botranking: botranking.position)
    else:
        ladder = []
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
    may_contest = get_default_may_contest()
    if may_contest.ranking:
        may_contest.ranking.updated = False
        may_contest.ranking.save()
    return send_bot_without_name(request, game_id)

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
            (exit_status, logs, bot) = create_bot_from_request(request, get_may_game(), testing=True)
            if exit_status != 0:
                return render_to_response('error.html',
                        {
                            'error_details': logs,
                        },
                        context_instance = RequestContext(request))

            # Check is user uploaded also an opponent
            # If so - handle it
            if 'opponent_source' in request.FILES:
                (exit_status, logs, opp) = create_bot_from_request(request, get_may_game(), bot_field='opponent_source', testing=True)
                if exit_status != 0:
                    # error occured
                    return render_to_response('error.html',
                            {
                                'error_details': logs,
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
                'judge_path': settings.MAY_CONTEST_EXAMPLE_JUDGE_PATH,
                'bot_path': settings.MAY_CONTEST_EXAMPLE_BOT_PATH,
                'judge_manual_path': settings.MAY_CONTEST_JUDGE_MANUAL_PATH,
            },
            context_instance=RequestContext(request))

def uploaded_for_tests(request):
    return render_to_response('may_contest/uploaded_for_testing.html',
            context_instance=RequestContext(request))

def contact(request):
    return render_to_response('may_contest/contact.html',
            context_instance=RequestContext(request))

def online_bot_uploaded(request, bot_name):
    return render_to_response('may_contest/online_bot_uploaded.html',
            {
                'bot_name': bot_name,
            },
            context_instance=RequestContext(request))

@login_required
def online_bot_creation(request):
    """
        Page where everyone can prepare bot online and submit it to contest.
    """

    default_bot_codes = get_default_bot_codes()
    code_names = settings.PICNIC_DEFAULT_BOTS_NAMES
    user = request.user 
    may_contest = get_default_may_contest()
    if may_contest.ranking:
        may_contest.ranking.updated = False
        may_contest.ranking.save()
    if request.method == 'POST':
        form = OnlineBotCreationForm(request.POST, initial=default_bot_codes)
        if not form.is_valid():
            return render_to_response('may_contest/online_bot_creation.html',
                    {
                        'form': form,
                        'code_names': code_names,
                    },
                    context_instance=RequestContext(request))
        else:
            source_code = request.POST['code']
            error_log = create_bot_and_add_to_contest(bot_name=bot_name, source_code=source_code,
                    owner=user, contest=may_contest, bot_language=settings.PICNIC_DEFAULT_LANGUAGE)
            if error_log:
                return render_to_response('error.html',
                        {
                            'error_details': error_log,
                        },
                        context_instance = RequestContext(request))
            return HttpResponseRedirect('/ladder/')
    else:
        form = OnlineBotCreationForm(initial=default_bot_codes)
        return render_to_response('may_contest/online_bot_creation.html',
            {
                'form': form,
                'code_names': code_names,
            },
            context_instance=RequestContext(request))
        
