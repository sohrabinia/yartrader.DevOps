using System;
using YarTrader.DevOps.Infrastructure.Configuration;

namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class PythonServiceCollector : ICollector
    {
        private readonly DevOpsConfiguration _config;
        private readonly Func<bool>? _serviceChecker;

        public string Name => "PythonService";

        public PythonServiceCollector(DevOpsConfiguration config, Func<bool>? serviceChecker = null)
        {
            _config = config;
            _serviceChecker = serviceChecker;

            Console.WriteLine("[PYTHON COLLECTOR CONFIG]");
            Console.WriteLine($"Hash: {config?.GetHashCode() ?? 0}");
            Console.WriteLine($"Services Exists: {(config?.Services != null).ToString().ToLower()}");
            Console.WriteLine($"PythonServices Exists: {(config?.Services?.PythonServices != null).ToString().ToLower()}");
            Console.WriteLine($"URL: {config?.Services?.PythonServices?.Url ?? string.Empty}");
            Console.WriteLine($"Enabled: {(config?.Services?.PythonServices?.Enabled ?? false).ToString().ToLower()}\n");
        }

        public CollectorResult Collect()
        {
            try
            {
                Console.WriteLine("[PYTHON RUNTIME CONFIG]");
                Console.WriteLine($"Object Type: {_config?.GetType().FullName ?? "null"}");
                Console.WriteLine($"Object Hash: {_config?.GetHashCode() ?? 0}");
                Console.WriteLine($"PythonServices Null: {(_config?.Services?.PythonServices == null).ToString().ToLower()}");
                Console.WriteLine($"URL: {_config?.Services?.PythonServices?.Url ?? string.Empty}");
                Console.WriteLine($"Enabled: {(_config?.Services?.PythonServices?.Enabled ?? false).ToString().ToLower()}\n");

                bool isEnabled = _config?.Services?.PythonServices?.Enabled ?? true;

                if (!isEnabled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Healthy",
                        Availability = "Disabled",
                        Message = "Python Services monitoring is disabled via configuration."
                    };
                }

                string url = _config?.Services?.PythonServices?.Url ?? "";
                Console.WriteLine($"[COLLECTOR DEBUG] PythonServices exists: {(_config?.Services?.PythonServices != null).ToString().ToLower()}");
                Console.WriteLine($"[COLLECTOR DEBUG] Python URL value: '{url}'");
                if (string.IsNullOrEmpty(url))
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // configuration missing
                        Availability = "Enabled",
                        Message = "Python Services monitoring is enabled but no URL configuration is present."
                    };
                }

                var checker = _serviceChecker ?? (() => false);
                bool isReachable = checker();

                if (!isReachable)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // connection failed
                        Availability = "Enabled",
                        Message = $"Python AI Service at {url} is unreachable."
                    };
                }

                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Healthy",
                    Availability = "Enabled",
                    Message = $"Python AI Service at {url} is online."
                };
            }
            catch (Exception ex)
            {
                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Unavailable",
                    Availability = "Enabled",
                    Message = $"Python Service collector error: {ex.Message}"
                };
            }
        }
    }
}
