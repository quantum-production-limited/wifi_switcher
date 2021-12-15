import yaml
import os
import subprocess
import logging

from .exceptions import ExitStatusException

logger = logging.getLogger()


class NetplanYamlUpdater:
    _default_wlan0 = {
        'access-points': {},
        'dhcp4': True
    }

    def __init__(self, path_to_netplan_file):
        self.path_to_netplan_file = path_to_netplan_file
        self.netplan_settings = None
        self._load_netplan_settings()

    def _load_netplan_settings(self):
        """Opens the YAML file at self.path_to_netplan_file and parses it using PyYAML.

        If the file is not found, instead returns an empty dict. If the file is found but is parsed into an object other
        than a dict, a TypeError is raised.

        self.netplan_settings will be set to the returned dict.

        :return: The loaded yaml file, if it is found. Otherwise, an empty dict.
        :rtype: dict
        :raises: TypeError
        """
        try:
            with open(self.path_to_netplan_file, 'r') as f:
                data = f.read()
                logger.debug(f'Opened existing netplan settings at {self.path_to_netplan_file}')
        except FileNotFoundError:
            data = None
            logger.debug(f'No netplan settings found at {self.path_to_netplan_file}')

        if data:
            parsed_data = yaml.safe_load(data)
            logger.debug(f'Parsed netplan settings: {parsed_data}')
            if isinstance(parsed_data, dict):
                self.netplan_settings = parsed_data
                logger.info(f'Successfully opened & parsed netplan settings at {self.path_to_netplan_file}')
            else:
                raise TypeError(f'The YAML file at {self.path_to_netplan_file} does not parse into a Python dictionary,'
                                f' so it cannot be loaded. The file parsed as: {type(parsed_data)}')

        else:
            self.netplan_settings = {}
            logger.info(f'No existing netplan settings found at {self.path_to_netplan_file}, starting from blank'
                        f' settings.')

        return self.netplan_settings

    def _get_or_create_wlan0_settings(self):
        """Gets the wlan0 settings from the netplan settings, or creates default settings if none exist.

        Attempts to return self.netplan_settings['network']['wifis']['wlan0']. If any of those keys don't exist,
        they will be created and a default value for wlan0 will be created:
        {'wlan0': 'access-points': {}, 'dhcp4': True}

        :return: The wlan0 settings from self.netplan_settings
        :rtype: dict
        """
        if self.netplan_settings is None:
            self._load_netplan_settings()
        return self.netplan_settings.setdefault(
            'network', {'version': 2}
        ).setdefault(
            'wifis', {}
        ).setdefault(
            'wlan0', self._default_wlan0
        )

    def set_wlan0_access_point(self, ssid, password):
        """Replaces the current access point(s) under wlan0 with the provided ssid/password"""
        access_points = self._get_or_create_wlan0_settings()['access-points']

        for key in list(access_points.keys()):
            access_points.pop(key)
            logger.debug(f'Removed existing access point: {key}')

        access_points[ssid] = {'password': password}
        logger.info(f'Added access point to wlan0: {ssid}')

        return access_points

    def save(self):
        """Dumps self.netplan_settings to a YAML file at the location in self.path_to_netplan_file"""
        # Create the folder tree if it doesn't exist already
        folder = os.path.dirname(self.path_to_netplan_file)
        if folder:
            os.makedirs(folder, exist_ok=True)
            logger.debug(f'Folder did not exist, but was created: {folder}')

        # Save the yaml file
        with open(self.path_to_netplan_file, 'w') as f:
            yaml.dump(self.netplan_settings, f)
            logger.info(f'Saved new netplan settings to disk at {self.path_to_netplan_file}')


def update_netplan_settings(ssid, password, path_to_netplan_yaml):
    netplan = NetplanYamlUpdater(path_to_netplan_yaml)

    netplan.set_wlan0_access_point(ssid, password)
    netplan.save()


def generate_and_apply_netplan_changes():
    generate_command = ['netplan', 'generate']
    generate_result = subprocess.run(generate_command, capture_output=True)
    if generate_result.returncode != 0:
        raise ExitStatusException(f'Non-zero exit status was generated from command {generate_command}.'
                                  f' Exit status code: {generate_result.returncode}.\nError message:\n'
                                  f'{generate_result.stderr.decode("utf-8")}')
    else:
        apply_command = ['netplan', 'apply']
        apply_result = subprocess.run(apply_command, capture_output=True)
        if apply_result.returncode != 0:
            raise ExitStatusException(f'Non-zero exit status was generated from command {apply_command}.'
                                      f' Exit status code: {apply_result.returncode}.\nError message:\n'
                                      f'{apply_result.stderr.decode("utf-8")}')


def connect_to_network(ssid, password, path_to_netplan_yaml):
    update_netplan_settings(ssid, password, path_to_netplan_yaml)
    generate_and_apply_netplan_changes()
