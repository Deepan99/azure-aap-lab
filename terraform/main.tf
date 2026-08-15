terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Use existing Resource Group
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# Use existing Virtual Network
data "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  resource_group_name = var.resource_group_name
}

# Use existing Subnet
data "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = var.vnet_name
}

# Use existing Public IP
data "azurerm_public_ip" "public_ip" {
  name                = var.public_ip_name
  resource_group_name = var.resource_group_name
}

# Use existing Network Security Group
data "azurerm_network_security_group" "nsg" {
  name                = var.nsg_name
  resource_group_name = var.resource_group_name
}

# Use existing Network Interface
data "azurerm_network_interface" "nic" {
  name                = var.nic_name
  resource_group_name = var.resource_group_name
}

# Virtual Machine - Red Hat Enterprise Linux 9
resource "azurerm_linux_virtual_machine" "vm" {
  name                = "vm-aap-controller"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    data.azurerm_network_interface.nic.id,
  ]

  # Use SSH key authentication for security (required by Trivy)
  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  # Enable managed identity for Azure AD SSH authentication
  identity {
    type = "SystemAssigned"
  }

  os_disk {
    caching                   = "ReadWrite"
    disk_size_gb              = 64
    storage_account_type      = "Premium_LRS"
    write_accelerator_enabled = false
  }

  source_image_reference {
    offer     = "RHEL"
    publisher = "RedHat"
    sku       = "9-lvm-gen2"
    version   = "latest"
  }

  tags = {
    Environment = "Lab"
    Project     = "Ansible Automation Platform"
  }
}

# Azure AD Login Extension for SSH
resource "azurerm_virtual_machine_extension" "aad_ssh_login" {
  name                       = "AADSSHLoginForLinux"
  virtual_machine_id         = azurerm_linux_virtual_machine.vm.id
  publisher                  = "Microsoft.Azure.ActiveDirectory"
  type                       = "AADSSHLoginForLinux"
  type_handler_version       = "1.0"
  auto_upgrade_minor_version = true

  settings = jsonencode({
    "AADConfig" = {
      "TenantId" = var.tenant_id
    }
  })
}
