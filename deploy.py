import os
import subprocess
import yaml
import sys

from src import aws
from src.utils import * 

TERRAFORM_DIR = './tmp/'
SCRIPT_DIR = './terraform_templates/scripts'
OUTPUT_DIR = './output/'

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def main(config_file, ssh_key_path):
    config = load_config(config_file)

    for provider in config['cloud_providers']:
        if provider['name'] == 'AWS':
            aws.setup_aws_credentials(provider['credentials'])

            for vm_config in provider['vm_configs']:
                vm_name = aws.create_vm_name_from_config(vm_config)
                new_vm_dir = aws.write_aws_terraform_vars(vm_config, ssh_key_path, vm_name)
                deploy_vm(new_vm_dir)
                public_ip = get_public_ip(new_vm_dir)
                vm_output_dir = os.path.join(OUTPUT_DIR, vm_name)
                for params in vm_config.get('traceroute_params'):
                    run_measurement(public_ip, "experiment", ssh_key_path, "traceroute", params, vm_output_dir)
                destroy_vm(new_vm_dir)

                

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python deploy.py <config.yaml> <path-to-ssh-key>")
        sys.exit(1)

    config_file = sys.argv[1]
    ssh_key_path = sys.argv[2]
    main(config_file, ssh_key_path)
