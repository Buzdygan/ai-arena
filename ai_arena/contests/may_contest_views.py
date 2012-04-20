from datetime import datetime
from os import system
from django.core.files import File
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect
from contests.forms import MayContestSendBotForTest

from ai_arena.contests.models import Bot, Game
from ai_arena import settings
from ai_arena.contests.compilation import compile
from ai_arena.contests.bot_views import create_bot_from_request
from ai_arena.contests.game_launcher import launch_single_match
from ai_arena.contests.may_contest_helper_functions import *

def downloads(request):
    """

    """
    return render_to_response('index.html',
            context_instance=RequestContext(request))

def my_results(request):
    return render_to_response('may_contest/results.html',
            context_instance=RequestContext(request))

def show_ladder(request):
    return render_to_response('index.html',
            context_instance=RequestContext(request))

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
            (exit_status, bot) = create_bot_from_request(request, getMayGame())
            if exit_status != 0:
                return render_to_response('error.html',
                        {
                            'error_details': bot,
                        },
                        context_instance = RequestContext(request))

            # Check is user uploaded also an opponent
            # If so - handle it
            if 'opponent_source' in request.FILES:
                (exit_status, opp) = create_bot_from_request(request, getMayGame(), bot_field='opponent_source')
                if exit_status != 0:
                    # error occured
                    return render_to_response('error.html',
                            {
                                'error_details': opp,
                            },
                            context_instance = RequestContext(request))
            # otherwise - use default bot as an opponent
            else: 
                opp = getDefaultMayContestBot()
            
            launch_single_match(getMayGame(), [bot, opp])
            
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
        
