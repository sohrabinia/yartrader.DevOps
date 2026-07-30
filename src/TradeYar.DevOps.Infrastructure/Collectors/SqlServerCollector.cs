using System;
using TradeYar.DevOps.Infrastructure.Configuration;

namespace TradeYar.DevOps.Infrastructure.Collectors
{
    public class SqlServerCollector : ICollector
    {
        private readonly DevOpsConfiguration _config;
        private readonly Func<bool>? _sqlDetector;
        private readonly Func<bool>? _sqlConnectionChecker;
        private readonly Func<bool>? _archiveConnectionChecker;

        public string Name => "SqlServer";

        public SqlServerCollector(
            DevOpsConfiguration config,
            Func<bool>? sqlDetector = null,
            Func<bool>? sqlConnectionChecker = null,
            Func<bool>? archiveConnectionChecker = null)
        {
            _config = config;
            _sqlDetector = sqlDetector;
            _sqlConnectionChecker = sqlConnectionChecker;
            _archiveConnectionChecker = archiveConnectionChecker;
        }

        public CollectorResult Collect()
        {
            try
            {
                bool isEnabled = _config?.Databases?.MainDatabase?.Enabled ?? true;

                if (!isEnabled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Healthy",
                        Availability = "Disabled",
                        Message = "SQL Server monitoring is disabled via configuration."
                    };
                }

                var sqlDetector = _sqlDetector ?? (() => false);
                bool isInstalled = sqlDetector();
                if (!isInstalled)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // dependency missing
                        Availability = "Not Installed",
                        Message = "SQL Server is not installed on this server."
                    };
                }

                var mainChecker = _sqlConnectionChecker ?? (() => false);
                var archiveChecker = _archiveConnectionChecker ?? (() => false);

                bool canConnectMain = mainChecker();
                bool canConnectArchive = archiveChecker();

                if (!canConnectMain && !canConnectArchive)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Unavailable", // connection failed completely
                        Availability = "Enabled",
                        Message = "SQL Server connection attempt failed for both Main and Archive databases."
                    };
                }

                if (!canConnectMain || !canConnectArchive)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Warning", // partially available
                        Availability = "Enabled",
                        Message = $"SQL Server is partially available. Main DB: {(canConnectMain ? "Healthy" : "Failed")}, Archive DB: {(canConnectArchive ? "Healthy" : "Failed")}."
                    };
                }

                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Healthy",
                    Availability = "Enabled",
                    Message = "SQL Server connections to both Main and Archive databases succeeded."
                };
            }
            catch (Exception ex)
            {
                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Unavailable",
                    Availability = "Enabled",
                    Message = $"SQL Server collector error: {ex.Message}"
                };
            }
        }
    }
}
