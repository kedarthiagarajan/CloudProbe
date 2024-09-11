import paramiko
import time

class SSHMeasurementRunner:
    def __init__(self, ssh_host, ssh_user, ssh_key_path):
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_key_path = ssh_key_path

    def run_ssh_command(self, command):
        """
        Establish an SSH connection, run the command, and return the output.
        """
        try:
            # Set up the SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ssh_host, username=self.ssh_user, key_filename=self.ssh_key_path)

            # Run the command
            stdin, stdout, stderr = ssh.exec_command(command)
            print(stdout)
            
            # Wait for the command to finish and retrieve the output
            stdout.channel.recv_exit_status()  # Wait for the command to finish
            output = stdout.read().decode('utf-8')

            # Close the SSH connection
            ssh.close()

            return output
        except Exception as e:
            raise Exception(f"SSH command failed: {str(e)}")

    def run_measurement(self, measurement_type, params) -> str:
        """
        Run the TRACEROUTE measurement over SSH and return the result.
        """
        if measurement_type == "traceroute":
            # Construct the traceroute command with the parameters
            cmd = "scamper -c \"trace -w {0} -P {1} -f {2} -m {3}\" -i {4}".format(
                int(params.get("response_timeout", 10000)) // 1000,  # Convert ms to seconds
                params["protocol"],
                params["first_hop"],
                params["max_hops"],
                params["target"], af=params["af"])
        
        else:
            raise Exception(f"Unsupported measurement type: {measurement_type}")

        # Run the command on the remote host via SSH and return the result
        return self.run_ssh_command(cmd)

if __name__ == "__main__":
    ssh_host = "34.224.90.228"  # Replace with the public IP
    ssh_user = "experiment"      # Replace with the SSH user
    ssh_key_path = "/path/to/id_rsa"  # Replace with the path to your private SSH key

    params = {
        "target": "example.com",
        "af": 4,  # IPv4
        "protocol": "ICMP",
        "response_timeout": 5000,  # 5 seconds
        "first_hop": 1,
        "max_hops": 30
    }

    runner = SSHMeasurementRunner(ssh_host, ssh_user, ssh_key_path)
    output = runner.run_measurement(params)

    print("Measurement output:", output)