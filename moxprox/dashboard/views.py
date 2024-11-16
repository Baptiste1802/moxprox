from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import DashboardDatacenter, DashboardNode, DashboardDomain

from .back.constant import Protocol
from .back.node import Node
import platform

# Create your views here.
def index(request):
        local_node = Node.factory("127.0.0.1", Protocol.LOCALHOST, "root", "root")

        current_node = platform.node()

        remote_dc = (DashboardDatacenter.objects.all())[0]
        remote_node = DashboardNode.objects.filter(datacenter_id=remote_dc.id)
        remote_domain = DashboardDomain.objects.all()       

        print(remote_dc)
        context = {"nodes" : remote_node, "domains": remote_domain}
        return render(request, "dashboard/index.html", context)

def dc(request):
        return HttpResponse("This is a test")