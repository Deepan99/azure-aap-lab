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

# Network Interface (NIC)
resource "azurerm_network_interface" "nic" {
  name                = "nic-aap-controller"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = data.azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = data.azurerm_public_ip.public_ip.id
  }
}

# Associate NSG with NIC
resource "azurerm_network_interface_security_group_association" "nic_nsg" {
  network_interface_id      = azurerm_network_interface.nic.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

# Virtual Machine - Red Hat Enterprise Linux 9
resource "azurerm_linux_virtual_machine" "vm" {
  name                = "vm-aap-controller"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  size                = var.vm_size
  admin_username      = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = file(var.ssh_public_key_path)
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
    disk_size_gb         = 64 # Recommended for AAP installation
  }

  source_image_reference {
    publisher = "RedHat"
    offer     = "RHEL"
    sku       = "9-lvm-gen2"
    version   = "latest"
  }

  tags = {
    Environment = "Lab"
    Project     = "Ansible Automation Platform"
  }
}
