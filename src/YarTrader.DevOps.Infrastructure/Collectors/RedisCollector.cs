using System;
using YarTrader.DevOps.Infrastructure.Configuration;

namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class RedisCollector : ICollector
    {
        private readonly DevOpsConfiguration _config;
        private readonly Func<bool>? _redisDetector;
        private readonly Func<bool>? _redisConnectionChecker;

        public string Name => "Redis";

        public RedisCollector(DevOpsConfiguration config, Func<bool>? redisDetector = null, Func<bool>? redisConnectionChecker = null)
        {
            _config = config;
            _redisDetector = redisDetector;
            _redisConnectionChecker = redisConnectionChecker;
        }

        public CollectorResult Collect()
        {
            try
            {
                bool isEnabled = _config?.Redis?.Enabled ?? false;

                if (!isEnabled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Healthy",
                        Availability = "Disabled",
                        Message = "Redis monitoring is disabled via configuration."
                    };
                }

                var redisDetector = _redisDetector ?? (() => false);
                bool isInstalled = redisDetector();
                if (!isInstalled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // dependency missing
                        Availability = "Optional",
                        Message = "Redis is not installed or optional component missing."
                    };
                }

                var connectionChecker = _redisConnectionChecker ?? (() => false);
                bool canConnect = connectionChecker();
                if (!canConnect)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // connection failed
                        Availability = "Enabled",
                        Message = "Redis is enabled but connection failed."
                    };
                }

                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Healthy",
                    Availability = "Enabled",
                    Message = "Redis is running and connection succeeded."
                };
            }
            catch (Exception ex)
            {
                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Unavailable",
                    Availability = "Enabled",
                    Message = $"Redis collector error: {ex.Message}"
                };
            }
        }
    }
}
