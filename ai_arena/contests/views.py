from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    """
        Returns main template to render.
    """
    return render_to_response('index.html',
            context_instance=RequestContext(request))

