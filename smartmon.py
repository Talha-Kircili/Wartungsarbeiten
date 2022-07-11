from multiprocessing.pool import ThreadPool
from multiprocessing import freeze_support
from utils import *


''' settings '''
csv_file = "smartmon.csv"   # output file
table_head = ['PC', 'Zustand', 'Protokoll'] # column names
defekt_pcs = [(3,2)]        # defective machines in list in forms of tuple. f.e reihe3-pc2 => (3,2)


def main(x,y):
    hostname = f"reihe{x}-pc{y}"
    ''' skip defective machines '''
    if (x,y) in defekt_pcs:
        return write(csv_file, [hostname,'defekt','defekt'], 'a')
    ''' establish ssh connection '''
    client = connect(hostname, 'root')
    if client == -1:
        return write(csv_file, [hostname, 'Host unreachable', 'Host unreachable'], 'a')
    ''' check/install smartmontools '''
    apt = command(client, hostname, "apt list --installed | grep smartmontools")
    if 'smartmontools' in apt:
        print(f"{hostname}: smartmontools is installed\n")
    else:
        pkg = command(client, hostname, "sudo apt install -y smartmontools", timeout=10)
        if pkg == -1:
            msg = "failed installing smartmontools"
            print(f"{hostname}: {msg}\n")
            client.close()
            return write(csv_file, [hostname, msg, msg], 'a')
        print(f"{hostname}: smartmontools successfully installed\n")
    ''' run smartctl short test and get the results '''
    command(client, hostname, "smartctl -t short -C /dev/sda")
    protokoll = command(client, hostname, "smartctl -a /dev/sda")
    zustand = command(client, hostname, "smartctl -a /dev/sda -j")
    ''' json.loads error handling '''
    try:
        zustand = loads(zustand)
        zustand = zustand["ata_smart_self_test_log"]["standard"]["table"][-1]["status"]["passed"]
        print(f"{hostname}: passed: {zustand}\n")
    except Exception as e:
        zustand = e
        print(f"{hostname}: {e}\nOutput: {zustand}\n")
    ''' close connection and document results '''
    client.close()
    write(csv_file, [hostname, zustand, protokoll], 'a')


if __name__ == "__main__":
    freeze_support()
    write(csv_file, table_head, 'w')
    with ThreadPool() as p:
        p.starmap(main, list((x,y) for x in range(1,5) for y in range(1,7)))
