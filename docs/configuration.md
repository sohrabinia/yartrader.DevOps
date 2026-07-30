# TradeYar.DevOps Configuration Guide

The `TradeYar.DevOps` configuration engine uses simple, clean YAML files designed to support dynamic, multi-profile overrides.

## Configuration Structure

The configuration files reside in two main directories:

- `/config`: Holds default base infrastructure parameters.
- `/profiles`: Holds environment-specific overrides (e.g. production vs development).

```
config/
 ├── platform.yaml
 ├── databases.yaml
 ├── redis.yaml
 ├── services.yaml
 └── monitoring.yaml

profiles/
 └── tradeyar-production.yaml
```

---

## Configuration Details

### 1. Platform Base (`config/platform.yaml`)
Defines default identity.
```yaml
platform:
  name: "TradeYar AI"
  type: "Financial Intelligence Platform"
  environment: "Production"
```

### 2. Databases Configuration (`config/databases.yaml`)
Maintains connection parameters.
```yaml
databases:
  mainDatabase:
    enabled: true
    connectionString: "Server=tradeyar-prod-sql;Database=TradeYarDb;Trusted_Connection=True;"
  archiveDatabase:
    enabled: true
    connectionString: "Server=tradeyar-prod-sql;Database=TradeYarArchiveDb;Trusted_Connection=True;"
```

### 3. Redis Telemetry (`config/redis.yaml`)
Handles cache state tracking.
```yaml
redis:
  enabled: false
  connectionString: "tradeyar-prod-redis:6379"
  optional: true
```

### 4. Services Integration (`config/services.yaml`)
Configures microservice URLs for Python AI agents and MT5 proxies.
```yaml
services:
  pythonServices:
    enabled: true
    url: "http://tradeyar-prod-ai:8000"
  mt5Service:
    enabled: true
    host: "tradeyar-prod-mt5"
    port: 5001
```

### 5. Monitoring Parameters (`config/monitoring.yaml`)
Adjusts engine intervals and webhook targets.
```yaml
monitoring:
  intervalSeconds: 30
  logLevel: "Information"
  alertWebhook: "https://alerts.tradeyar.dev/webhook"
```

---

## Active Profiles (`profiles/tradeyar-production.yaml`)

This profile overrides base configs for production deployments.

```yaml
platform:
  name: TradeYar AI
  type: Financial Intelligence Platform

components:
  pythonServices:
    enabled: true
  mt5:
    enabled: true
  sqlServer:
    enabled: false
  redis:
    enabled: false
  iis:
    enabled: false
```

## Resiliency Policies
- **Missing Files**: The loader tolerates missing files gracefully by utilizing robust structural defaults.
- **Malformed Content**: In case of invalid YAML syntax, the loader logs the error, falls back to safe defaults, and keeps the API running.
