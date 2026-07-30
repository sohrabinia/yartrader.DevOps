using Microsoft.Extensions.DependencyInjection;

namespace TradeYar.DevOps.Core.Modules
{
    public interface IModule
    {
        string Name { get; }
        void ConfigureServices(IServiceCollection services);
    }

    public class ModuleInfo
    {
        public string Name { get; set; } = "";
        public bool IsLoaded { get; set; } = true;
        public string Version { get; set; } = "1.0.0";
    }
}
