# Nornir-Netbox-Sync
Example implementation of tasks that will take production data from nornir and update Netbox.

## Install Dependencies
```bash
$ pip3 -m virtualenv ./venv
$ pip3 install -r requirements.txt
```

## Configure
Update the ``.env`` file with your environment.

## Run It
```bash
python3 netbox_interface_sync.py
```