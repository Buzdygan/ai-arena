from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    """
        Returns main template to render.
    """
    return render_to_response('index.html',
            context_instance=RequestContext(request))

def error(request):
    """
        Shows standard error page when an error occurs 
        (e.g. during compilation)
    """
    return render_to_response('error.html',
            context_instance=RequestContext(request))
