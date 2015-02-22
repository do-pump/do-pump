This utility allows you to manage sets of VMs in Digital Ocean

# Examples

`dop droplet create -c 5` - will create 5 VMs with default settings: 2gb Ubuntu 14.04 machines in Amsterdam-3 zone with names node01..node05

`dop droplet destroy -p node` - will destroy all droplets with names starting with "node"

`dop list droplets` - to list all droplets

`dop list droplets -a name,ip,private_ip,size` - to specify droplet attributes should be shown in output

`dop list droplets -s -a ip` - list IPs of all droplets in one line separated by space