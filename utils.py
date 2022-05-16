from os.path import expanduser
from json import loads
from csv import writer

''' supress deprecated warnings '''
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from paramiko import SSHClient, AutoAddPolicy


def write(file, data, mode):
    with open(file, mode, encoding='UTF8', newline='') as f:
        file_writer = writer(f)
        file_writer.writerow(data)

def connect(hostname, username, key_filename=None, timeout=5, **kwargs):
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys(key_filename)
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh_client.connect(hostname, username=username, timeout=timeout, **kwargs)
    except Exception as e:
        print(f"{hostname}: {e}")
        return -1
    return ssh_client

def command(user, hostname, cmd, **kwargs):
    output = ""
    print(f"{hostname}: {cmd}")
    stdin, stdout, stderr = user.exec_command(cmd, **kwargs)
    if stdout.channel.recv_exit_status() == 0:
        output = stdout.read().decode('UTF8')
    else:
        print(f"{hostname}: STDERR: {stderr.read().decode('UTF8')}")
        output = -1
    stdin.close()
    stdout.close()
    stderr.close()
    return output
