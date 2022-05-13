from multiprocessing import Pool
from utils import *


''' settings '''
csv_file = "smartmon.csv"   # output file
table_head = ['PC', 'Zustand', 'Protokoll'] # column names
defekt_pcs = [(3,2)] # defekte rechner in diese liste als tuple angeben. bsp.: reihe3-pc2 => (3,2)


def main(x,y):
    host = f"reihe{x}-pc{y}"

    if (x,y) in defekt_pcs:
        write(csv_file, [host,'ignored','ignored'], 'a')
        return 

    client = connect(host, 'root', f'{expanduser('~')}/.ssh/netzlabor-root.key')
    if client == -1:
        write(csv_file, [host,'Exception','Exception'], 'a')
        return

    command(client, host, "sudo apt install -y smartmontools")
    command(client, host, "smartctl -t short -C /dev/sda")
    protokoll = command(client, host, "smartctl -a /dev/sda")
    zustand = loads(command(client, host, "smartctl -a /dev/sda -j"))

    client.close()

    zustand = zustand["ata_smart_self_test_log"]["standard"]["table"][-1]["status"]["passed"]
    print(f"{host}: passed: {zustand}")
    write(csv_file, [host, zustand, protokoll], 'a')


if __name__ == "__main__":
    freeze_support()
    write(csv_file, table_head, 'w')
    with Pool() as p:   # später ändern zu Threading?
        p.starmap(main, list((x,y) for x in range(1,5) for y in range(1,7)))
