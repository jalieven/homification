import netifaces


class Nic:
    def __init__(self):
        pass

    def get_current_address(self):
        interfaces = netifaces.interfaces()
        for i in interfaces:
            if i == 'lo':
                continue
            iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
            if iface is not None:
                for j in iface:
                    if j['addr'] != '127.0.0.1':
                        return j['addr']
            else:
                return None


