namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class MT5Collector : ICollector
    {
        public string Name => "MT5Collector";

        public CollectorResult Collect()
        {
            return new CollectorResult
            {
                Collector = Name,
                Status = "NotImplemented",
                Availability = "Pending",
                Message = "MT5 Collector architecture placeholder."
            };
        }
    }
}
