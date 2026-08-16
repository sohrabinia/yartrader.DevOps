namespace YarTrader.DevOps.Infrastructure.Collectors
{
    public class ModelHealthCollector : ICollector
    {
        public string Name => "ModelHealthCollector";

        public CollectorResult Collect()
        {
            return new CollectorResult
            {
                Collector = Name,
                Status = "NotImplemented",
                Availability = "Pending",
                Message = "Model Health Collector architecture placeholder."
            };
        }
    }
}
