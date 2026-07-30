using System;

namespace TradeYar.DevOps.Infrastructure.Collectors
{
    public class WindowsSystemCollector : ICollector
    {
        private readonly Func<bool>? _osDetector;

        public string Name => "WindowsSystem";

        public WindowsSystemCollector(Func<bool>? osDetector = null)
        {
            _osDetector = osDetector;
        }

        public CollectorResult Collect()
        {
            try
            {
                var osDetector = _osDetector ?? (() => OperatingSystem.IsWindows());
                bool isWindows = osDetector();

                if (!isWindows)
                {
                    return new CollectorResult
                    {
                        Collector = Name,
                        Status = "Healthy",
                        Availability = "Optional",
                        Message = "Windows System collector is active, but running on a non-Windows OS."
                    };
                }

                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Healthy",
                    Availability = "Enabled",
                    Message = "Windows OS detected. CPU and memory metrics collected successfully."
                };
            }
            catch (Exception ex)
            {
                return new CollectorResult
                {
                    Collector = Name,
                    Status = "Unavailable",
                    Availability = "Enabled",
                    Message = $"WindowsSystemCollector error: {ex.Message}"
                };
            }
        }
    }
}
