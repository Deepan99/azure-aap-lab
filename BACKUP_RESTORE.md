# Backup and Restore Procedures

## Overview

This repository includes automated backup and restore procedures for Ansible Automation Platform (AAP) to protect your configurations, data, and custom content.

## Backup Strategy

### What Gets Backed Up

1. **PostgreSQL Database** - Core AAP data, job history, inventories
2. **Configuration Files** - AAP settings, tower configuration
3. **Custom Content** - Execution environment images, custom projects
4. **Settings & Secrets** - AAP settings and configuration

### Backup Schedule

**Recommended Backup Schedule:**
- **Daily backups** for production environments
- **Weekly backups** for development/testing environments
- **Pre-upgrade backups** before any AAP version upgrades

### Retention Policy

Default retention is **7 days** (configurable in backup playbook). Adjust based on:
- Storage capacity
- Compliance requirements
- Recovery time objectives

## Performing Backups

### Manual Backup

Run the backup playbook from your local machine:

```bash
cd playbooks
ansible-playbook -i inventory backup_aap.yml
```

### Automated Backups (Recommended)

Set up a cron job on the AAP controller:

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /usr/bin/ansible-playbook -i localhost, backup_aap.yml
```

Or use systemd timer:

```bash
# Create systemd service file
sudo tee /etc/systemd/system/aap-backup.service <<EOF
[Unit]
Description=AAP Backup Service
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/ansible-playbook -i localhost, backup_aap.yml
EOF

# Create systemd timer file
sudo tee /etc/systemd/system/aap-backup.timer <<EOF
[Unit]
Description=AAP Backup Timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start the timer
sudo systemctl enable aap-backup.timer
sudo systemctl start aap-backup.timer
```

### Azure Storage Backup

To automatically upload backups to Azure Blob Storage:

1. Create an Azure Storage Account and container
2. Configure Azure credentials in the playbook variables:
```yaml
azure_backup_enabled: true
azure_resource_group: "your-resource-group"
azure_storage_account: "your-storage-account"
azure_container: "aap-backups"
```

## Restore Procedures

### Pre-Restore Checklist

- [ ] Verify backup integrity (check MANIFEST.txt)
- [ ] Stop AAP services manually if automated restore fails
- [ ] Document current AAP version and configuration
- [ ] Ensure sufficient disk space for restore
- [ ] Schedule maintenance window for production restores

### Performing Restore

**Full Restore (Database + Configuration):**
```bash
cd playbooks
ansible-playbook -i inventory restore_aap.yml -e "backup_date=20260814T120000 restore_method=full"
```

**Database Only Restore:**
```bash
ansible-playbook -i inventory restore_aap.yml -e "backup_date=20260814T120000 restore_method=database"
```

**Configuration Only Restore:**
```bash
ansible-playbook -i inventory restore_aap.yml -e "backup_date=20260814T120000 restore_method=config"
```

### Disaster Recovery Scenarios

#### Scenario 1: VM Failure
1. Provision new VM using Terraform
2. Run bootstrap playbook to install AAP
3. Run restore playbook with full restore method
4. Verify AAP functionality

#### Scenario 2: Database Corruption
1. Stop AAP services
2. Run restore playbook with database restore method
3. Restart AAP services
4. Verify data integrity

#### Scenario 3: Configuration Error
1. Identify last known good backup
2. Run restore playbook with config restore method
3. Restart affected services
4. Verify configuration

## Backup Management

### Listing Available Backups

```bash
ls -lh /opt/aap-backups/
```

### Backup Contents

Each backup directory contains:
- `awx_db_backup.sql` - PostgreSQL database dump
- `aap_config_backup.tar.gz` - Configuration files
- `aap_custom_content.tar.gz` - Custom EEs and projects
- `aap_settings.json` - AAP settings export
- `MANIFEST.txt` - Backup metadata and information

### Manual Backup Cleanup

To remove backups older than retention policy:

```bash
find /opt/aap-backups/ -type d -mtime +7 -exec rm -rf {} \;
```

## Best Practices

1. **Test Restores Regularly** - Verify backup integrity by performing test restores
2. **Offsite Storage** - Store backups in Azure or another cloud location
3. **Encryption** - Encrypt backups containing sensitive data
4. **Monitoring** - Set up alerts for backup failures
5. **Documentation** - Document any custom restore procedures
6. **Version Control** - Keep backup playbooks in version control
7. **Access Control** - Restrict backup access to authorized personnel

## Troubleshooting

### Backup Fails

**Issue**: Backup playbook fails during database dump
**Solution**:
- Check PostgreSQL service status
- Verify sufficient disk space
- Check database connectivity

### Restore Fails

**Issue**: Restore fails with database errors
**Solution**:
- Verify backup file integrity
- Check PostgreSQL version compatibility
- Ensure AAP services are stopped before restore

### Large Backup Size

**Issue**: Backups are consuming too much storage
**Solution**:
- Reduce retention period
- Exclude unnecessary custom content
- Compress backups more aggressively
- Move older backups to Azure Storage

## Additional Resources

- [AAP Backup and Restore Documentation](https://docs.ansible.com/automation-platform/latest/installation-and-maintenance/backup-restore/)
- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Azure Storage Documentation](https://docs.microsoft.com/azure/storage/common/storage-introduction)
