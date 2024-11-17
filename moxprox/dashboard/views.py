from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import DashboardDatacenter, DashboardNode, DashboardDomain
from django.http import JsonResponse
from .back.constant import Protocol
from .back.node import Node
import platform
import json
import ast
import threading

# Create your views here.
def index(request):
        local_node = Node.factory("127.0.0.1", Protocol.LOCALHOST, "root", "root")
        local_node.remote_update()

        current_node = platform.node()

        remote_dc = (DashboardDatacenter.objects.all())[0]
        remote_node = DashboardNode.objects.filter(datacenter_id=remote_dc.id)
        remote_domain = DashboardDomain.objects.all()       

        context = {"nodes" : remote_node, "domains": remote_domain}
        return render(request, "dashboard/index.html", context)

def refresh(request):
        print("refresh")
        local_node = Node.factory("127.0.0.1", Protocol.LOCALHOST, "root", "root")
        print("before update")
        local_node.remote_update()
        print("after update")

        remote_dc = (DashboardDatacenter.objects.all())[0]
        remote_node = DashboardNode.objects.filter(datacenter_id=remote_dc.id)
        remote_domain = DashboardDomain.objects.all()
        print("after querying")

        data = {
        "nodes": [
                {
                "id": node.id,
                "name": node.name,
                "ip": node.ip,
                "domains": [
                        {
                        "id": domain.id,
                        "name": domain.name,
                        "uuid": str(domain.uuid),
                        "status": domain.status,
                        "current_ram": domain.current_ram,
                        "max_ram": domain.max_ram,
                        "vcpus": domain.vcpus,
                        "vnc_port": domain.vnc_port,
                        "proxy_port": domain.proxy_port,
                        }
                        for domain in remote_domain if domain.node_id == node.id
                ]
                }
                for node in remote_node
        ]
        }
        
        return JsonResponse(data)

def start_domain(request):
        if request.method == "POST":
                dict_body = ast.literal_eval((request.body).decode("UTF-8"))
                domain_uuid = dict_body['uuid']
                action = dict_body['action']
                manage_domain_back(domain_uuid, action)
                # thread = threading.Thread(target=manage_domain_back, daemon=True, args=(domain_uuid, 'create_domain'))
                # thread.start()

                return JsonResponse({"success": f"Domaine {domain_uuid} démarré"})
        return JsonResponse({"error": "Request not POST"}, status=400)

def manage_domain_back(domain_uuid, action):
        if not domain_uuid:
                return JsonResponse({"error": "UUID manquant"}, status=400)

        node_owner_of_domain = (DashboardNode.objects.filter(id=(DashboardDomain.objects.filter(uuid=domain_uuid)[0]).node_id))[0]
        ip = node_owner_of_domain.ip
        node_owner_of_domain = None
        Node.manage_domain(ip, domain_uuid, action)
        