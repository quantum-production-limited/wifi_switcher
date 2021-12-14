# WiFi Switcher
A simple tool to update a netplan YAML file with a new WiFi SSID and password, then connect
to it.

A function is provided with the below signature:
```python
connect_to_network(ssid, password, path_to_netplan_yaml)
```

Executing this function will:
- Look for a file at `path_to_netplan_yaml` and parse the YAML inside it.
- Overwrite the `Network.wifis.wlan0.access-points` node with the `ssid` and `password`
provided. Any existing SSIDs and passwords will be replaced, not added to.
- If the file doesn't contain the nested key `Network.wifis.wlan0`, then it will be
created and assigned the default values below (`dhcp4: true` and basic settings for the
`ssid` and `password`)
- If the file doesn't exist at all, then it will be created (as well as creating the full
folder path), with the settings below.

```yaml
Network:
  version: 2
  wifis:
    wlan0:
      access-points:
        your_ssid:
          password: your_password
      dhcp4: true
```

##Installation:

`pip install git+https://github.com/quantum-production-limited/wifi_switcher.git`

##Usage:

```python
from wifi_switcher.wifi_switcher import connect_to_network

# Optional: set up logging to print to stdout
import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

# All-in-one function to connect to a network
connect_to_network('ssid', 'password', 'full_path_to_netplan_yaml_file')

# Alternatively, just update the netplan yaml file:
from wifi_switcher.wifi_switcher import update_netplan_settings
update_netplan_settings('ssid', 'password', 'full_path_to_netplan_yaml_file')

# Then generate & apply the changes (using `netplan generate` then `netplan apply`):
from wifi_switcher.wifi_switcher import generate_and_apply_netplan_changes
generate_and_apply_netplan_changes()
```
 