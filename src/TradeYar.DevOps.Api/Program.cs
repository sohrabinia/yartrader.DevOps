using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Hosting.WindowsServices;
using Microsoft.OpenApi.Models;
using System;
using System.IO;
using TradeYar.DevOps.Infrastructure.Collectors;
using TradeYar.DevOps.Infrastructure.Configuration;
using TradeYar.DevOps.Core.Events;
using TradeYar.DevOps.Core.Logging;

namespace TradeYar.DevOps.Api
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var options = new WebApplicationOptions
            {
                Args = args,
                ContentRootPath = WindowsServiceHelpers.IsWindowsService()
                    ? AppContext.BaseDirectory
                    : null
            };

            var builder = WebApplication.CreateBuilder(options);

            // Enable Windows Service deployment
            builder.Host.UseWindowsService(serviceOptions =>
            {
                serviceOptions.ServiceName = "TradeYar-DevOps";
            });

            // Load configurations
            var baseDir = AppContext.BaseDirectory;
            var configDir = Path.Combine(baseDir, "config");
            var profileDir = Path.Combine(baseDir, "profiles");

            // If local directory doesn't have it, try repository root/relative paths
            if (!Directory.Exists(configDir))
            {
                configDir = Path.Combine(Directory.GetCurrentDirectory(), "config");
            }
            if (!Directory.Exists(profileDir))
            {
                profileDir = Path.Combine(Directory.GetCurrentDirectory(), "profiles");
            }

            var loader = new ConfigurationLoader();
            var devOpsConfig = loader.LoadConfiguration(configDir, profileDir);

            // Safe startup diagnostics logging
            Console.WriteLine("[CONFIG INSTANCE]");
            Console.WriteLine($"Hash: {devOpsConfig!.GetHashCode()}");
            Console.WriteLine($"Services Exists: {(devOpsConfig?.Services != null).ToString().ToLower()}");
            Console.WriteLine($"PythonServices Exists: {(devOpsConfig?.Services?.PythonServices != null).ToString().ToLower()}");
            Console.WriteLine($"Python URL: {devOpsConfig?.Services?.PythonServices?.Url ?? string.Empty}");
            Console.WriteLine($"Python Enabled: {(devOpsConfig?.Services?.PythonServices?.Enabled ?? false).ToString().ToLower()}\n");

            builder.Services.AddSingleton(devOpsConfig!);

            // Core Abstractions
            builder.Services.AddSingleton<IEventBus, InMemoryEventBus>();
            builder.Services.AddSingleton<IAuditLogger, ConsoleAuditLogger>();

            // Register standard, production, and AI collectors
            builder.Services.AddSingleton<ICollector, IisCollector>();
            builder.Services.AddSingleton<ICollector, SqlServerCollector>();
            builder.Services.AddSingleton<ICollector, RedisCollector>();
            builder.Services.AddSingleton<ICollector, WindowsSystemCollector>();
            builder.Services.AddSingleton<ICollector, PythonServiceCollector>();
            builder.Services.AddSingleton<ICollector, MT5Collector>();
            builder.Services.AddSingleton<ICollector, PythonAICollector>();
            builder.Services.AddSingleton<ICollector, FastAPICollector>();
            builder.Services.AddSingleton<ICollector, ModelHealthCollector>();

            // Add Controllers with explicit application part for robust test scanning
            builder.Services.AddControllers()
                .AddApplicationPart(typeof(IApiMarker).Assembly);

            // Configure Swagger
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "TradeYar.DevOps.Api",
                    Version = "v1",
                    Description = "TradeYar AI DevOps foundation platform API."
                });
            });

            var app = builder.Build();

            // Use Swagger
            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "TradeYar.DevOps.Api v1");
                c.RoutePrefix = string.Empty; // Serve Swagger UI at root url
            });

            app.UseAuthorization();
            app.MapControllers();

            app.Run();
        }
    }
}
