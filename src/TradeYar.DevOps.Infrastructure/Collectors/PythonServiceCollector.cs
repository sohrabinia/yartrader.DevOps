using System;
using TradeYar.DevOps.Infrastructure.Configuration;

namespace TradeYar.DevOps.Infrastructure.Collectors
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
        }

        public CollectorResult Collect()
        {
            try
            {
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
