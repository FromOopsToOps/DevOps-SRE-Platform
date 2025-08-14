output "wordpress_instance_name" {
  value       = aws_lightsail_instance.wordpress.name
  description = "Name of the WordPress Lightsail instance"
}

output "wordpress_public_ip" {
  value       = aws_lightsail_static_ip.wp_ip.ip_address
  description = "Static public IP of the WordPress server"
}

output "wordpress_url" {
  value       = "http://${aws_lightsail_static_ip.wp_ip.ip_address}"
  description = "URL to access the WordPress site"
}

