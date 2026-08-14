# Sample Terraform variables file
# Copy this to terraform.tfvars and modify as needed

resource_group_name = "rg-ansible-automation-platform"
location            = "eastus"
vm_size             = "Standard_D4s_v5"
admin_username      = "azureuser"

# Path to the SSH public key you want to use for the VM
ssh_public_key_path = "~/.ssh/id_rsa.pub"

# Choose a unique DNS label to access the AAP console
# This will form the URL: https://<dns_label>.<location>.cloudapp.azure.com
public_ip_dns_label = "aap-controller-lab-unique"

# SECURITY: Restrict SSH access to your public IP for better security
# Find your public IP at: https://whatismyipaddress.com/
# Format: "YOUR_PUBLIC_IP/32" (e.g., "203.0.113.1/32")
# Use "*" only for testing (not recommended for production)
allowed_ssh_source_ip = "*"
