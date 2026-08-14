# Comprehensive Troubleshooting Guide

## Overview

This guide provides detailed troubleshooting steps for common issues encountered when deploying, managing, and using Ansible Automation Platform (AAP) on Azure using this repository.

## Table of Contents

- [Infrastructure Issues](#infrastructure-issues)
- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Runtime Issues](#runtime-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Network Issues](#network-issues)
- [Backup/Restore Issues](#backuprestore-issues)
- [Upgrade Issues](#upgrade-issues)
- [Configuration Migration Issues](#configuration-migration-issues)

## Infrastructure Issues

### Terraform Fails to Provision Resources

**Symptoms**:
- Terraform apply fails with API errors
- Resource creation timeouts
- Permission denied errors

**Diagnosis**:
```bash
# Check Azure CLI authentication
az account show

# Check Terraform version
terraform --version

# Enable detailed logging
export TF_LOG=DEBUG
terraform apply
```

**Solutions**:
1. **Authentication Issues**:
   ```bash
   az login
   az account set --subscription <subscription-id>
   ```

2. **Quota Limitations**:
   - Check Azure quotas for your subscription
   - Request quota increases if needed
   - Try different region with available capacity

3. **Resource Naming Conflicts**:
   - Change `public_ip_dns_label` in terraform.tfvars
   - Use unique resource group names

4. **Network Issues**:
   - Check Azure regional availability
   - Verify VNet address space doesn't conflict

### VM Creation Fails

**Symptoms**:
- VM provisioning fails during creation
- SSH access not working after creation
- VM not responding to ping

**Diagnosis**:
```bash
# Check VM status in Azure Portal
az vm show --resource-group rg-ansible-automation-platform --name vm-aap-controller

# Check NSG rules
az network nsg rule list --resource-group rg-ansible-automation-platform --nsg-name nsg-aap-controller
```

**Solutions**:
1. **SSH Access Issues**:
   - Verify SSH public key path in terraform.tfvars
   - Check NSG allows port 22 from your IP
   - Verify SSH key format (RSA vs ED25519)

2. **VM Size Issues**:
   - Check if VM size is available in region
   - Try alternative VM size in terraform.tfvars
   - Verify quota for requested VM size

3. **Image Issues**:
   - Check RHEL image availability in region
   - Try different RHEL version if needed

## Installation Issues

### Red Hat Registration Fails

**Symptoms**:
- Subscription manager registration errors
- Repository enablement fails
- Credential authentication errors

**Diagnosis**:
```bash
# Check subscription status
subscription-manager status

# Test credentials manually
subscription-manager register --username <user> --password <pass> --auto-attach
```

**Solutions**:
1. **Credential Issues**:
   - Verify Red Hat developer account is active
   - Check for typos in username/password
   - Reset password if needed

2. **Subscription Issues**:
   - Verify subscription has AAP entitlements
   - Check subscription expiration date
   - Contact Red Hat support if needed

3. **Network Issues**:
   - Check connectivity to Red Hat subscription servers
   - Verify DNS resolution
   - Check firewall rules allow subscription traffic

### AAP Installer Fails

**Symptoms**:
- Installer script exits with errors
- Installation hangs indefinitely
- Service startup failures after installation

**Diagnosis**:
```bash
# Check installer logs
tail -f /tmp/ansible-local-*/setup.log

# Check system resources
free -h
df -h

# Check service status
systemctl status postgresql awx
```

**Solutions**:
1. **Resource Issues**:
   - Ensure VM meets minimum requirements (4 vCPUs, 16GB RAM)
   - Check disk space (minimum 50GB free)
   - Verify sufficient memory available

2. **Database Issues**:
   ```bash
   # Check PostgreSQL status
   systemctl status postgresql
   
   # Initialize database if needed
   postgresql-setup --initdb
   ```

3. **Repository Issues**:
   ```bash
   # Verify AAP repositories are enabled
   subscription-manager repos --list | grep ansible
   
   # Manually enable repositories
   subscription-manager repos --enable=ansible-automation-platform-2.4-for-rhel-9-x86_64-rpms
   ```

4. **Port Conflicts**:
   ```bash
   # Check if ports are in use
   netstat -tlnp | grep -E '5432|443|80'
   
   # Stop conflicting services if needed
   ```

## Configuration Issues

### Web Console Not Accessible

**Symptoms**:
- Cannot access AAP web interface
- Connection timeout errors
- SSL certificate errors

**Diagnosis**:
```bash
# Check AAP service status
systemctl status awx

# Check web server
curl -k https://localhost

# Check ports
netstat -tlnp | grep 443
```

**Solutions**:
1. **Service Issues**:
   ```bash
   # Restart AAP service
   systemctl restart awx
   
   # Check service logs
   journalctl -u awx -f
   ```

2. **SSL Certificate Issues**:
   ```bash
   # Check certificate
   openssl s_client -connect localhost:443 -showcerts
   
   # Regenerate certificate if needed
   awx-manage setup_ssl
   ```

3. **Network Issues**:
   - Verify NSG allows port 443
   - Check Azure DNS propagation
   - Try using IP address instead of DNS name

### Job Execution Failures

**Symptoms**:
- Jobs fail to start
- Jobs hang indefinitely
- Jobs fail with runtime errors

**Diagnosis**:
```bash
# Check job logs
tail -f /var/log/tower/job_output.log

# Check execution node status
awx-manage list_execution_nodes

# Check system resources
free -h
```

**Solutions**:
1. **Execution Environment Issues**:
   - Verify execution environment images are available
   - Check EE registry credentials
   - Rebuild custom execution environments

2. **Credential Issues**:
   - Verify credentials are properly configured
   - Test credential connectivity
   - Check credential permissions

3. **Resource Issues**:
   - Increase memory allocation for large jobs
   - Check disk space for job output
   - Monitor CPU usage during job execution

## Runtime Issues

### Database Connection Errors

**Symptoms**:
- AAP cannot connect to PostgreSQL
- Jobs fail with database errors
- Service startup failures

**Diagnosis**:
```bash
# Check PostgreSQL status
systemctl status postgresql

# Test database connection
psql -U awx -d awx -c "SELECT 1"

# Check database logs
tail -f /var/lib/pgsql/data/log/postgresql-*.log
```

**Solutions**:
1. **Service Issues**:
   ```bash
   # Start PostgreSQL service
   systemctl start postgresql
   
   # Enable service
   systemctl enable postgresql
   ```

2. **Connection Issues**:
   ```bash
   # Check pg_hba.conf configuration
   cat /var/lib/pgsql/data/pg_hba.conf
   
   # Restart PostgreSQL after config changes
   systemctl restart postgresql
   ```

3. **Database Corruption**:
   ```bash
   # Check database integrity
   psql -U awx -d awx -c "SELECT * FROM pg_stat_database"
   
   # Restore from backup if needed
   ansible-playbook restore_aap.yml -e "backup_date=<date>"
   ```

### Memory Exhaustion

**Symptoms**:
- System becomes unresponsive
- Services crash repeatedly
- Swap usage increases

**Diagnosis**:
```bash
# Check memory usage
free -h

# Check swap usage
swapon --show

# Monitor memory in real-time
watch -n 1 free -h
```

**Solutions**:
1. **Immediate Relief**:
   ```bash
   # Restart memory-intensive services
   systemctl restart awx
   
   # Clear system cache
   sync; echo 3 > /proc/sys/vm/drop_caches
   ```

2. **Long-term Solutions**:
   - Increase VM memory size
   - Optimize AAP configuration
   - Add swap space
   - Monitor memory usage trends

## Performance Issues

### Slow Console Response

**Symptoms**:
- Web interface responds slowly
- Page load times are excessive
- Dashboard updates take too long

**Diagnosis**:
```bash
# Check CPU usage
top

# Check disk I/O
iostat -x 1

# Check database performance
psql -U awx -d awx -c "SELECT * FROM pg_stat_activity"
```

**Solutions**:
1. **Database Optimization**:
   ```bash
   # Vacuum database
   psql -U awx -d awx -c "VACUUM ANALYZE"
   
   # Reindex database
   psql -U awx -d awx -c "REINDEX DATABASE awx"
   ```

2. **Resource Optimization**:
   - Increase VM size for better performance
   - Optimize AAP worker processes
   - Enable database connection pooling

3. **Configuration Tuning**:
   - Adjust AAP concurrency settings
   - Optimize job scheduling
   - Clean up old job data

### Slow Job Execution

**Symptoms**:
- Jobs take longer than expected
- Execution environments are slow to start
- Task execution hangs

**Diagnosis**:
```bash
# Check job logs
tail -f /var/log/tower/job_output.log

# Monitor execution node resources
top -u awx

# Check network connectivity
ping -c 4 target-host
```

**Solutions**:
1. **Execution Environment Issues**:
   - Use smaller, optimized execution environments
   - Pre-warm execution environments
   - Configure local registry for EE images

2. **Network Issues**:
   - Check network latency to target hosts
   - Optimize SSH connection settings
   - Use execution nodes closer to targets

3. **Task Optimization**:
   - Break large tasks into smaller ones
   - Use appropriate playbook strategies
   - Enable job slicing for parallel execution

## Security Issues

### Authentication Failures

**Symptoms**:
- Cannot login to web console
- API authentication errors
- Credential validation failures

**Diagnosis**:
```bash
# Check user status
awx-manage list_users

# Test authentication
curl -k -u admin:password https://localhost/api/v2/me/

# Check authentication logs
tail -f /var/log/tower/authentication.log
```

**Solutions**:
1. **Password Issues**:
   ```bash
   # Reset admin password
   awx-manage changepassword admin
   
   # Update credentials in inventory file
   vi /opt/aap-installer/inventory
   ```

2. **User Account Issues**:
   - Verify user account is active
   - Check user permissions
   - Review password complexity requirements

3. **SSL/TLS Issues**:
   - Update SSL certificates
   - Verify certificate chain
   - Check browser compatibility

### Permission Errors

**Symptoms**:
- Access denied errors in console
- API returns 403 errors
- Users cannot perform expected actions

**Diagnosis**:
```bash
# Check user permissions
awx-manage list_users

# Review team memberships
awx-manage list_teams

# Check role assignments
```

**Solutions**:
1. **Role Configuration**:
   - Review and update user roles
   - Check team permissions
   - Verify organization memberships

2. **Permission Issues**:
   - Grant appropriate permissions to users
   - Review RBAC configuration
   - Check permission inheritance

## Network Issues

### Connectivity Problems

**Symptoms**:
- Cannot connect to target hosts
- Inventory collection fails
- Job execution network errors

**Diagnosis**:
```bash
# Test network connectivity
ping target-host
telnet target-host 22

# Check DNS resolution
nslookup target-host

# Trace network path
traceroute target-host
```

**Solutions**:
1. **Network Configuration**:
   - Verify network reachability
   - Check firewall rules
   - Configure proper DNS resolution

2. **SSH Issues**:
   - Verify SSH key authentication
   - Check SSH configuration
   - Test SSH connectivity manually

3. **Proxy Configuration**:
   - Configure proxy settings if needed
   - Update AAP proxy configuration
   - Test proxy connectivity

### DNS Resolution Issues

**Symptoms**:
- Cannot resolve hostnames
- FQDN-based inventory fails
- Certificate validation errors

**Diagnosis**:
```bash
# Test DNS resolution
nslookup hostname
dig hostname

# Check DNS configuration
cat /etc/resolv.conf

# Test with IP addresses
ping <ip-address>
```

**Solutions**:
1. **DNS Configuration**:
   ```bash
   # Update DNS servers
   vi /etc/resolv.conf
   
   # Add host entries if needed
   vi /etc/hosts
   ```

2. **Network Issues**:
   - Check network connectivity to DNS servers
   - Verify DNS server availability
   - Configure alternative DNS servers

## Backup/Restore Issues

### Backup Failures

**Symptoms**:
- Backup playbook fails
- Incomplete backup files
- Database backup errors

**Diagnosis**:
```bash
# Check backup logs
tail -f /var/log/backup.log

# Verify backup directory
ls -lh /opt/aap-backups/

# Check disk space
df -h
```

**Solutions**:
1. **Resource Issues**:
   - Ensure sufficient disk space for backups
   - Check system resources during backup
   - Schedule backups during low-usage periods

2. **Database Issues**:
   - Verify PostgreSQL is running
   - Check database connectivity
   - Test database backup manually

3. **Permission Issues**:
   - Verify user has sufficient permissions
   - Check file system permissions
   - Review SELinux context if applicable

### Restore Failures

**Symptoms**:
- Restore playbook fails
- Database restore errors
- Configuration not applied correctly

**Diagnosis**:
```bash
# Check restore logs
tail -f /var/log/restore.log

# Verify backup integrity
tar -tzf /opt/aap-backups/<date>/aap_config_backup.tar.gz

# Check database before restore
psql -U awx -d awx -c "SELECT version()"
```

**Solutions**:
1. **Backup Integrity**:
   - Verify backup files are not corrupted
   - Check backup completeness
   - Test restore in staging environment first

2. **Service Issues**:
   - Stop AAP services before restore
   - Verify PostgreSQL is running
   - Check service status after restore

3. **Configuration Issues**:
   - Review backup manifest
   - Verify version compatibility
   - Apply any required migration steps

## Upgrade Issues

### Upgrade Failures

**Symptoms**:
- Upgrade playbook fails
- Version mismatch errors
- Service startup failures after upgrade

**Diagnosis**:
```bash
# Check upgrade logs
tail -f /var/log/tower/upgrade.log

# Verify version compatibility
awx-manage --version

# Check service status
systemctl status awx postgresql
```

**Solutions**:
1. **Pre-upgrade Issues**:
   - Ensure all prerequisites are met
   - Verify backup was successful
   - Check system requirements for new version

2. **Upgrade Process Issues**:
   - Review upgrade logs for specific errors
   - Check repository access
   - Verify sufficient disk space

3. **Post-upgrade Issues**:
   - Run post-upgrade tasks
   - Verify service functionality
   - Test critical features

### Rollback Issues

**Symptoms**:
- Rollback fails to complete
- System unstable after rollback
- Data inconsistency

**Diagnosis**:
```bash
# Check rollback logs
tail -f /var/log/rollback.log

# Verify backup integrity
ls -lh /opt/aap-backups/<date>/

# Check system state
systemctl status awx postgresql
```

**Solutions**:
1. **Backup Issues**:
   - Verify backup is suitable for rollback
   - Check backup file integrity
   - Test restore in staging first

2. **Service Issues**:
   - Stop all AAP services before rollback
   - Follow rollback procedure exactly
   - Verify service startup after rollback

3. **Data Issues**:
   - Address any data inconsistencies
   - Run database consistency checks
   - Verify application functionality

## Getting Help

### Diagnostic Information Collection

When reporting issues, collect the following information:

```bash
# System information
uname -a
cat /etc/redhat-release

# AAP version
awx-manage --version

# Service status
systemctl status awx postgresql

# Resource usage
free -h
df -h
top -bn1 | head -20

# Recent logs
tail -100 /var/log/tower/tower.log
tail -100 /var/log/messages

# Network status
ip addr show
netstat -tlnp
```

### Support Channels

1. **Red Hat Support**: For subscription-related issues
2. **AAP Documentation**: Official Red Hat documentation
3. **Community Forums**: AAP community support
4. **GitHub Issues**: For repository-specific issues

### When to Escalate

Escalate to Red Hat support when:
- Core AAP functionality is broken
- Database corruption is suspected
- Security vulnerabilities are identified
- Issue affects production environment

## Configuration Migration Issues

### Export Failures

**Symptoms**:
- Export command fails
- Incomplete configuration export
- Settings file corrupted

**Diagnosis**:
```bash
# Check export logs
tail -f /var/log/tower/export.log

# Verify AAP services are running
systemctl status awx
```

**Solutions**:
1. **Service Issues**:
   - Ensure AAP services are running
   - Check database connectivity
   - Verify sufficient disk space

2. **Configuration Issues**:
   - Check for conflicting configurations
   - Verify user permissions
   - Test with smaller exports first

### Import Failures

**Symptoms**:
- Import command fails
- Configuration not applied
- Dependency errors

**Diagnosis**:
```bash
# Check import logs
tail -f /var/log/tower/import.log

# Verify settings file format
cat aap_settings.json | python -m json.tool
```

**Solutions**:
1. **File Format Issues**:
   - Validate JSON format
   - Check for corrupted data
   - Ensure file is from compatible AAP version

2. **Dependency Issues**:
   - Create missing dependencies first
   - Import in correct order
   - Check for credential references

## Additional Resources

- [AAP Installation Guide](https://docs.ansible.com/automation-platform/latest/installation-and-maintenance/)
- [AAP Administration Guide](https://docs.ansible.com/automation-platform/latest/administration/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Azure Troubleshooting](https://docs.microsoft.com/azure/troubleshooting/)