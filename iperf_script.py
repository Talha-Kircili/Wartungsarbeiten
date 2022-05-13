from multiprocessing import Process
from utils import *


''' settings '''
csv_file = "iperf.csv"   # output file
table_head = ['PC', 'Bandwidth', 'Retransmits'] # column names
defekt_pcs = [(3,2)] # defekte rechner in diese liste als tuple angeben. bsp.: reihe3-pc2 => (3,2)


def main():
    for x in range(1,5):
        for y in range(1,7):
            host = f"reihe{x}-pc{y}"

            if (x,y) in defekt_pcs:
                write(csv_file, [host,'ignored','ignored'], 'a')
                continue

            client = connect(host, 'root', f'{expanduser('~')}/.ssh/netzlabor-root.key')
            if client == -1:
                write(csv_file, [host,'Exception','Exception'], 'a')
                continue

            out = loads(command(client, host, "iperf3 -c 192.168.1.8 -p 2222 -J"))
            client.close()

            retransmits = out["end"]["sum_sent"]["retransmits"]
            bandwith = out["end"]["sum_sent"]["bits_per_second"]//1000000

            print("Bandwith:", bandwith, "Mbit/s")
            print("Retransmits:", retransmits, "\n")
            write(csv_file, [host, bandwith, retransmits], 'a')


if __name__ == "__main__":
    freeze_support()
    write(csv_file, table_head, 'w')
    server = connect('support.netzlabor', 'root', f'{expanduser('~')}/.ssh/id_rsa')
    if server == -1:
        exit()
    p = Process(target=command, args=(server, 'support.netzlabor', "iperf3 -s -p 2222", True))
    p.start()
    main()
    p.terminate()
    p.join()
    server.close()
