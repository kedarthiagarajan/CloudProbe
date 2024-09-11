import subprocess
import json
import os
from cloudprobe.src.SSHMeasurementRunner import SSHMeasurementRunner

TERRAFORM_TEMPLATE_DIR = "./terraform_templates"
def get_public_ip(terraform_dir):
    try:
        # Run terraform output command and parse JSON output
        output = subprocess.check_output(['terraform', 'output', '-json'], cwd=terraform_dir)
        terraform_outputs = json.loads(output)
        
        # Extract and return public IP
        return terraform_outputs['instance_public_ip']['value']
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving Terraform outputs: {e}")
        return None
    except KeyError:
        print("Public IP not found in Terraform outputs.")
        return None
    
def deploy_vm(terraform_dir):
    # Ensure the provided directory exists
    if not os.path.exists(terraform_dir):
        os.makedirs(terraform_dir)

    # Copy or prepare necessary Terraform files in the temp folder (if needed)
    subprocess.run(["terraform", "init"], cwd=terraform_dir)
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=terraform_dir)

    # Get Terraform output after apply, and extract instance ID
    output = subprocess.check_output(['terraform', 'output', '-json'], cwd=terraform_dir)
    terraform_outputs = json.loads(output)

    # Assuming instance ID is part of outputs
    instance_id = terraform_outputs.get('instance_id', {}).get('value', None)
    
    return instance_id

def destroy_vm(terraform_dir):
    """
    Destroys the VM (or infrastructure) managed by Terraform in the given directory.
    
    :param terraform_dir: The directory where the Terraform configuration and state are located.
    """
    try:
        # Run `terraform destroy` in the specified directory
        subprocess.run(["terraform", "destroy", "-auto-approve"], cwd=terraform_dir, check=True)
        print(f"Successfully destroyed resources in {terraform_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error during destroy operation: {e}")

def run_measurement(public_ip, ssh_user, ssh_key_path, measurement_type, params, output_dir):
    """
    Run the specified measurement over SSH, collect the result, and save it to a file.
    
    :param public_ip: The public IP address of the remote server.
    :param ssh_user: The SSH username.
    :param ssh_key_path: Path to the private SSH key.
    :param measurement_type: Type of measurement to perform (e.g., "traceroute").
    :param params: Parameters for the measurement (e.g., traceroute settings).
    :param output_dir: Path to save the output result.
    """
    # Initialize SSH runner
    runner = SSHMeasurementRunner(public_ip, ssh_user, ssh_key_path)

    # Run the measurement command on the remote server
    print(f"Running {measurement_type} on {public_ip}...")
    result = runner.run_measurement(measurement_type, params)

    # Save the output to the specified path
    try:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{params['target']}_{measurement_type}.out")
        with open(output_path, 'w') as f:
            f.write(result)
        print(f"Measurement result saved to {output_path}")
    except IOError as e:
        print(f"Failed to save the result to {output_path}: {str(e)}")
    