# Upgrade and Configuration Migration Guide

## Overview

This guide covers upgrading Ansible Automation Platform (AAP) and migrating configurations. Always test upgrades in a non-production environment first.

## Prerequisites

### Before Upgrade

- [ ] Complete backup of current installation
- [ ] Verify current AAP version and health status
- [ ] Review release notes for target version
- [ ] Check system requirements for new version
- [ ] Plan maintenance window (30-60 minutes expected)
- [ ] Test upgrade in staging environment

### System Requirements

Ensure your system meets the requirements for the target AAP version:
- Minimum 4 vCPUs, 16GB RAM
- At least 50GB free disk space
- Compatible RHEL version
- Sufficient database capacity

## Upgrade Process

### Automated Upgrade

Use the automated upgrade playbook:

```bash
cd playbooks
ansible-playbook -i inventory upgrade_aap.yml -e "target_version=2.5"
```

The playbook will:
1. Confirm upgrade intent
2. Create pre-upgrade backup
3. Perform health checks
4. Update repositories and installer
5. Run the upgrade process
6. Verify new version
7. Generate upgrade manifest

### Manual Upgrade

If you prefer manual control:

1. **Create Backup**
   ```bash
   ansible-playbook -i inventory backup_aap.yml
   ```

2. **Stop AAP Services**
   ```bash
   systemctl stop awx receptor
   ```

3. **Update Repositories**
   ```bash
   subscription-manager repos --enable=ansible-automation-platform-2.5-for-rhel-9-x86_64-rpms
   ```

4. **Update Installer**
   ```bash
   dnf update ansible-automation-platform-installer
   ```

5. **Update Inventory File**
   ```bash
   vi /opt/aap-installer/inventory
   # Update automation_platform_version to target version
   ```

6. **Run Upgrade**
   ```bash
   cd /usr/share/ansible-automation-platform-installer
   ./setup.sh -i /opt/aap-installer/inventory
   ```

7. **Start Services**
   ```bash
   systemctl start postgresql awx receptor
   ```

8. **Verify Upgrade**
   ```bash
   awx-manage --version
   ```

## Post-Upgrade Tasks

### Verification Steps

1. **Version Verification**
   ```bash
   awx-manage --version
   ```

2. **Console Access**
   - Access web console
   - Verify all users can login
   - Check job templates display correctly

3. **Job Execution**
   - Run test job templates
   - Verify execution environments work
   - Check credential functionality

4. **Integration Testing**
   - Test cloud provider integrations
   - Verify webhook functionality
   - Check external systems connectivity

### Configuration Updates

**Breaking Changes**: Review the release notes for configuration changes that may require manual updates:

```bash
# Check for deprecated settings
grep -r "deprecated" /etc/tower/
```

**Execution Environments**: Rebuild or update custom execution environments if needed:

```bash
# Update EE images
podman pull registry.redhat.io/ansible-automation-platform/ee-<version>:latest
```

**Database Migrations**: The installer handles database migrations automatically, but verify completion:

```bash
# Check migration logs
tail -f /var/log/tower/migration.log
```

## Rollback Procedures

### Automated Rollback

If the upgrade fails, use the automated rollback:

```bash
cd playbooks
ansible-playbook -i inventory restore_aap.yml \
  -e "backup_date=20260814T120000" \
  -e "restore_method=full"
```

### Manual Rollback

1. **Stop Services**
   ```bash
   systemctl stop awx receptor postgresql
   ```

2. **Restore Database**
   ```bash
   su - awx
   psql awx < /opt/aap-backups/<backup_date>/awx_db_backup.sql
   ```

3. **Restore Configuration**
   ```bash
   tar -xzf /opt/aap-backups/<backup_date>/aap_config_backup.tar.gz -C /
   ```

4. **Restart Services**
   ```bash
   systemctl start postgresql awx receptor
   ```

5. **Verify Version**
   ```bash
   awx-manage --version
   ```

## Configuration Migration

### Exporting Configuration

1. **Export AAP Configuration**
   ```bash
   # Export job templates, credentials, inventories
   awx-manage export_settings --indent 2 > aap_settings.json
   ```

2. **Backup Data**
   ```bash
   ansible-playbook -i inventory backup_aap.yml
   ```

### Importing Configuration

1. **Import AAP Configuration**
   ```bash
   awx-manage import_settings aap_settings.json
   ```

2. **Verify Configuration**
   ```bash
   # Check that all configurations are imported correctly
   awx-manage list_users
   awx-manage list_credentials
   ```

## Version-Specific Notes

### AAP 2.4 to 2.5

**Key Changes**:
- Updated execution environment images
- Enhanced RBAC permissions
- New API endpoints
- Performance improvements

**Required Actions**:
- Update custom execution environments
- Review RBAC permissions
- Test new API endpoints
- Update automation scripts if needed

### AAP 2.3 to 2.4

**Key Changes**:
- PostgreSQL version upgrade
- New webhook features
- Enhanced logging

**Required Actions**:
- Ensure PostgreSQL compatibility
- Review webhook configurations
- Update logging configurations

## Troubleshooting

### Upgrade Fails Mid-Process

**Issue**: Upgrade stops during installation
**Solution**:
1. Check logs: `/var/log/tower/`
2. Verify service status: `systemctl status awx postgresql`
3. Review installer output for specific errors
4. Consider rollback if critical issues

### Database Migration Errors

**Issue**: Database migration fails
**Solution**:
1. Check PostgreSQL service status
2. Verify database disk space
3. Review migration logs
4. Manually run migration if needed

### Execution Environment Issues

**Issue**: Custom EEs not working after upgrade
**Solution**:
1. Rebuild custom execution environments
2. Update base image references
3. Verify EE registry credentials
4. Test EE functionality manually

### Web Console Not Accessible

**Issue**: Cannot access web console after upgrade
**Solution**:
1. Check web service status: `systemctl status awx`
2. Verify web port: `netstat -tlnp | grep 443`
3. Check nginx/tower configuration
4. Review web logs: `/var/log/tower/`

## Best Practices

### Upgrade Planning

1. **Schedule maintenance windows** during low-usage periods
2. **Communicate upgrades** to all stakeholders
3. **Document current configuration** before upgrade
4. **Test in staging** first
5. **Have rollback plan** ready

### Risk Mitigation

1. **Always backup** before upgrading
2. **Monitor system resources** during upgrade
3. **Keep detailed logs** of upgrade process
4. **Verify each step** before proceeding
5. **Have support contacts** ready

### Continuous Improvement

1. **Document lessons learned** from each upgrade
2. **Refine upgrade procedures** based on experience
3. **Monitor system performance** post-upgrade
4. **Gather user feedback** on new features
5. **Plan next upgrade cycle**

## Additional Resources

- [AAP Release Notes](https://docs.ansible.com/automation-platform/latest/release-notes/)
- [AAP Upgrade Documentation](https://docs.ansible.com/automation-platform/latest/installation-and-maintenance/upgrade/)
- [Red Hat Customer Portal](https://access.redhat.com/)
- [AAP Community Forums](https://forum.ansible.com/)