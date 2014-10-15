from django.shortcuts import render, HttpResponse ,render_to_response
from django.template import RequestContext
import json
#from django.utils import
# Create your views here.

def render_to_json(dic):
    return HttpResponse(json.dumps(dic))

def a1_index(request):
    if request.method == 'POST' and request.is_ajax():
        name = 'Fang'
        city = 'ST'
        message = name + ' lives in ' + city


        dic = dict(message = message, address = 'BeiJing')
        return render_to_json(dic)
    return render(request, 'a1/a1.html')

def a2(request):
    if request.method == 'POST' and request.is_ajax():
        name = 'Fang'
        city = 'ST'
        message = name + ' lives in ' + city


        dic = dict(message = message, address = 'BeiJing')
        return render_to_json(dic)
    return render(request, 'a1/a2.html')
