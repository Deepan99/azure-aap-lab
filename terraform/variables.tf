variable "resource_group_name" {
  type        = string
  description = "The name of the resource group in which to create the resources."
  default     = "rg-ansible-automation-platform"

  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]{1,90}$", var.resource_group_name))
    error_message = "Resource group name must be between 1 and 90 characters and contain only letters, numbers, underscores, or hyphens."
  }
}

variable "location" {
  type        = string
  description = "The Azure region where resources should be created."
  default     = "eastus"
}

variable "vnet_address_space" {
  type        = list(string)
  description = "The address space for the virtual network."
  default     = ["10.0.0.0/16"]
}

variable "subnet_address_prefix" {
  type        = list(string)
  description = "The subnet address prefix."
  default     = ["10.0.1.0/24"]
}

variable "vm_size" {
  type        = string
  description = "The size of the virtual machine. AAP requires a minimum of 4 vCPUs and 16 GB RAM."
  default     = "Standard_D4s_v5"
}

variable "admin_username" {
  type        = string
  description = "The administrator username for the VM."
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  type        = string
  description = "The path to the local SSH public key file to inject into the VM."
  default     = "~/.ssh/id_rsa.pub"
}

variable "public_ip_dns_label" {
  type        = string
  description = "Unique DNS label for the public IP address."
  default     = "aap-controller-lab"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,63}$", var.public_ip_dns_label))
    error_message = "DNS label must be between 3 and 63 characters, contain only lowercase letters, numbers, or hyphens, and start/end with alphanumeric characters."
  }
}

variable "allowed_ssh_source_ip" {
  type        = string
  description = "CIDR block for allowed SSH source IP (e.g., 'YOUR_PUBLIC_IP/32'). Use '*' for any IP (not recommended for production)."
  default     = "*"

  validation {
    condition     = var.allowed_ssh_source_ip == "*" || can(regex("^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}/[0-9]{1,2}$", var.allowed_ssh_source_ip))
    error_message = "SSH source IP must be a valid CIDR block (e.g., '203.0.113.1/32') or '*' for any IP."
  }
}
