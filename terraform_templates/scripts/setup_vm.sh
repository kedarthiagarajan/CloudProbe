 #!/bin/bash
adduser --disabled-password --gecos "" experiment
echo 'experiment ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Create .ssh directory for experiment user
mkdir -p /home/experiment/.ssh
chmod 700 /home/experiment/.ssh

# Add the public key to authorized_keys
echo "${file(var.public_key_path)}" > /home/experiment/.ssh/authorized_keys
chmod 600 /home/experiment/.ssh/authorized_keys
chown -R experiment:experiment /home/experiment/.ssh
# Update and install scamper
apt-get update
apt-get install -y scamper

# Enable SSH for experiment user
mkdir /home/experiment/.ssh
chmod 700 /home/experiment/.ssh
touch /home/experiment/.ssh/authorized_keys
chmod 600 /home/experiment/.ssh/authorized_keys
chown -R experiment:experiment /home/experiment/.ssh
