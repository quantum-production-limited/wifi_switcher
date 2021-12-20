from .nmcli_tools import connect_to_network_with_nmcli
from .netplan_tools import connect_to_network_with_netplan


def connect_to_network(ssid, password, path_to_netplan_yaml=None):
    if path_to_netplan_yaml is not None:
        connect_to_network_with_netplan(
            ssid, password, path_to_netplan_yaml
        )
        return False, 'Unable to check if connection succeeded when using netplan'
    else:
        return connect_to_network_with_nmcli(ssid, password)
