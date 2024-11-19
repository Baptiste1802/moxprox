from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import DashboardDatacenter, DashboardNode, DashboardDomain
from django.http import JsonResponse
from .back.constant import Protocol
from .back.node import Node
from django_mysql.exceptions import TimeoutError
from django_mysql.locks import Lock

import platform
import json
import ast
import threading

# Create your views here.
def index(request):
        local_node    = None
        remote_node   = None
        remote_domain = None

        try:
                with Lock("cloud_lock", acquire_timeout=5.0):
                        local_node = Node.factory("127.0.0.1", Protocol.LOCALHOST, "root", "root")
                        local_node.remote_update()

                        remote_dc = (DashboardDatacenter.objects.all())[0]
                        remote_node = DashboardNode.objects.filter(datacenter_id=remote_dc.id)
                        remote_domain = DashboardDomain.objects.all()       
        except TimeoutError:
                print("Could not get the lock")

        context = {"nodes" : remote_node, "domains": remote_domain}
        return render(request, "dashboard/index.html", context)

def refresh(request):
        local_node    = None
        remote_node   = None
        remote_domain = None

        try:
                with Lock("cloud_lock", acquire_timeout=2.0):
                        local_node = Node.factory("127.0.0.1", Protocol.LOCALHOST, "root", "root")
                        local_node.remote_update()

                        remote_dc     = (DashboardDatacenter.objects.all())[0]
                        remote_node   = DashboardNode.objects.filter(datacenter_id=remote_dc.id)
                        remote_domain = DashboardDomain.objects.all()
        except TimeoutError:
                print("Could not get the lock")

        data = {
        "nodes": [
                {
                "id": node.id,
                "name": node.name,
                "ip": node.ip,
                "domains": [
                        {
                        "id"         : domain.id,
                        "name"       : domain.name,
                        "uuid"       : str(domain.uuid),
                        "status"     : domain.status,
                        "current_ram": domain.current_ram,
                        "max_ram"    : domain.max_ram,
                        "vcpus"      : domain.vcpus,
                        "vnc_port"   : domain.vnc_port,
                        "proxy_port" : domain.proxy_port,
                        "mac_address": domain.mac_address
                        }
                        for domain in remote_domain if domain.node_id == node.id
                ]
                }
                for node in remote_node
        ]
        }
        
        return JsonResponse(data)

def manage_domain(request):
        if request.method == "POST":
                dict_body = ast.literal_eval((request.body).decode("UTF-8"))
                domain_uuid = dict_body['uuid']
                action = dict_body['action']

                try:
                        with Lock("cloud_lock", acquire_timeout=2.0):
                                manage_domain_back(domain_uuid, action)
                except TimeoutError:
                        print("Could not get the lock")
                        return JsonResponse({"error": "Request not POST"}, status=400)

                return JsonResponse({"success": f"Domaine {domain_uuid} démarré"})
        return JsonResponse({"error": "Request not POST"}, status=400)

def manage_domain_back(domain_uuid, action):
        if not domain_uuid:
                return JsonResponse({"error": "UUID manquant"}, status=400)

        node_owner_of_domain = (DashboardNode.objects.filter(id=(DashboardDomain.objects.filter(uuid=domain_uuid)[0]).node_id))[0]
        ip = node_owner_of_domain.ip
        node_owner_of_domain = None
        Node.manage_domain(ip, domain_uuid, action)

def create_vm(request):
        if request.method == "POST":
                dict_body = ast.literal_eval((request.body).decode("UTF-8"))
                name         = dict_body["name"        ]
                node_id      = dict_body["node_id"     ]
                memory       = int(dict_body["memory"      ])
                disk_size    = dict_body["disk_size"   ]
                vcpus_number = dict_body["vcpus_number"]

                if Node.new_vm(name, node_id, memory, disk_size, vcpus_number):
                        refresh(None)
                        return JsonResponse({"success": "VM in creation"})
        return JsonResponse({"error": "An error occured while creation of the VM"})
