from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from contests.forms import MayContestSendBotForTest

def downloads(request):
    """

    """
    return render_to_response('index.html',
            context_instance=RequestContext(request))

def my_results(request):
    return render_to_response('index.html',
            context_instance=RequestContext(request))

def show_ladder(request):
    return render_to_response('index.html',
            context_instance=RequestContext(request))

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

            # Check is user uploaded also an opponent
            # If so - handle it

            # otherwise - use default one

            # Schedule play
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
    return render_to_response('index.html',
            context_instance=RequestContext(request))
        
