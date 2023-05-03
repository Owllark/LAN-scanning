import os, socket, struct, re, sys, subprocess


def toInt(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def toStr(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def getValue(s):
    i = 0
    b = True
    while not '0' < s[i] < '9' or b:
        i += 1
        if s[i] == '.':
            b = False
    return s[i:len(s)]


# Checking interfaces
interface_list = list()
ipconfig_res = subprocess.Popen("ipconfig", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
lines = []
masks = []
interface = ['0'] * 3
for line in ipconfig_res.stdout.readlines():
    line = line.strip()
    if line:
        line = line.decode('cp866')
        lines.append(line)
        if 'Адаптер' in line:
            interface[0] = line
        if 'IPv4' in line:
            interface[1] = getValue(line)
        if 'Маска подсети' in line:
            interface[2] = getValue(line)
            interface_list.append(interface.copy())
ipconfig_res.terminate()

for i in range(0, len(interface_list)):
    print(i + 1, *interface_list[i])

idx = 0
print('Enter interface number:')
while not 0 < idx <= len(interface_list):
    try:
        idx = int(input())
        if not 0 < idx <= len(interface_list): 
            print('Please enter correct number:')
    except:
        print('Please enter correct number:')
# Broadcasting
interface = interface_list[idx - 1]
ip = toInt(interface[1])
mask = toInt(interface[2])

lan = ip & mask
broadcast = ip | (mask ^ 0xFFFFFFFF)

print('My IP:     ', toStr(ip))
print('Host name  ', socket.gethostname())
print('Netmask:   ', toStr(mask))
print('Network:   ', toStr(lan))

nodes = []
fromi = toStr(lan + 1).split('.')
toi = toStr(broadcast - 1).split('.')
for a in range(int(fromi[0]), int(toi[0]) + 1, 1):
    for b in range(int(fromi[1]), int(toi[1]) + 1, 1):
        for c in range(int(fromi[2]), int(toi[2]) + 1, 1):
            for d in range(int(fromi[3]), int(toi[3]) + 1, 1):
                ip_check = str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d)
                res = os.popen('ping -n 1 -w 800  ' + ip_check).read().encode('cp1251').decode('cp866')
                if 'Превышен интервал ожидания' in res:
                    pass

                else:
                    nodes.append(ip_check)

# Checkings MAC - addresses
print('       IP         |          MAC         |')
print('------------------------------------------')
arp_res = subprocess.Popen("arp -a", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
hosts = []
for line in arp_res.stdout.readlines():
        line = line.strip()
        if line:
            line = line.decode('cp866')
            hosts.append(line)
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} +$", line[0:16]):
                arp_ip = line[0:16].strip()
                if toInt(arp_ip) & mask == lan and toInt(arp_ip) != broadcast:
                    print(line[0:40])
                    is_node_found = True
                    break
arp_res.terminate()
