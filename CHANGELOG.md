# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-30

### Added
- Created complete `YarTrader.DevOps` platform foundation from scratch.
- Implemented `YarTrader.DevOps.Api` Web API project supporting Windows Service integration, Swagger (title: `YarTrader.DevOps.Api`), and OpenAPI v1 specs.
- Implemented `YarTrader.DevOps.Infrastructure` telemetry engine.
- Created highly resilient, hardened, and configurable Collectors (`ICollector`, `IisCollector`, `SqlServerCollector`, `RedisCollector`, `WindowsSystemCollector`, `PythonServiceCollector`).
- Added placeholder collectors for YarTrader AI expansion: `MT5Collector`, `PythonAICollector`, `FastAPICollector`, `ModelHealthCollector`.
- Introduced fail-safe `ConfigurationLoader` that safely loads YAML configs (`platform.yaml`, `databases.yaml`, `redis.yaml`, `services.yaml`, `monitoring.yaml`) and `YarTrader-production.yaml` profiles with zero crash risk.
- Developed comprehensive xUnit testing suite (17 robust unit and integration tests) using test-host `WebApplicationFactory` for HTTP GET contract verification.
- Authored extensive system architecture, configuration, and deployment documentation.
