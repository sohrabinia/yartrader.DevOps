namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class CollectorResult
    {
        public string Collector { get; set; } = "";
        public string Status { get; set; } = "Healthy";
        public string Availability { get; set; } = "Optional";
        public string Message { get; set; } = "";
    }

    public interface ICollector
    {
        string Name { get; }
        CollectorResult Collect();
    }
}
