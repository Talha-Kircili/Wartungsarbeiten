from utils import *


''' settings '''
csv_file = "iperf.csv"      # output file
table_head = ['PC', 'Bandwidth', 'Retransmits'] # column names
defekt_pcs = [(3,2)]        # defective machines in list in forms of tuple. f.e reihe3-pc2 => (3,2)
server_name = "support.netzlabor" # iperf3 server
server_port = "2222"          # listening port


def main():
    for x in range(1,5):
        for y in range(1,7):
            hostname = f"reihe{x}-pc{y}"
            ''' skip defective machines '''
            if (x,y) in defekt_pcs:
                write(csv_file, [hostname, 'defekt', 'defekt'], 'a')
                continue
            ''' establish ssh connection '''
            client = connect(hostname, 'root')
            if client == -1:
                write(csv_file, [hostname,'Host unreachable', 'Host unreachable'], 'a')
                continue
            ''' check/install iperf3 '''
            apt = command(client, hostname, "apt list --installed | grep iperf3")
            if 'iperf3' in apt:
                print(f"{hostname}: iperf3 is installed")
            else:
                pkg = command(client, hostname, "sudo apt install -y iperf3", timeout=10)
                if pkg == -1:
                    msg = "failed installing iperf3"
                    print(f"{hostname}: {msg}")
                    client.close()
                    write(csv_file, [hostname, msg, msg], 'a')
                    continue 
                print(f"{hostname}: iperf3 successfully installed")
            ''' json.loads error handling '''
            result = command(client, hostname, "iperf3 -c {server_name} -p {server_port} -J")
            try:
                result = loads(result)
                retransmits = result["end"]["sum_sent"]["retransmits"]
                bandwidth = int(result["end"]["sum_sent"]["bits_per_second"]/1000000)
                print(f"Bandwidth: {bandwidth} Mbit/s")
                print(f"Retransmits: {retransmits}\n")
            except Exception as e:
                bandwidth = retransmits = e
                print(f"{hostname}: {e}\nOutput: {result}\n")
            ''' close connection and document results '''
            client.close()
            write(csv_file, [hostname, bandwidth, retransmits], 'a')


if __name__ == "__main__":
    write(csv_file, table_head, 'w')
    main()
