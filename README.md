# Cloud Probe

The **Cloud Probe** is designed to run internet measurements such as traceroute on cloud-hosted virtual machines (VMs) using the `scamper` tool. It currently supports running VMs on AWS, with plans to extend to other cloud providers. The tool allows you to configure and run multiple sets of measurements via SSH and collect the results.

## Features

- **Automated Cloud Deployment**: Launch and configure cloud-hosted VMs.
- **Traceroute Measurements**: Run flexible, parameterized traceroute measurements using `scamper`.
- **Scalable**: Easily configure and run measurements across multiple cloud providers.
- **SSH Execution**: Remotely execute commands on the VM via SSH.

## Requirements

- Python 3.x
- `paramiko` for SSH connections (Install via `pip install paramiko`)
- AWS CLI installed 

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-repo/cloud-measurement-tool.git
cd cloud-measurement-tool
pip install -r requirements.txt
Configuration
```

The tool uses a YAML configuration file to specify cloud provider credentials, VM configurations, and measurement parameters. You can specify multiple sets of measurements.

Example Configuration
```yaml
cloud_providers:
  - name: AWS
    credentials:
      access_key: your-key
      secret_key: your-key
    vm_configs:
      - region: us-east-1
        instance_type: t2.micro
        traceroute_params:
          - target: 8.8.8.8
            af: 4
            protocol: UDP
            resolve_on_probe: false
            packets: 3
            size: 48
            first_hop: 1
            max_hops: 32
            paris: 16
            dont_fragment: true
          - target: 1.1.1.1
            af: 4
            protocol: ICMP
            resolve_on_probe: false
            packets: 3
            size: 64
            first_hop: 1
            max_hops: 30
            paris: 8
            dont_fragment: false
```

## AWS Config
name: The cloud provider's name (currently supports AWS).
credentials: AWS credentials to access and manage VMs.
access_key: Your AWS access key.
secret_key: Your AWS secret key.
vm_configs: A list of VM configurations for measurements.
region: The AWS region to deploy the VM.
instance_type: The type of instance (e.g., t2.micro).
traceroute_params: A list of traceroute parameters (see below).
Traceroute Params Format
Each traceroute_params entry is a tuple with the following fields:

target: The IP or hostname to trace.
af: Address family (IPv4 = 4, IPv6 = 6).
protocol: Protocol to use for traceroute (e.g., UDP, ICMP).
resolve_on_probe: Whether to resolve hostnames during the probe (true or false).
packets: Number of packets to send for each probe.
size: Size of the packet in bytes.
first_hop: First hop to start the traceroute from.
max_hops: Maximum number of hops to trace.
paris: The number of flow IDs for Paris-traceroute.
dont_fragment: Whether to set the "Don't Fragment" flag (true or false).


Example of Traceroute Parameters

```
traceroute_params:
  - [8.8.8.8, 4, UDP, false, 3, 48, 1, 32, 16, true]
  - [1.1.1.1, 4, ICMP, false, 3, 64, 1, 30, 8, false]
```
How to Run

Prepare the Configuration: Create a YAML configuration file with your cloud provider credentials, VM details, and traceroute parameters.
Run the Python Script: Execute the Python script with the configuration file and your SSH public key.
```bash
python deploy.py cloud_config.yaml /path/to/your/ssh_key.pub
Parameters:
cloud_config.yaml: Path to the YAML configuration file that contains cloud provider credentials and traceroute parameters.
/path/to/your/ssh_key.pub: Path to your public SSH key used to access the cloud VMs.
```

The script will:

Deploy VMs on the specified cloud provider (AWS).
SSH into the VMs to run traceroute measurements using scamper.
Collect and save the measurement results.

```bash

python deploy.py aws_experiment.yaml /home/user/.ssh/id_rsa.pub
This command runs the traceroute measurements defined in the aws_experiment.yaml configuration file, using the specified SSH key to access the AWS instance.
```

Output

The tool prints the result of each measurement to the console and saves the output to a file specified in the script. Results can include the hop-by-hop route to the target IP or hostname.
