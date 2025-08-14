terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_lightsail_instance" "wordpress" {
  name              = var.instance_name
  availability_zone = "${var.aws_region}a"
  blueprint_id      = "wordpress"
  bundle_id         = var.instance_size
  key_pair_name     = var.key_pair_name
}

resource "aws_lightsail_static_ip" "wp_ip" {
  name = "${var.instance_name}-static-ip"
}

resource "aws_lightsail_static_ip_attachment" "wp_ip_attachment" {
  static_ip_name = aws_lightsail_static_ip.wp_ip.name
  instance_name  = aws_lightsail_instance.wordpress.name
}

