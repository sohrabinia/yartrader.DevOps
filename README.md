# YarTrader.DevOps

YarTrader.DevOps is a robust, independent production monitoring and DevOps platform custom-designed for **YarTrader AI**, a high-performance Financial Intelligence Platform. This solution has been engineered from the ground up, completely independent from legacy dependencies, to provide production-hardened infrastructure tracking, service telemetry, and MT5/AI model health diagnostics.

## Features

- **Decoupled Architecture**: Fully separated API (`YarTrader.DevOps.Api`) and Core/Telemetry engine (`YarTrader.DevOps.Infrastructure`).
- **Resilient Configuration**: Profile-based environment loading (`config/` and `profiles/`) supporting fail-safe parameters, graceful syntax error fallbacks, and multi-profile setups.
- **Production-Hardened Collectors**: Monitors IIS, SQL Server, Redis, and Windows Systems. Designed so that non-critical, missing, or optional dependencies do NOT crash the platform or mark it unhealthy unnecessarily.
- **AI-Monitoring Preparedness**: In-built architecture placeholders for `MT5Collector`, `PythonAICollector`, `FastAPICollector`, and `ModelHealthCollector` returning `NotImplemented` status and `Pending` availability, ready for rapid agent deployment.
- **Dynamic Health Status Calculation**: The `/api/devops/health` endpoint evaluates state dynamically, distinguishing between non-critical degraded optional modules versus critical component failures.
- **Windows Service Ready**: Supports running natively as a Windows Service (`YarTrader-DevOps`) with auto-start, crash recovery, graceful shutdown, and local file logging.

---

## Quick Start

### Prerequisites
- .NET 8.0 SDK or higher
- Supported on Linux (Docker/Kubernetes), macOS, and Windows

### Building the Project
Clone the repository and run:
```bash
dotnet build
```

### Running Tests
To run the comprehensive unit, integration, and resiliency tests:
```bash
dotnet test
```

### Running the API locally
```bash
dotnet run --project src/YarTrader.DevOps.Api
```
Once running, open your browser and navigate to:
- Swagger UI: `http://localhost:5000/` or `https://localhost:5001/` (at root `/` URL)
- Health Check: `http://localhost:5000/api/devops/health`

---

## Documentation

Comprehensive guides are available inside the `/docs` directory:
- [Architecture Guide](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [Deployment Guide](docs/deployment.md)
- [Production Readiness Checklist](docs/PRODUCTION_READINESS_CHECKLIST.md)
