#!/usr/bin/env python3
"""Helper functions to assist with Netbox data ingestion.
"""

from nornir.core.inventory import ConnectionOptions
from netbox import NetBox

def is_interface_present(nb_interfaces:list, device_name:str, interface_name:str) -> bool:
    """Helper function to figure out if the interface in question already exists in Netbox

    Args:
        nb_interfaces (list): List of Netbox interfaces returned fromt he Netbox API
        device_name (str): Device name that we are working with
        interface_name (str): Interface name in question

    Returns:
        bool: True if the interface is present, False otherwise.
    """
    for i in nb_interfaces:
        if i["name"] == interface_name and i["device"]["display_name"] == device_name:
            return True
    return False

def get_device_id(device_name:str, netbox:NetBox) -> int:
    """Helper function to lookup the Netbox device id from the Netbox API

    Args:
        device_name (str): Device name we are looking for.
        netbox (Netbox): Netbox instance

    Returns:
        [int]: Device id
    """

    device_id:int = netbox.dcim.get_devices(name=device_name)[0]["id"]
    return device_id

def create_connection_options(username:str, password:str, secret:str) -> dict:
    """Helper function to create or connection options.

    Args:
        username (str): Username to use to connect to device.
        password (str): Password to use to connect to device.
        secret (str): Secret or enable password to use to elevate perissions on the device.

    Returns:
        dict: Nornir ConnectionOptions object
    """
    napalm_options = ConnectionOptions(
        username=username,
        password=password,
        extras={
            "optional_args": {
                "conn_timeout": 500,
                "secret": secret
            }
        }
    )

    connection_options = {
        "napalm": napalm_options
    }

    return connection_options
