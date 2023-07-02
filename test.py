import subprocess

def convert_to_dicts(data):
    keys = data[0].split()
    interfaces = []
    #print(keys)   
    for values in data[1:]:
        if (values.replace(" ","") != ""):
            interface = dict(zip(keys,values.split()))
            interfaces.append(interface)
    return interfaces

cmdline = ['nmcli', 'device', 'status'] 
result = subprocess.run(cmdline, stdout=subprocess.PIPE)
available_interfaces = str(result.stdout.decode()).replace('\n\n','n').split('\n')

veth_index = 0
for interface in convert_to_dicts(available_interfaces):
    if (interface["TYPE"] == "ethernet"):
        new_name = "veth" + str(veth_index)
        subprocess.run(["ip", "link", "set", "dev", interface["DEVICE"], "down"], check=True)
        print('BEFORE RENAMING')        
        subprocess.run(["ip", "link", "set", "dev", interface["DEVICE"], "name", new_name], check=True)
        print('AFTER RENAMING')
        subprocess.run(["ip", "link", "set", "dev", new_name, "up"], check=True)
        print(interface["DEVICE"])

    print(interface)
