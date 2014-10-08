from django.shortcuts import render, HttpResponse ,render_to_response
from django.template import RequestContext
import json
#from django.utils import
# Create your views here.

def a1_index(request):
    if request.method == 'POST' and request.is_ajax():
        name = 'fang'
        city = 'ST'
        message = name + ' lives in ' + city
        print 'xxx'

        return render_to_response('a1/a1.html',json.dumps({'message': message}),\
context_instance=RequestContext(request))
    return render(request, 'a1/a1.html')
