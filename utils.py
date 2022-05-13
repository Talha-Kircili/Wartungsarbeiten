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

def connect(host, username, key_file):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh_client.connect(host, username=username, key_filename=key_file, timeout=5)
    except Exception as e:
        print(e)
        return -1
    return ssh_client

def command(host, hostname, cmd):
    output = ""
    print(f"{hostname}: {cmd}")
    stdin, stdout, stderr = host.exec_command(cmd)
    if stdout.channel.recv_exit_status() == 0:
        output = stdout.read().decode("utf8")
    else:
        print(f'{hostname}: STDERR: {stderr.read().decode("utf8")}')
    stdin.close()
    stdout.close()
    stderr.close()
    return output