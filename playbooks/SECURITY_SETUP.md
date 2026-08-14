# Security Setup Guide

## Credential Management

This repository uses Ansible Vault to secure sensitive credentials. Follow these steps to set up encrypted credentials.

### Option 1: Using Ansible Vault (Recommended)

1. **Create vault file from example:**
   ```bash
   cd playbooks
   cp vault.yml.example vault.yml
   ```

2. **Edit vault.yml with your actual credentials:**
   ```bash
   vi vault.yml
   ```

3. **Encrypt the vault file:**
   ```bash
   ansible-vault encrypt vault.yml
   ```

4. **Run playbooks with vault:**
   ```bash
   ansible-playbook -i inventory install_aap.yml --ask-vault-pass
   ```

### Option 2: Using Environment Variables

For CI/CD or automated deployments, you can use environment variables instead of vault:

```bash
export RH_USERNAME="your_redhat_username"
export RH_PASSWORD="your_redhat_password"
export AAP_ADMIN_PASSWORD="your_admin_password"
export AAP_DB_PASSWORD="your_db_password"

ansible-playbook -i inventory install_aap.yml
```

### Security Best Practices

1. **Never commit vault.yml or actual credentials** to the repository
2. **Use strong, unique passwords** for all AAP components
3. **Rotate credentials regularly** in production environments
4. **Limit vault file access** to only necessary team members
5. **Use different credentials** for development, staging, and production
6. **Enable audit logging** in AAP to track credential usage

### Terraform Security

The Terraform configuration includes variable validation. When running Terraform:

1. **Restrict SSH access** by setting your public IP in `terraform.tfvars`:
   ```hcl
   allowed_ssh_source_ip = "YOUR_PUBLIC_IP/32"
   ```

2. **Use Azure Key Vault** for storing secrets in production (not implemented in this lab)

3. **Enable Azure security features** like Azure Security Center and Defender

### Additional Security Measures

- **Network Security Groups**: Restrict inbound traffic to only necessary ports and sources
- **Disk Encryption**: Enable Azure Disk Encryption for VM disks
- **Managed Identities**: Use Azure Managed Identities instead of service principals where possible
- **HTTPS Only**: Always use HTTPS for AAP console access
- **Regular Updates**: Keep RHEL, AAP, and Azure components updated
