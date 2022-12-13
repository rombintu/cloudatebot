from internal import api
from datetime import datetime 

osapi = api.OpenStackApi()

class Server:
    ifaces = []
    hypervisor = ""
    status = ""

    def __init__(self, base):
        self.base = base
        self.refresh_info()

    def refresh_info(self):
        if self.base._info["addresses"]:
            self.ifaces = [{net: [a["addr"] for a in addrs]} for net, addrs in self.base._info["addresses"].items()]
        self.hypervisor = self.base._info["OS-EXT-SRV-ATTR:host"]
        self.status = self.base._info["status"]
        self.key_name = self.base._info["key_name"]
        # self.status = self.base._info[""]
    
    def get_pretty_info(self):
        # info = f"Имя: {self.base.name.replace('_', '-')}"
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
        info += f"\nКлючевая пара: *{self.key_name}*"
        info += f"\nСтатус: {self.get_pretty_status(self.status)}"
        return info

    def get_pretty_status(self, status):
        if status.lower() == "shutoff":
            return f"*{status}* ⛔️"
        elif status.lower() == "active":
            return f"*{status}* ✅"
        else:
            return f"*{status}* ⚠️"

class MEM:
    servers = []
    updated = datetime.now()

    def refresh_servers(self):
        servers, err = osapi.server_list()
        if err:
            print(err)
            return
        # REFRESH CACHE
        self.servers = servers
        self.updated = datetime.now()

    def server_find(self, _id):
        for s in self.servers:
            if _id == s.id:
                return Server(s)
        return None

    # def server_info(self, server):
        
            
    #     return info