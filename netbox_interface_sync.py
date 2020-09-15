#!/usr/bin/env python3
"""Example nornir tasks to update Netbox from live device data.
"""

from os import getenv
from nornir.init_nornir import InitNornir
from nornir.core.task import Task, Result
from nornir.core.configuration import logging
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from netbox import NetBox
from dotenv import find_dotenv, load_dotenv
from helpers import get_device_id, is_interface_present, create_connection_options

def update_netbox_interfaces(task: Task, nb_interfaces: list, netbox) -> Result:
    """Nornir task to update interfaces in Netbox obtained via napalm_get from live devices.

    Args:
        task (Task): This.
        nb_interfaces (list): List of netbox interfaces.
        netbox (NetBox): Netbox instance

    Returns:
        Result: Nornir task result
    """
    task_result = task.run(task=napalm_get, getters=['interfaces'], severity_level=logging.FATAL)
    interfaces = task_result.result['interfaces']

    changed:bool = False
    changed_items:list = []

    for interface_name in interfaces.keys():
        enabled=interfaces[interface_name]['is_enabled']
        mtu=interfaces[interface_name]['mtu']
        description=interfaces[interface_name]['description']
        mac_address=interfaces[interface_name]['mac_address']

        if (is_interface_present(nb_interfaces=nb_interfaces,
                                device_name=f"{task.host}",
                                interface_name=interface_name)):
            print(
                f"* Updating Netbox Interface for device {task.host}, interface {interface_name}"
            )

            dcim_result = netbox.dcim.update_interface(
                device=f"{task.host}",
                interface=interface_name,
                description=description,
                enabled=enabled,
                mtu=mtu,
                mac_address=mac_address,
            )

            changed=True
            changed_items.append(f"{task.host} : {interface_name} Updated: {dcim_result}")

    return Result(host=task.host, result=changed_items, changed=changed)

def create_netbox_interfaces(task: Task, nb_interfaces: list, netbox: NetBox) -> Result:
    """Nornir task to create interfaces in Netbox obtained via napalm_get from live devices.

    Args:
        task (Task): This.
        nb_interfaces (list): List of netbox interfaces.
        netbox (NetBox): Netbox instance

    Returns:
        Result: Nornir task result
    """
    task_result = task.run(task=napalm_get, getters=['interfaces'], severity_level=logging.FATAL)
    interfaces = task_result.result['interfaces']

    changed:bool = False

    changed_items:list = []

    for interface_name in interfaces.keys():
        exists = is_interface_present(nb_interfaces=nb_interfaces,
                                    device_name=f"{task.host}",
                                    interface_name=interface_name)

        if not exists:
            print(
                f"* Creating Netbox Interface for device {task.host}, interface {interface_name}"
            )

            device_id = get_device_id(device_name=f"{task.host}", netbox=netbox)
            print (f"Device ID: {device_id}")

            dcim_result = netbox.dcim.create_interface(
                device_id=device_id,
                name=f"{interface_name}",
                interface_type="1000base-t",
                enabled=interfaces[interface_name]['is_enabled'],
                mtu=interfaces[interface_name]['mtu'],
                description=interfaces[interface_name]['description'],
                mac_address=interfaces[interface_name]['mac_address'],
            )

            changed_items.append(dcim_result)

            changed=True

    return Result(host=task.host,result=changed_items, changed=changed)

def main():
    """ Here's the good stuff
    """
    dotenv_file = find_dotenv()
    load_dotenv(dotenv_path=dotenv_file, verbose=True)

    ## NetBox Stuff
    nb_host=getenv('nb_host')
    nb_url=f"http://{nb_host}"
    nb_token=getenv('nb_token')

    ## Napalm Stuff
    username=getenv('username')
    password=getenv('password')
    secret=getenv('secret')

    netbox:NetBox = NetBox(host=nb_host, auth_token=nb_token,
                            ssl_verify=False, use_ssl=False,
                            port=80)

    nb_interfaces:list = netbox.dcim.get_interfaces()

    nornir_instance = InitNornir(
        inventory={
            "plugin":"NetBoxInventory2",
            "options": {
                "nb_url": nb_url,
                "nb_token": nb_token
            }
        },
        logging={
            "enabled": True,
            "level": "INFO", # DEBUG is most verbose
            "to_console": False, # True returns ALOT of stuff
        }
    )

    for host in nornir_instance.inventory.hosts.keys():
        nornir_instance.inventory.hosts[host].connection_options = create_connection_options(
                                                        username=username,
                                                        password=password,
                                                        secret=secret)

    # Create New Interfaces
    result = nornir_instance.run(task=create_netbox_interfaces,
                    nb_interfaces=nb_interfaces,
                    netbox=netbox)
    print_result(result)

    # Update Existing Interfaces
    result = nornir_instance.run(task=update_netbox_interfaces,
                    nb_interfaces=nb_interfaces,
                    netbox=netbox)
    print_result(result)

    # # Getters: https://napalm.readthedocs.io/en/latest/support/#getters-support-matrix
    # result = nornir_instance.run(task=napalm_get, getters=['vlans'])
    # print_result(result)

    # # result = nornir_instance.run(task=napalm_get, getters=['users'])
    # # print_result(result)

    # # result = nornir_instance.run(task=napalm_get, getters=['snmp_information'])
    # # print_result(result)

    # # result = nornir_instance.run(task=napalm_get, getters=['interfaces_ip'])
    # # print_result(result)

if __name__ == "__main__":
    main()
