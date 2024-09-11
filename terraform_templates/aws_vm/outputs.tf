output "instance_public_ip" {
  description = "The public IP address of the Debian VM"
  value       = aws_instance.debian_vm.public_ip
}

output "instance_id" {
  description = "The ID of the deployed AWS instance"
  value       = aws_instance.debian_vm.id
}
