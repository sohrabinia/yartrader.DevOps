using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using YarTrader.DevOps.Infrastructure.Collectors;
using YarTrader.DevOps.Infrastructure.Configuration;
using YarTrader.DevOps.Core.Events;
using YarTrader.DevOps.Core.Modules;
using YarTrader.DevOps.Core.Logging;

namespace YarTrader.DevOps.Api.Controllers
{
    [ApiController]
    [Route("api/devops")]
    public class DevOpsController : ControllerBase
    {
        private readonly DevOpsConfiguration _config;
        private readonly IEnumerable<ICollector> _collectors;
        private readonly IEventBus _eventBus;
        private readonly IAuditLogger _auditLogger;

        private static readonly List<string> _simulatedEvents = new()
        {
            "System initialized successfully.",
            "Profile 'YarTrader-production' loaded.",
            "Redis optional check: NotInstalled."
        };

        public DevOpsController(
            DevOpsConfiguration config,
            IEnumerable<ICollector> collectors,
            IEventBus? eventBus = null,
            IAuditLogger? auditLogger = null)
        {
            _config = config;
            _collectors = collectors;
            _eventBus = eventBus ?? new InMemoryEventBus();
            _auditLogger = auditLogger ?? new ConsoleAuditLogger();
        }

        [HttpGet("health")]
        public IActionResult GetHealth()
        {
            try
            {
                var componentResults = new List<CollectorResult>();
                foreach (var collector in _collectors)
                {
                    componentResults.Add(collector.Collect());
                }

                string overallStatus = "Healthy";
                bool hasWarning = componentResults.Any(c => c.Status == "Warning");
                bool hasUnavailable = componentResults.Any(c => c.Status == "Unavailable");

                var sqlResult = componentResults.FirstOrDefault(c => c.Collector == "SqlServer");
                bool sqlFailed = sqlResult != null && sqlResult.Status == "Unavailable" && sqlResult.Availability == "Enabled";

                var pythonResult = componentResults.FirstOrDefault(c => c.Collector == "PythonService");
                bool pythonFailed = pythonResult != null && pythonResult.Status == "Unavailable" && pythonResult.Availability == "Enabled";

                if (sqlFailed || pythonFailed)
                {
                    overallStatus = "Unhealthy";
                }
                else if (hasWarning || hasUnavailable)
                {
                    overallStatus = "Degraded";
                }

                _auditLogger.LogActionAsync("System", "GET_Health", "devops/health", $"Calculated status: {overallStatus}");

                return Ok(new
                {
                    status = overallStatus,
                    timestamp = DateTime.UtcNow.ToString("o"),
                    components = componentResults.ToDictionary(c => c.Collector, c => new {
                        status = c.Status,
                        availability = c.Availability,
                        message = c.Message
                    })
                });
            }
            catch (Exception ex)
            {
                return Ok(new
                {
                    status = "Unhealthy",
                    timestamp = DateTime.UtcNow.ToString("o"),
                    error = ex.Message,
                    components = new Dictionary<string, object>()
                });
            }
        }

        [HttpGet("server")]
        public IActionResult GetServerInfo()
        {
            _auditLogger.LogActionAsync("User", "GET_Server", "devops/server", "Queried server details.");

            return Ok(new
            {
                os = Environment.OSVersion.ToString(),
                machineName = Environment.MachineName,
                processorCount = Environment.ProcessorCount,
                workingSet = Environment.WorkingSet,
                timestamp = DateTime.UtcNow.ToString("o"),
                runtime = ".NET " + Environment.Version
            });
        }

        [HttpGet("modules")]
        public IActionResult GetModules()
        {
            var modules = new List<ModuleInfo>
            {
                new() { Name = "YarTrader.DevOps.Core", IsLoaded = true, Version = "1.0.0" },
                new() { Name = "YarTrader.DevOps.Infrastructure", IsLoaded = true, Version = "1.0.0" },
                new() { Name = "YarTrader.DevOps.Shared", IsLoaded = true, Version = "1.0.0" }
            };

            _auditLogger.LogActionAsync("User", "GET_Modules", "devops/modules", $"Retrieved {modules.Count} modules.");

            return Ok(new
            {
                count = modules.Count,
                modules
            });
        }

        [HttpGet("collectors")]
        public IActionResult GetCollectors()
        {
            var summary = _collectors.Select(c => new
            {
                name = c.Name,
                type = c.GetType().Name
            }).ToList();

            _auditLogger.LogActionAsync("User", "GET_Collectors", "devops/collectors", $"Retrieved {summary.Count} collectors.");

            return Ok(new
            {
                count = summary.Count,
                collectors = summary
            });
        }

        [HttpGet("events")]
        public IActionResult GetEvents()
        {
            _auditLogger.LogActionAsync("User", "GET_Events", "devops/events", "Queried event bus logs.");

            return Ok(new
            {
                busType = _eventBus.GetType().Name,
                events = _simulatedEvents
            });
        }

        [HttpGet("policies")]
        public IActionResult GetPolicies()
        {
            _auditLogger.LogActionAsync("User", "GET_Policies", "devops/policies", "Queried monitoring threshold policies.");

            return Ok(new
            {
                intervalSeconds = _config.Monitoring.IntervalSeconds,
                logLevel = _config.Monitoring.LogLevel,
                alertWebhook = _config.Monitoring.AlertWebhook,
                rules = new[]
                {
                    new { condition = "CPU > 90%", severity = "Critical" },
                    new { condition = "MemoryAvailable < 10%", severity = "High" },
                    new { condition = "SQLConnectionTime > 5s", severity = "Warning" }
                }
            });
        }
    }
}
