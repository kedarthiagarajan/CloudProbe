variable "aws_region" {
  description = "The AWS region to deploy in."
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "The EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Name of the SSH key pair."
  type        = string
}

variable "public_key_path" {
  description = "Path to the SSH public key."
  type        = string
}
