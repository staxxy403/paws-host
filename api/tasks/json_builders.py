import os

from database.core import VPS

INCUS_INSTANCE_TYPE = os.getenv('INCUS_INSTANCE_TYPE', 'virtual-machine')


def vm_create_payload(vps: VPS, user_data_yaml: str, network_data_yaml: str) -> dict[str,str]:
    json = {
      'name': vps.incus_name,
      'type': INCUS_INSTANCE_TYPE,
      'start': True,
      'profiles': [],
      'source': {
        'type': 'image',
        'mode': 'pull',
        'server': 'https://images.linuxcontainers.org',
        'protocol': 'simplestreams',
        'alias': vps.os.incus_name
      },
      'config': {
        'limits.cpu': vps.tariff.cpu_cores,
        'limits.memory': f'{vps.tariff.ram_gb}GiB',
        'cloud-init.user-data': user_data_yaml,
        'cloud-init.network-config': network_data_yaml
      },
      'devices': {
        'root': {
          'type': 'disk',
          'pool': 'default',
          'path': '/',
          'size': f'{vps.tariff.disk_gb}GiB'
        },
        'eth0': {
          'type': 'nic',
          'nictype': 'routed',
          'parent': vps.node.parent_interface,
          'ipv4.address': vps.ip_address.ip
        }
      }
    }
    return json
