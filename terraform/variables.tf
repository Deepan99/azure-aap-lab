variable "resource_group_name" {
  type        = string
  description = "The name of the resource group in which to create the resources."
  default     = "rg-ansible-automation-platform"
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
}

variable "allowed_ssh_source_ip" {
  type        = string
  description = "CIDR block allowed to reach SSH (e.g., 'YOUR_PUBLIC_IP/32'). Must be an explicit CIDR; wildcards are rejected."

  validation {
    condition     = can(cidrhost(var.allowed_ssh_source_ip, 0)) && var.allowed_ssh_source_ip != "0.0.0.0/0"
    error_message = "allowed_ssh_source_ip must be a specific CIDR block such as '203.0.113.1/32'. Exposing SSH to '*' or '0.0.0.0/0' is not permitted."
  }
}

variable "allowed_web_source_ip" {
  type        = string
  description = "CIDR block allowed to reach the AAP web console (443/8443). Must be an explicit CIDR; wildcards are rejected."

  validation {
    condition     = can(cidrhost(var.allowed_web_source_ip, 0)) && var.allowed_web_source_ip != "0.0.0.0/0"
    error_message = "allowed_web_source_ip must be a specific CIDR block such as '203.0.113.1/32'. Exposing the console to '*' or '0.0.0.0/0' is not permitted."
  }
}
