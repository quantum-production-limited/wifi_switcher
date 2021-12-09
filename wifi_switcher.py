import nmcli
import logging

logger = logging.getLogger()


class NetworkConnector:
    def __init__(self):
        self.successful = None
        self.message = None

    def _connection_attempt(self, ssid, password):
        """Connect to a WiFi network with the provided SSID and Password.

        Attempts to connect to a WiFi network using NMCLI. If the network is not found, a scan will be performed to try to
        find it and then attempt to connect again.
        """
        nmcli.disable_use_sudo()

        logger.info(f'Attempting to connect to network with SSID {ssid}')
        try:
            nmcli.device.wifi_connect(ssid, password)
        except nmcli._exception.NotExistException:
            logger.info(f'Connection not found, rescanning to see if it can be found:')
            try:
                nmcli.device.wifi_rescan(ssid='Wf_htc')
            except nmcli._exception.ScanningNotAllowedException:
                logger.warning(f'Not allowed to scan immediately after another scan, please try again in 30 seconds.')
                self.successful = False
                self.message = f'Failed to scan for network with SSID: {ssid}. You are not allowed to scan' \
                               f' immediately after a previous scan, please wait 30 seconds and try again.'
                return

            logger.info(f'Scan complete, attempting to connect again...')
            try:
                nmcli.device.wifi_connect(ssid, password)
            except nmcli._exception.NotExistException:
                logger.warning(f'Connection still not found after rescanning, check the SSID is correct')
                self.successful = False
                self.message = f'Unable to find a connection with SSID: {ssid}'
                return

        # Sometimes nmcli doesn't report an error, but the network connection failed (e.g. if it times out). We can
        # check this by looking at the connection details of the requested connection...
        try:
            # Try grabbing details with just the provided SSID
            all_connection_details = nmcli.connection.show(ssid)
        except nmcli._exception.NotExistException:
            try:
                # If it's not found, try prefixing with "Auto " - some Linux distros add this to the SSID when saving.
                all_connection_details = nmcli.connection.show(f'Auto {ssid}')
            except nmcli._exception.NotExistException:
                logger.warning(f'SSID {ssid} does not seem to be associated with a connection, so cannot confirm the'
                               f' connection status')
                self.successful = False
                self.message = f'Attempted to connect to SSID: {ssid}. Unable to confirm whether the connection ' \
                               f'attempt succeeded as there is no saved connection for that SSID.'
                return

        # Once we've found the connection details, we get a Dict with a lot of information. If the connection is
        # currently connected, it will have the key 'GENERAL.STATE' and value 'activated'..
        if all_connection_details.get('GENERAL.STATE') == 'activated':
            logger.info(f'Connected successfully to network with SSID {ssid}')
            self.successful = True
            self.message = f'Connected successfully to network with SSID {ssid}'
            return
        else:
            logger.warning(
                f'Some unknown connection error while connecting to SSID {ssid}. This can happen if the network was'
                f' cached from a previous scan or connection attempt. Wait 30 seconds and try again.')
            self.successful = False
            self.message = f'Unknown connection error while connecting to SSID {ssid}. Normally this means the ' \
                           f'connection attempt timed out, try again in 30 seconds.'
            return

    def connect_to_network(self, ssid, password):
        self._connection_attempt(ssid, password)
        return self.successful, self.message


def connect_to_network(ssid: str, password: str) -> tuple:
    """Connect to a WiFi network with the provided SSID and Password
    
    Creates a NetworkConnector and attempts to connect using the provided details. If the network isn't found, it will
    be scanned for and then another connection attempt is made.

    :param ssid: The SSID of the WiFi network you want to scan for and connect to.
    :param password: The password for the WiFi network
    :return: A 2-tuple. The first element is a Boolean showing whether the connection attempt succeeded, and the second
        element is a success/error message that can be displayed to the user.
    :rtype: tuple
    """
    connector = NetworkConnector()
    return connector.connect_to_network(ssid, password)
