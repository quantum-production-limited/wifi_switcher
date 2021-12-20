# WiFi Switcher
A simple tool to update a netplan YAML file with a new WiFi SSID and password, then connect
to it.

A function is provided with the below signature:
```python
connect_to_network(ssid, password, path_to_netplan_yaml=None)
```

If the `path_to_netplan_yaml` argument is provided, then `netplan` will be used to connect to the
network. Otherwise, `nmcli` is used.

## Installation:

`pip install git+https://github.com/quantum-production-limited/wifi_switcher.git`

## Usage:

```python
from wifi_switcher.wifi_switcher import connect_to_network

# Optional: set up logging to print to stdout
import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# All-in-one function to connect to a network using netplan:
connect_to_network('ssid', 'password', '/full/path_to/netplan_yaml_file.yaml')

# Alternatively, using nmcli:
success, message = connect_to_network('ssid', 'password')
if success:
    # Do something when the connection attempt succeeds
    pass
else:
    # Do something when the connection attempt fails
    pass
```

## Using netplan
If you provide a value for the `path_to_netplan_yaml` argument, then the module will attempt to
connect to a network using netplan.

Executing this function will:
- Look for a file at `path_to_netplan_yaml` and parse the YAML inside it.
- Overwrite the `network.wifis.wlan0.access-points` node with the `ssid` and `password`
provided. Any existing SSIDs and passwords will be replaced, not added to.
- If the file doesn't contain the nested key `network.wifis.wlan0`, then it will be
created and assigned the default values below (`dhcp4: true` and basic settings for the
`ssid` and `password`)
- If the file doesn't exist at all, then it will be created (as well as creating the full
folder path), with the settings below.
- The function returns a 2-tuple, to match the signature used when connecting via `nmcli`.
However, it will always return `False` as the first argument because currently we're not able
to check whether a connection attempt succeeded when using netplan.

```yaml
network:
  version: 2
  wifis:
    wlan0:
      access-points:
        your_ssid:
          password: your_password
      dhcp4: true
```

## Using nmcli
If you don't provide an argument for `path_to_netplan_yaml`, then the module will attempt to connect
using nmcli.

If the requested SSID is not in the list of available networks, then a network scan will be performed to
try to find it and then the connection attempt will be repeated.

The function returns a 2-tuple where the first element is a 
boolean showing whether the connection attempt succeeded, and the second is a string containing the
success/error message.
 