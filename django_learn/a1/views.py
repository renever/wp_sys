from django.shortcuts import render, render_to_response
from django.template import RequestContext
# Create your views here.

def a1_index(request):
    context = {}

    return render_to_response('a1/a1.html',context,
                context_instance=RequestContext(request),
            )
