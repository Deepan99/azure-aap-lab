# Security Policy

## Supported Versions

Currently supported versions of this deployment:
- Ansible Automation Platform 2.4.x
- RHEL 9.x
- Terraform 1.5.x
- Ansible 2.15.x

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it responsibly.

### How to Report

**Do not open a public issue** for security vulnerabilities.

Instead, please send an email to: **security@example.com** (replace with actual contact)

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if known)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Investigation**: Within 1 week
- **Resolution**: Based on severity and complexity

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate the report and determine severity
3. **Coordination**: We will work with you to understand and fix the issue
4. **Disclosure**: We will coordinate public disclosure timing

## Security Best Practices

### For Users

1. **Never commit sensitive data**:
   - Use Ansible Vault for credentials
   - Never commit vault.yml files
   - Use environment variables for secrets

2. **Restrict SSH access**:
   - Always set `allowed_ssh_source_ip` in terraform.tfvars
   - Use Azure Bastion for production access
   - Regularly rotate SSH keys

3. **Keep dependencies updated**:
   - Regularly update Terraform providers
   - Keep Ansible collections current
   - Monitor security advisories

4. **Enable monitoring**:
   - Set up monitoring and logging
   - Review logs regularly
   - Set up security alerts

### For Contributors

1. **Code Review**:
   - All changes require review
   - Security-sensitive changes need additional review
   - Never bypass security checks

2. **Testing**:
   - Test security changes in non-production
   - Validate that security controls still work
   - Document security implications

3. **Dependencies**:
   - Review new dependencies for security issues
   - Keep dependencies updated
   - Report vulnerable dependencies

## Security Features

### Implemented Security Measures

- **Credential Management**: Ansible Vault for secrets
- **Network Security**: IP-restricted SSH access
- **Input Validation**: Terraform variable validation
- **Security Scanning**: CI/CD pipeline with Trivy and tfsec
- **Secret Detection**: Automated scanning for hardcoded secrets
- **Access Control**: Environment-based deployment controls

### CI/CD Security

- **Automated Security Scanning**: Every commit is scanned
- **Branch Protection**: Main branch requires approval
- **Required Status Checks**: Security checks must pass
- **Environment Protection**: Production deployment requires approval
- **Secret Management**: GitHub Secrets for sensitive data

## Known Security Considerations

### Current Limitations

1. **Single Node Deployment**: No high-availability by default
2. **Self-Signed Certificates**: Default AAP installation uses self-signed SSL
3. **Database**: Local PostgreSQL without replication
4. **Logging**: Local logs without centralized log management

### Mitigations

1. **Regular Backups**: Automated backup procedures
2. **Monitoring**: Health checks and alerting
3. **Updates**: Regular security updates
4. **Documentation**: Security best practices documented

## Dependency Security

### Terraform Providers

- **hashicorp/azurerm**: Updated regularly for security patches
- **Source**: Official HashiCorp repository

### Ansible Collections

- **azure.azcollection**: From official Red Hat repositories
- **community.general**: From Ansible Galaxy

### Python Dependencies

- **Ansible**: Official Red Hat packages
- **Security Updates**: Monitored via Red Hat Security Advisories

## Security Updates

### Update Process

1. **Monitor**: Regular monitoring of security advisories
2. **Test**: Test updates in development environment
3. **Deploy**: Deploy to production after validation
4. **Document**: Document security updates

### Update Frequency

- **Terraform Providers**: Monthly review
- **Ansible Collections**: Monthly review
- **System Packages**: As needed per Red Hat advisories
- **Security Patches**: Immediate for critical issues

## Compliance

### Security Standards

This deployment follows industry best practices for:
- **Credential Management**: Secure storage and rotation
- **Network Security**: Access control and encryption
- **Logging and Monitoring**: Comprehensive audit trail
- **Patch Management**: Regular security updates
- **Access Control**: Role-based access control

### Recommendations

For production deployments, consider:
- **Azure Security Center**: Enhanced security monitoring
- **Azure Policy**: Compliance enforcement
- **Azure Defender**: Advanced threat protection
- **Compliance Standards**: HIPAA, PCI DSS, etc. as needed

## Contact

### Security Team

- **Email**: security@example.com (replace with actual contact)
- **PGP Key**: [Add PGP key fingerprint if available]
- **Response Time**: Within 48 hours

### Repository Maintainers

- **Primary Maintainer**: https://github.com/Deepan99
- **Security Issues**: Use the security reporting process above

## Resources

- [Red Hat Security Advisories](https://access.redhat.com/security/)
- [Terraform Security](https://www.terraform.io/docs/cloud/security/index.html)
- [Ansible Security](https://docs.ansible.com/ansible/latest/security/)
- [Azure Security](https://docs.microsoft.com/azure/security/)
- [GitHub Security](https://docs.github.com/en/security)

## License

This security policy is part of the azure-aap-lab repository and follows the same license terms.

---

**Last Updated**: 2026-08-14  
**Version**: 1.0  
**Repository**: https://github.com/Deepan99/azure-aap-lab