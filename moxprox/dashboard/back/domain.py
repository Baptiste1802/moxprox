import libvirt
from xml.dom import minidom
import threading
import time
import subprocess

class Domain:
    proxy_port = 6080
    websockify_pid = dict()

    def __init__(self, vir_domain=None, conn=None):
        self.virtuel_domain = vir_domain
        self.name           = self.virtuel_domain.name()
        self.conn           = conn
        self.status_event   = threading.Event()
        self.uuid           = self.virtuel_domain.UUIDString()
        self.vnc_port       = self.get_vnc_port()
        self.proxy_port     = Domain.determine_proxy_port(self.vnc_port)
        self.mac_address    = self.get_mac_address()

    @staticmethod
    def determine_proxy_port(vnc_port):
        if vnc_port != -1:
            print(vnc_port)
            print("before for proxy loop")
            for key in Domain.websockify_pid.keys():
                print(key)
                if Domain.websockify_pid[key]["vnc"] == vnc_port:
                    print("before return")
                    return key

            print("after for proxy loop")
            
            is_okay = False
            while not is_okay:
                current_try_port = Domain.proxy_port+1
                Domain.proxy_port = current_try_port

                cmd = f"netstat -tn |grep {current_try_port}"
                netstat = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                output = str(netstat.communicate()[0])
                if f"{current_try_port}" not in str(output):
                    is_okay = True

            return current_try_port

    def update_domain(self):
        self.virtuel_domain = self.conn.lookupByName(self.name)

    def get_status(self):
        if self.virtuel_domain is None:
            self.update_domain()

        if self.virtuel_domain is not None:
            return "Active" if self.virtuel_domain.isActive() else "Inactive"
        
        return "Indisponible"

    def get_status_bool(self):
        if self.virtuel_domain is None:
            self.update_domain()

        if self.virtuel_domain is not None:
            return self.virtuel_domain.isActive()

    def get_ram_info(self):
        if self.get_status_bool():
            return (self.virtuel_domain.memoryStats())["rss"]
        else:
            return 0

    def get_id(self):
        if self.virtuel_domain.isActive():
            return (self.virtuel_domain.ID())
        else:
            return -1
            
    def get_max_memory(self):
        return (self.virtuel_domain.maxMemory())
    
    def get_max_vcpu(self):
        return self.virtuel_domain.maxVcpus()
    
    def shutdown_domain(self):
        if self.get_status_bool():
            self.virtuel_domain.shutdown()

    def destroy_domain(self):
        if self.get_status_bool():
            self.virtuel_domain.destroy()

    def create_domain(self):
        if not self.get_status_bool():
            self.virtuel_domain.create()

    def restart_domain_unblock(self):
        self.status_event.clear()
        try:
            self.virtuel_domain.destroy()
            while self.get_status_bool():
                time.sleep(0.5)
            
            self.virtuel_domain.create()

            while not self.get_status_bool(): 
                time.sleep(0.5)
            self.status_event.set()
        except Exception as e:
            self.status_event.set()

    def get_vnc_port(self):
        if self.get_status_bool:
            try:
                result = subprocess.run(
                    ["virsh" f" vncdisplay {self.uuid}"], capture_output=True, text=True, shell=True
                )

                vnc_port = None
                stdout   = ((result.stdout.splitlines()[0]).split(":"))
                if len(stdout) > 1:
                    vnc_port = int(stdout[1]) + 5900
                
                return vnc_port

            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'exécution de la commande : {e}")
                return -1
        return -1


    def restart_domain(self):
        self.status_event.clear()
        thread = threading.Thread(target=self.restart_domain_unblock)
        thread.daemon = True
        thread.start()
        self.status_event.wait()

    def get_vcpu(self):
        raw_xml = self.virtuel_domain.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        vcpu_elements = xml.getElementsByTagName('vcpu')
        if vcpu_elements and vcpu_elements[0].firstChild:
            return int(vcpu_elements[0].firstChild.nodeValue)
        else:
            raise Exception("Impossible de récupérer la valeur de la balise <vcpu>")

    def get_mac_address(self):
        raw_xml = self.virtuel_domain.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        try:
            interfaces = xml.getElementsByTagName("interface")
            for interface in interfaces:
                mac_elements = interface.getElementsByTagName("mac")
                if mac_elements:
                    mac_address = mac_elements[0].getAttribute("address")
                    if mac_address:
                        return mac_address
            return None
        except Exception as e:
            print(f"Erreur lors de l'analyse du XML : {e}")
            return None


    def print_disk(self):
        raw_xml = self.virtuel_domain.XMLDesc(0)
        xml = minidom.parseString(raw_xml)
        diskTypes = xml.getElementsByTagName('disk')
        for diskType in diskTypes:
            print('disk: type='+diskType.getAttribute('type')+' device='+diskType.getAttribute('device'))
            diskNodes = diskType.childNodes
            for diskNode in diskNodes:
                if diskNode.nodeName[0:1] != '#':
                    print('  '+diskNode.nodeName)
                    for attr in diskNode.attributes.keys():
                        print('    '+diskNode.attributes[attr].name+' = '+
                         diskNode.attributes[attr].value)