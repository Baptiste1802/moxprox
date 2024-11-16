from ..models import DashboardNode, DashboardDomain

import libvirt
import sys
from .constant import *
from .domain import Domain
from urllib.parse import urlparse
import platform

from websockify import WebSocketProxy
from multiprocessing import Process

class Node:
    def __init__(self, conn):
        self.conn    = conn
        self.ip      = self.get_node_ip()
        self.domains = []
        self.load_domain()
        self.name = platform.node()
        self.remote_update()

    @staticmethod
    def run_websockify(vnc_port, websocket_port, host="0.0.0.0"):
        server = WebSocketProxy(
            target_host="127.0.0.1",
            target_port=vnc_port,
            listen_host=host,
            listen_port=websocket_port,
            web="/usr/share/novnc/",
            daemon=False
        )
        server.start_server()

    def remote_update(self):
        remote_current_node = (DashboardNode.objects.filter(name=self.name))[0]
        remote_current_domain = DashboardDomain.objects.filter(node_id=remote_current_node.id)

        self.load_domain()
        
        # Création des domaines en base et gestion des proxy
        for local_domain in self.domains:
            create = True
            for remote_domain in remote_current_domain:
                if remote_domain.uuid == local_domain.uuid:
                    create = False
            if create:
                dd = DashboardDomain(id=local_domain.get_id(), name=local_domain.name, uuid=local_domain.uuid, status=local_domain.get_status(), max_ram=local_domain.get_max_memory(), current_ram=local_domain.get_ram_info(), vcpus=local_domain.get_vcpu(), vnc_port=local_domain.get_vnc_port(), proxy_port=local_domain.proxy_port, node_id=remote_current_node.id, ip="")
                dd.save()

                if f"{local_domain.proxy_port}" in Domain.websockify_pid:
                    try:        # Ajoutez votre logique ici

                        Domain.websockify_pid[f"{local_domain.proxy_port}"].terminate()
                    except Exception as e:
                        print("Terminate websockify didn't work properly")

                    Domain.websockify_pid.pop(f"{local_domain.proxy_port}")

                Domain.websockify_pid[f"{local_domain.proxy_port}"] = Process(target=Node.run_websockify, args=(local_domain.vnc_port, local_domain.proxy_port, "0.0.0.0"))
                Domain.websockify_pid[f"{local_domain.proxy_port}"].start()

        # Suppression des domaines en base et gestion des proxy
        for remote_domain in remote_current_domain:
            delete = True
            for local_domain in self.domains:
                if remote_domain.uuid == local_domain.uuid:
                    delete = False
            if delete:
                remote_domain.delete()
                Domain.websockify_pid[f"{remote_domain.proxy_port}"].terminate()
                Domain.websockify_pid.pop(f"{remote_domain.proxy_port}")


    def end_node(self):
        for domain in self.domains:
            if domain.conn == self.conn:
                self.domains.remove(domain)
        self.conn.close()

    def load_domain(self):
        domains = None
        domains = self.conn.listAllDomains()

        if len(domains) != 0:
            for domain in domains:
                append = True
                for local_domain in self.domains:
                    if domain.UUIDString() == local_domain.uuid:
                        append = False
                if append:
                    self.domains.append(Domain(domain, self.conn))
            
            for local_domain in self.domains:
                remove = True
                for domain in domains:
                    if domain.UUIDString() == local_domain.uuid:
                        remove = False
                if remove:
                    self.domains.remove(domain)                

    def shutdown_domain(self, id):
        if id >= 0:
            for domain in self.domains:
                if domain.close_domain(id):
                    return True
                
        return False
    
    def destroy_domain(self, id):
        if id >= 0:
            for domain in self.domains:
                if domain.close_domain(id):
                    return True
                
        return False
    
    def create_domain(self, id):
        for domain in self.domains:
            if domain.virtuel_domain.ID() == id:
                domain.create_domain()

    def get_node_ip(self):
        return urlparse(self.conn.getURI()).hostname

    @staticmethod
    def factory(ip, protocol, user="", password=""):
        strAuthentication = ""

        match protocol:
            case Protocol.SECURESHELL:
                user_prefix = f"{user}@" if user else ""
                str_authentication = f"qemu+ssh://{user_prefix}{ip}/system"
            case Protocol.LOCALHOST:
                str_authentication = "qemu+tcp://localhost/system"
            case _:
                raise ValueError(f"Unknown protocol: {protocol}")

        # Méthode d'authentification
        auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], lambda credentials, user_data: 0, None]

        # Connexion
        conn = libvirt.openAuth(str_authentication, auth, 0)
        if not conn:
            raise Exception("Could not connect to node")

        return Node(conn)

