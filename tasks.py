import os
from invoke import task
from dotenv import load_dotenv


def is_in_container() -> bool:
    try:
        with open('/run/systemd/container', 'r') as f:
            print('[!] Вызов из Incus-контейнера, выполняю команду...')
            return f.read().strip() in ['lxc', 'incus']
    except Exception:
        print('[!] Вызов с хоста, выполняю команду в Incus-контейнере...')
        return False


def run_cmd(c, container, cmd, use_compose=True):
    full_cmd = f'docker compose {cmd}' if use_compose else cmd
    
    if not is_in_container():
        wrap = f'incus exec {container} -- sh -c \'cd /root/pawshost && {full_cmd}\''
        c.run(wrap, pty=True)
    else:
        c.run(full_cmd, pty=True)


@task
def up(c, container='pawshost'):
    run_cmd(c, container, 'up -d')

@task
def build(c, container='pawshost'):
    run_cmd(c, container, 'up -d --build')

@task
def down(c, container='pawshost'):
    run_cmd(c, container, 'down')

@task
def restart(c, container='pawshost'):
    run_cmd(c, container, 'restart bot api')

@task
def restart_all(c, container='pawshost'):
    run_cmd(c, container, 'restart')

@task
def logs(c, container='pawshost', s=''):
    run_cmd(c, container, f'logs -f {s}')

@task
def shell(c, container='pawshost', s=''):
    run_cmd(c, container, f'exec -it {s} bash')

@task
def db_shell(c, container='pawshost', db='pawshost'):
    run_cmd(c, container, f'exec -it db psql -U postgres -d {db}')

@task
def alembic_upgrade(c, container='pawshost'):
    run_cmd(c, container, 'exec internal-api alembic upgrade head')

@task
def alembic_revision(c, container='pawshost', m=''):
    run_cmd(c, container, f'exec internal-api alembic revision --autogenerate -m="{m}"')
                             