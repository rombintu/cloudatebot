from internal import api
from datetime import datetime 
import os
from io import StringIO

from dotenv import load_dotenv
from dotenv import dotenv_values
load_dotenv()

osapi = api.OpenStackApi()

class Server:
    ifaces = []
    hypervisor = ""
    status = ""
    def __init__(self, base):
        self.base = base
        self.updated = datetime.now()
        try:
            self.vnc_url = base.get_console_url("novnc")["console"]["url"]
        except:
            self.vnc_url = "https://docs.openstack.org/nova/latest/admin/remote-console-access.html"
        self.refresh_info()

    def refresh_info(self):
        if self.base._info["addresses"]:
            self.ifaces = [{net: [a["addr"] for a in addrs]} for net, addrs in self.base._info["addresses"].items()]
        self.hypervisor = self.base._info["OS-EXT-SRV-ATTR:host"]
        self.status = self.base._info["status"]
        self.key_name = self.base._info["key_name"]
    
    def get_pretty_info(self):
        info = f"Имя: `{self.base.name}`"
        info += f"\nID: `{self.base.id}`\n"
        if self.ifaces:
            for net in self.ifaces:
                for name, addrs in net.items():
                    info += f"\nIP сеть: *{name}* "
                    info += ','.join(f"`{a}`" for a in addrs)
        else:
            info += "\IP: Нет"
        info += f"\nГипервизор: `{self.hypervisor}`"
        info += f"\nКлючевая пара: *{self.key_name}* 🔑"
        info += f"\nСтатус: {self.get_pretty_status(self.status)}"
        info += f"\nОбновлено: {self.updated.strftime('%d %B в %H:%M:%S')} ⌛️"
        return info

    def get_pretty_status(self, status):
        if status.lower() == "shutoff":
            return f"*{status}* ⛔️"
        elif status.lower() == "active":
            return f"*{status}* ✅"
        else:
            return f"*{status}* ⚠️"

class User:
    access = False
    creds: bytes
    def __init__(self, uuid, username):
        self.uuid = uuid
        self.username = username
    
    def set_creds(self, creds):
        self.creds = creds
    
    def get_creds(self):
        return self.creds

    def get_env(self):
        creds = self.get_creds()
        if not creds:
            return {}
        return dotenv_values(stream=StringIO(creds.decode()))
        
     

class MEM:
    admins = [int(os.environ["BOT_ADMIN"])]
    services = []
    servers = []
    users = []

    def __init__(self) -> None:
        self.refresh_servers()
        self.refresh_services()

    def login_check(self, uuid):
        for user in self.users:
            if uuid == user.uuid:
                return True
        for admin in self.admins:
            if uuid == admin:
                return True
        return False

    def login(self, user):
        self.users.append(user)

    def logout(self, user):
        for i, luser in enumerate(self.users):
            if luser.uuid == user.uuid:
                self.users.pop(i)

    def refresh_servers(self):
        servers, err = osapi.server_list()
        if err:
            print(err)
            return
        # REFRESH CACHE
        self.servers = servers

    def refresh_services(self):
        services, err = osapi.service_list()
        if err:
            print(err)
            return
        # REFRESH CACHE
        self.services = services

    def server_find(self, _id):
        for s in self.servers:
            if _id == s.id:
                return Server(s)
        return None

    def services_info(self):
        info = "\n"
        for s in self.services:
            info += f"\n{s.id}. {s.zone} *{s.binary}* {'✅' if s.state == 'up' else '⛔️'}"
        return info