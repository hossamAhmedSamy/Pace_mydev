import os
import subprocess

def convert_to_dicts(data):
    keys = data[0].split()
    interfaces = []
    for values in data[1:]:
        if (values.replace(" ","") != ""):
            interface = dict(zip(keys,values.split()))
            interfaces.append(interface)
    return interfaces

cmdline = ['nmcli', 'device', 'status'] 
result = subprocess.run(cmdline, stdout=subprocess.PIPE)
available_interfaces = str(result.stdout.decode()).replace('\n\n','n').split('\n')


filePath = '/etc/sysconfig/network-scripts/ifcfg-{}'
veth_index = 0
for interface in convert_to_dicts(available_interfaces):
    if (interface["TYPE"] == "ethernet"):
        oldName = interface["DEVICE"]
        newName = "veth" + str(veth_index)

        subprocess.run(["ip", "link", "set", "dev", oldName, "down"], check=True)
        subprocess.run(["ip", "link", "set", "dev", oldName, "name", newName], check=True)
        subprocess.run(["ip", "link", "set", "dev", newName, "up"], check=True)
        veth_index += 1
        if (os.path.exists(filePath.format(oldName))):
            with open(filePath.format(oldName), "r") as file:
                lines = file.readlines()
            with open(filePath.format(newName), "w") as file:
                for line in lines:
                    newLine = line.replace(oldName, newName)
                    file.write(newLine)
            
        print(interface)
