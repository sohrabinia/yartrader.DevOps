using System;
using YarTrader.DevOps.Infrastructure.Configuration;

namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class IisCollector : ICollector
    {
        private readonly DevOpsConfiguration _config;
        private readonly Func<bool>? _iisDetector;

        public string Name => "Iis";

        public IisCollector(DevOpsConfiguration config, Func<bool>? iisDetector = null)
        {
            _config = config;
            _iisDetector = iisDetector;
        }

        public CollectorResult Collect()
        {
            try
            {
                // Check if IIS is disabled in config
                bool isEnabled = true;
                if (_config?.Profile?.Components != null && _config.Profile.Components.TryGetValue("iis", out var overrideVal))
                {
                    isEnabled = overrideVal.Enabled;
                }

                if (!isEnabled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Healthy",
                        Availability = "Disabled",
                        Message = "IIS monitoring is disabled via configuration profile."
                    };
                }

                var iisDetector = _iisDetector ?? (() => false);
                bool isInstalled = iisDetector();
                if (!isInstalled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // dependency missing
                        Availability = "Optional",
                        Message = "IIS is not installed or missing from this environment."
                    };
                }

                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Healthy",
                    Availability = "Enabled",
                    Message = "IIS is installed and healthy."
                };
            }
            catch (Exception ex)
            {
                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Unavailable",
                    Availability = "Enabled",
                    Message = $"IIS collector encountered an error: {ex.Message}"
                };
            }
        }
    }
}
