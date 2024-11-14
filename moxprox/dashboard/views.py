from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def index(request):
        datacenter_name = "saladre"
        context = {"salade" : datacenter_name}
        return render(request, "dashboard/index.html", context)