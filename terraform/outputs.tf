output "resource_group_name" {
  description = "The name of the created Resource Group."
  value       = azurerm_resource_group.rg.name
}

output "public_ip_address" {
  description = "The public IP address of the AAP Controller VM."
  value       = azurerm_linux_virtual_machine.vm.public_ip_address
}

output "public_ip_dns_name" {
  description = "The FQDN of the AAP Controller VM."
  value       = azurerm_public_ip.public_ip.fqdn
}

output "ssh_command" {
  description = "The command to SSH into the AAP Controller VM."
  value       = "ssh -i ${replace(var.ssh_public_key_path, "~", "$HOME")} ${var.admin_username}@${azurerm_public_ip.public_ip.fqdn}"
}

output "aap_console_url" {
  description = "The URL to access the Ansible Automation Platform Web Console."
  value       = "https://${azurerm_public_ip.public_ip.fqdn}"
}
