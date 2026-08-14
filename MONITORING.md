# Monitoring and Logging Guide

## Overview

This repository includes comprehensive monitoring and logging configuration for Ansible Automation Platform (AAP) to ensure visibility into system health, performance, and operational status.

## Features

### Included Monitoring Components

1. **Enhanced Logging** - Detailed AAP application and system logs
2. **Log Rotation** - Automatic log management with configurable retention
3. **Metrics Exporter** - Prometheus-compatible metrics for system and AAP
4. **Health Checks** - Automated health monitoring with alerts
5. **Optional Integrations** - Azure Monitor, Prometheus, and Grafana support

## Quick Start

### Basic Monitoring Setup

Run the monitoring playbook to set up basic monitoring:

```bash
cd playbooks
ansible-playbook -i inventory setup_monitoring.yml
```

This will install:
- Enhanced logging configuration
- Log rotation setup
- Metrics exporter (available at http://localhost:9100/metrics)
- Automated health checks (every 5 minutes)

### Advanced Monitoring Setup

For advanced monitoring with Prometheus and Grafana:

```bash
ansible-playbook -i inventory setup_monitoring.yml \
  -e "install_prometheus=true" \
  -e "install_grafana=true"
```

For Azure Monitor integration:

```bash
ansible-playbook -i inventory setup_monitoring.yml \
  -e "install_azure_monitor=true" \
  -e "azure_workspace_id=YOUR_WORKSPACE_ID" \
  -e "azure_shared_key=YOUR_SHARED_KEY"
```

## Monitoring Components

### 1. Enhanced Logging

**Configuration**: `/etc/tower/conf.d/logging.py`

**Features**:
- Detailed logging format with timestamps, modules, and thread information
- Rotating file handler (100MB max, 5 backup files)
- Separate loggers for Django and AWX components
- Console and file output

**Log Locations**:
- AAP Application: `/var/log/tower/tower.log`
- AWX Jobs: `/var/log/awx/`
- System logs: `/var/log/messages`

### 2. Log Rotation

**Configuration**: `/etc/logrotate.d/aap`

**Default Retention**: 30 days (configurable)

**Features**:
- Daily rotation
- Compression of old logs
- Automatic service reload
- Configurable retention period

**Customize Retention**:
```bash
ansible-playbook -i inventory setup_monitoring.yml -e "log_retention_days=14"
```

### 3. Metrics Exporter

**Service**: `aap-metrics-exporter.service`
**Endpoint**: `http://localhost:9100/metrics`

**Available Metrics**:
- `aap_system_cpu_percent` - CPU usage percentage
- `aap_system_memory_percent` - Memory usage percentage
- `aap_system_disk_percent` - Disk usage percentage
- `aap_processes_count` - Number of AAP processes running

**Service Management**:
```bash
# Check status
systemctl status aap-metrics-exporter

# Restart service
systemctl restart aap-metrics-exporter

# View metrics
curl http://localhost:9100/metrics
```

### 4. Health Checks

**Script**: `/usr/local/bin/aap_health_check.sh`
**Schedule**: Every 5 minutes (cron)
**Log**: `/var/log/aap_health_check.log`

**Health Checks**:
- AAP API health (`/api/v2/ping/`)
- PostgreSQL service status
- AAP service status
- Disk space availability

**Manual Health Check**:
```bash
/usr/local/bin/aap_health_check.sh
```

**View Health Check Logs**:
```bash
tail -f /var/log/aap_health_check.log
```

### 5. Optional Integrations

#### Azure Monitor

**Prerequisites**:
- Azure Monitor workspace
- Azure Monitor agent installed

**Configuration**:
```yaml
install_azure_monitor: true
azure_workspace_id: "YOUR_WORKSPACE_ID"
azure_shared_key: "YOUR_SHARED_KEY"
```

**Features**:
- Syslog collection
- File-based log collection
- Azure Monitor integration
- Centralized logging

#### Prometheus

**Configuration**: `/etc/prometheus/prometheus.yml`

**Access**: `http://localhost:9090`

**Features**:
- Metrics scraping from AAP exporter
- 15-second scrape interval
- Built-in dashboard and query interface

#### Grafana

**Access**: `http://localhost:3000`
**Default Credentials**: admin/admin (change on first login)

**Features**:
- Dashboard creation
- Metrics visualization
- Alert configuration
- Plugin ecosystem

## Monitoring Best Practices

### 1. Alerting

Set up alerts for critical metrics:

```bash
# Example alert using cron and mail
0 * * * * /usr/local/bin/aap_health_check.sh || echo "AAP health check failed" | mail -s "AAP Alert" admin@example.com
```

### 2. Performance Monitoring

Monitor key performance indicators:
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%
- API response time > 5 seconds
- Failed job rates

### 3. Log Analysis

Regularly review logs for:
- Error patterns
- Failed authentication attempts
- Performance issues
- Anomalies in job execution

### 4. Capacity Planning

Track trends for:
- Storage growth
- Memory usage patterns
- CPU utilization trends
- Job execution frequency

## Troubleshooting

### Metrics Exporter Not Working

**Issue**: Metrics endpoint not accessible
**Solution**:
```bash
# Check service status
systemctl status aap-metrics-exporter

# Check service logs
journalctl -u aap-metrics-exporter -f

# Restart service
systemctl restart aap-metrics-exporter
```

### Health Check Fails

**Issue**: Health check script returns unhealthy status
**Solution**:
```bash
# Run manual health check
/usr/local/bin/aap_health_check.sh

# Check individual components
systemctl status awx
systemctl status postgresql
curl -k https://localhost/api/v2/ping/
```

### Logs Not Rotating

**Issue**: Log files growing too large
**Solution**:
```bash
# Test logrotate configuration
logrotate -d /etc/logrotate.d/aap

# Force log rotation
logrotate -f /etc/logrotate.d/aap

# Check logrotate configuration
cat /etc/logrotate.d/aap
```

### High Memory Usage

**Issue**: AAP consuming excessive memory
**Solution**:
```bash
# Check memory usage
free -h
ps aux | grep awx

# Review metrics
curl http://localhost:9100/metrics | grep memory

# Consider scaling or tuning AAP configuration
```

## Advanced Configuration

### Custom Metrics

Add custom metrics by modifying `/usr/local/bin/aap_metrics_exporter.py`:

```python
# Add custom AAP-specific metrics
job_count_gauge = Gauge('aap_job_count', 'Number of jobs')
# Add collection logic
```

### Custom Health Checks

Modify `/usr/local/bin/aap_health_check.sh` to add custom checks:

```bash
check_custom_application() {
    # Add your custom health check logic
}
```

### Logging Configuration

Customize logging in `/etc/tower/conf.d/logging.py`:

```python
# Add custom loggers or formatters
# Adjust log levels
# Add custom handlers
```

## Monitoring Integration Examples

### Prometheus Alertmanager

Configure Alertmanager for alerts:

```yaml
# prometheus-alerts.yml
groups:
  - name: aap_alerts
    rules:
      - alert: HighCPUUsage
        expr: aap_system_cpu_percent > 80
        for: 5m
        annotations:
          summary: "High CPU usage on AAP controller"
```

### Grafana Dashboards

Import pre-built AAP dashboards or create custom ones:

1. Access Grafana at `http://localhost:3000`
2. Navigate to Dashboards → Import
3. Use AAP metrics datasource
4. Create panels for CPU, memory, disk, and job metrics

### Azure Monitor Dashboards

Create Azure Monitor workbooks for AAP monitoring:

1. Navigate to Azure Monitor → Workbooks
2. Create custom workbook with AAP metrics
3. Set up alerts based on log data

## Maintenance

### Regular Tasks

**Weekly**:
- Review health check logs
- Check disk space and log sizes
- Verify metrics collection

**Monthly**:
- Review and tune alert thresholds
- Analyze performance trends
- Update monitoring configurations

**Quarterly**:
- Review monitoring strategy
- Update documentation
- Test backup and restore procedures

### Updates

Update monitoring components:

```bash
# Update Prometheus
dnf update prometheus

# Update Grafana
dnf update grafana

# Restart services
systemctl restart prometheus grafana-server
```

## Additional Resources

- [AAP Documentation](https://docs.ansible.com/automation-platform/latest/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Azure Monitor Documentation](https://docs.microsoft.com/azure/azure-monitor/)
