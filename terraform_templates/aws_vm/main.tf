data "aws_availability_zones" "available" {
  state = "available"
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "debian_vm" {
  ami           = data.aws_ami.debian.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.vm_key.key_name

 user_data = <<-EOF
  #!/bin/bash
  adduser --disabled-password --gecos "" experiment
  echo 'experiment ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

  # Create the .ssh directory for the experiment user
  mkdir -p /home/experiment/.ssh
  chmod 700 /home/experiment/.ssh

  # Add the public key to authorized_keys
  echo "${file(var.public_key_path)}" > /home/experiment/.ssh/authorized_keys
  chmod 600 /home/experiment/.ssh/authorized_keys
  chown -R experiment:experiment /home/experiment/.ssh

  # Update and install scamper
  apt-get update
  apt-get install -y scamper
EOF

  tags = {
    Name = "Debian-Scamper-VM"
  }

  # Security Group for SSH Access
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  # Specify the subnet where the instance should be launched
  subnet_id = aws_subnet.custom_subnet.id
  associate_public_ip_address = true

}



# Fetch the latest Debian AMI
data "aws_ami" "debian" {
  most_recent = true
  filter {
    name   = "name"
    values = ["debian-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"  # Filter by x86_64 architecture
    values = ["x86_64"]
  }

  owners = ["136693071363"] # Debian images owner ID
}

# Data source to check instance status
data "aws_instance" "debian_vm" {
  instance_id = aws_instance.debian_vm.id
  depends_on  = [aws_instance.debian_vm]
}

# Null resource to wait for instance to be in 'running' state
resource "null_resource" "wait_for_instance" {
  depends_on = [aws_instance.debian_vm]

  provisioner "local-exec" {
    command = <<EOT
      while [ "$(aws ec2 describe-instance-status --instance-id ${aws_instance.debian_vm.id} --query "InstanceStatuses[0].SystemStatus.Status" --region ${var.aws_region} --output text)" != "ok" ] || \
             [ "$(aws ec2 describe-instance-status --instance-id ${aws_instance.debian_vm.id} --query "InstanceStatuses[0].InstanceStatus.Status" --region ${var.aws_region} --output text)" != "ok" ]; do
        echo "Waiting for instance ${aws_instance.debian_vm.id} status checks to pass..."
        sleep 10
      done
      echo "Instance ${aws_instance.debian_vm.id} status checks have passed!"
    EOT
  }
}



resource "aws_security_group" "allow_ssh" {
  vpc_id      = aws_vpc.custom_vpc.id  # Associate with the custom VPC
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
    prevent_destroy = true
  }
}



resource "aws_key_pair" "vm_key" {
  key_name   = var.key_name
  public_key = file(var.public_key_path)

  lifecycle {
    create_before_destroy = true
    prevent_destroy = true
  }
}


# Create a custom VPC
resource "aws_vpc" "custom_vpc" {
  cidr_block = "10.0.0.0/16"
}

# Create a subnet within the custom VPC
resource "aws_subnet" "custom_subnet" {
  vpc_id            = aws_vpc.custom_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0] # Adjust based on your region
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.custom_vpc.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.custom_vpc.id
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_association" {
  subnet_id      = aws_subnet.custom_subnet.id
  route_table_id = aws_route_table.public_rt.id
}