import os
import shutil
from cloudprobe.src.utils import TERRAFORM_TEMPLATE_DIR

TERRAFORM_TEMPLATE_DIR_AWS = os.path.join(TERRAFORM_TEMPLATE_DIR, 'aws_vm')
TERRAFORM_WORKSPACE_DIR = './terraform_workspaces/'
SCRIPT_DIR = os.path.join(TERRAFORM_TEMPLATE_DIR, "scripts")
def create_vm_name_from_config(vm_config):
    return f"vm_{vm_config.get('region')}"

def write_aws_terraform_vars(vm_config, ssh_key_path, vm_name):
    # Create a new directory for this specific VM deployment
    new_vm_dir = os.path.join(TERRAFORM_WORKSPACE_DIR, vm_name)
    if not os.path.exists(new_vm_dir):
        os.makedirs(new_vm_dir)

    # Copy the base Terraform files (main.tf, outputs.tf, variables.tf, etc.)
    for file_name in os.listdir(TERRAFORM_TEMPLATE_DIR_AWS):
        full_file_name = os.path.join(TERRAFORM_TEMPLATE_DIR_AWS, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, new_vm_dir)
    shutil.copy(os.path.join(SCRIPT_DIR, 'setup_vm.sh'), new_vm_dir)

    # Write the terraform.tfvars file in the new VM directory
    vars_content = f"""
    aws_region = "{vm_config['region']}"
    instance_type = "{vm_config['instance_type']}"
    key_name = "experiment-key"
    public_key_path = "{ssh_key_path}"
    """
    with open(os.path.join(new_vm_dir, 'terraform.tfvars'), 'w') as f:
        f.write(vars_content)

    return new_vm_dir

def setup_aws_credentials(credentials):
    os.environ["AWS_ACCESS_KEY_ID"] = credentials['access_key']
    os.environ["AWS_SECRET_ACCESS_KEY"] = credentials['secret_key']

