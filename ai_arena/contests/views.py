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
                context_instance=RequestContext(request));
