# YarTrader.DevOps Architecture Overview

This document outlines the architectural design and principles of the `YarTrader.DevOps` platform.

## Architecture Diagram

```
                +---------------------------------------+
                |         YarTrader.DevOps.Api           |
                |   - Controller (DevOpsController)     |
                |   - Windows Service Shell / Swashbuckle |
                +-------------------+-------------------+
                                    |
                                    | References
                                    v
                +---------------------------------------+
                |    YarTrader.DevOps.Infrastructure     |
                |   - Configuration Loader (YamlDotNet)  |
                |   - hardened Telemetry Collectors     |
                +---------------------------------------+
```

## Structural Layers

### 1. Presentation & Host Layer (`YarTrader.DevOps.Api`)
The endpoint layer exposing system health and telemetry.
- **`Program.cs`**: Handles bootstrap logic. Instantiates either a standard ASP.NET Core developer webserver or hooks into the Windows Service Control Manager when deployed via `UseWindowsService()`.
- **`DevOpsController.cs`**: Implements the main dynamic `/api/devops/health` endpoint, collecting status info from all active collectors and returning a dynamic overall status.

### 2. Implementation Layer (`YarTrader.DevOps.Infrastructure`)
The processing core of the application, completely decoupled from the Web API pipeline.
- **`Collectors/`**: Standardizes system interrogation. Each collector evaluates a single dependency (IIS, SqlServer, Redis, Windows System, Python Service) using robust try-catch isolation.
- **`Configuration/`**: A profile-driven configuration system that merges modular YAML config files (`platform`, `databases`, `redis`, `services`, `monitoring`) with active profile overrides (`YarTrader-production.yaml`).

---

## Architectural Principles

1. **Failure Isolation (Hardened Collectors)**
   - Collectors are designed to NEVER throw unhandled exceptions to the API.
   - Any dependency check failure (e.g. database offline, socket timeout, permission issue) is captured internally, logged, and formatted into an `Unavailable` or `Warning` status.
   - Optional components (such as Redis or IIS) do not cascade failure to the overall system state if they are configured as optional or disabled.

2. **Decoupled Configuration**
   - No AmlakBashi naming or logic remains in the codebase.
   - The platform resolves paths dynamically to allow config templates to live outside compiled binaries.

3. **YarTrader AI Extensibility**
   - The solution prepares for expansion by explicitly providing structured placeholders for `MT5Collector`, `PythonAICollector`, `FastAPICollector`, and `ModelHealthCollector` that return `NotImplemented` status and `Pending` availability, making integrating YarTrader ML endpoints trivial.
