# Security Fixes Applied

## Summary of Changes

This document outlines the security improvements made to the azure-aap-lab repository.

## ✅ Completed Fixes

### 1. Credential Management (CRITICAL)

**Issue**: Hardcoded credentials in `playbooks/install_aap.yml`

**Fix**:

- Removed hardcoded Red Hat and AAP credentials
- Added support for Ansible Vault (`vault_rh_username`, `vault_rh_password`, etc.)
- Added support for environment variables as fallback
- Created `playbooks/vault.yml.example` as template
- Created `playbooks/SECURITY_SETUP.md` with detailed setup instructions

**Files Modified**:

- `playbooks/install_aap.yml` - Replaced hardcoded credentials with vault/env variables
- `playbooks/vault.yml.example` - New file with credential template
- `playbooks/SECURITY_SETUP.md` - New comprehensive security guide

### 2. Network Security (HIGH)

**Issue**: Open SSH access allowing connections from any IP

**Fix**:

- Added `allowed_ssh_source_ip` variable to Terraform
- Updated NSG rules to use the restricted IP range
- Added validation for CIDR format
- Default set to "*" with strong recommendation to restrict

**Files Modified**:

- `terraform/variables.tf` - Added `allowed_ssh_source_ip` variable with validation
- `terraform/main.tf` - Updated NSG SSH rule to use variable
- `terraform/terraform.tfvars` - Added configuration with security comments

### 3. Input Validation (MEDIUM)

**Issue**: No validation for critical Terraform variables

**Fix**:

- Added validation for `resource_group_name` (format and length)
- Added validation for `public_ip_dns_label` (DNS naming rules)
- Added validation for `allowed_ssh_source_ip` (CIDR format)

**Files Modified**:

- `terraform/variables.tf` - Added validation blocks for all critical variables

### 4. Health Checks (MEDIUM)

**Issue**: No verification of AAP installation success

**Fix**:

- Added API endpoint health check (`/api/v2/ping/`)
- Added web interface accessibility check
- Added systemd service status checks for critical services
- Added retry logic with appropriate timeouts

**Files Modified**:

- `playbooks/install_aap.yml` - Added comprehensive health check tasks

### 5. Documentation & Git Security (MEDIUM)

**Issue**: Incomplete security documentation and vulnerable .gitignore

**Fix**:

- Updated README with security best practices section
- Added security references in quickstart and troubleshooting
- Updated .gitignore to prevent committing sensitive files
- Added comments to other playbooks about credential alternatives

**Files Modified**:

- `README.md` - Added security section and updated multiple sections
- `.gitignore` - Added vault files, state files, and OS files
- `ansible/bootstrap_rhel.yml` - Added comments about env variable alternatives
- `playbooks/azure_vm_provision.yml` - Added env variable support for SSH key path

## 📋 Security Recommendations

### Immediate Actions Required:
1. **Never commit actual credentials** - Use vault.yml.example as template only
2. **Set your public IP** in `terraform.tfvars` before deployment
3. **Encrypt vault.yml** with `ansible-vault encrypt vault.yml`
4. **Use strong passwords** when setting up credentials

### Ongoing Security Practices:
1. **Rotate credentials regularly** in production environments
2. **Monitor Azure Security Center** for recommendations
3. **Keep all components updated** (RHEL, AAP, Terraform providers)
4. **Review NSG rules** periodically and remove unnecessary access
5. **Enable Azure Disk Encryption** for production deployments

## 🔐 Before Production Use

The repository is now suitable for lab environments. For production use, consider:

1. **Azure Key Vault integration** for secret management
2. **Azure Private Endpoints** for network isolation
3. **Azure Managed Identities** instead of service principals
4. **Azure Backup** for disaster recovery
5. **Comprehensive monitoring and alerting**
6. **Multi-region deployment** for high availability

## 📝 Usage Instructions

### With Ansible Vault:
```bash
cd playbooks
cp vault.yml.example vault.yml
# Edit vault.yml with your credentials
ansible-vault encrypt vault.yml
ansible-playbook -i inventory install_aap.yml --ask-vault-pass
```

### With Environment Variables:
```bash
export RH_USERNAME="your_username"
export RH_PASSWORD="your_password"
export AAP_ADMIN_PASSWORD="your_admin_password"
export AAP_DB_PASSWORD="your_db_password"
ansible-playbook -i inventory install_aap.yml
```

### With Terraform Security:
```bash
cd terraform
# Edit terraform.tfvars and set:
# allowed_ssh_source_ip = "YOUR_PUBLIC_IP/32"
terraform init
terraform apply
```

## ✅ Verification

To verify the security fixes:
1. Check that no credentials are hardcoded in any files
2. Verify .gitignore includes vault.yml and sensitive files
3. Test Terraform with invalid CIDR to see validation in action
4. Run health checks after AAP installation to verify monitoring

---

**Date**: 2026-08-14  
**Repository**: azure-aap-lab  
**Security Level**: Improved from ⚠️ Vulnerable to ✅ Lab-Ready
