namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class FastAPICollector : ICollector
    {
        public string Name => "FastAPICollector";

        public CollectorResult Collect()
        {
            return new CollectorResult
            {
                Collector = Name,
                Status = "NotImplemented",
                Availability = "Pending",
                Message = "FastAPI Collector architecture placeholder."
            };
        }
    }
}
