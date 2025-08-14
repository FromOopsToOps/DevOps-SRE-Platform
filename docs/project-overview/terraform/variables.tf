variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_name" {
  description = "Name of the Lightsail instance"
  type        = string
  default     = "wordpress-server"
}

variable "instance_size" {
  description = "Lightsail bundle size (e.g., micro_2_0, small_2_0, medium_2_0)"
  type        = string
  default     = "medium_2_0"
}

variable "key_pair_name" {
  description = "Name of the Lightsail SSH key pair"
  type        = string
}

