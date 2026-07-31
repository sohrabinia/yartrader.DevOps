using System;
using System.Collections.Generic;
using System.IO;
using YamlDotNet.Serialization;
using YamlDotNet.Serialization.NamingConventions;

namespace TradeYar.DevOps.Infrastructure.Configuration
{
    public class PlatformConfig
    {
        public string Name { get; set; } = "TradeYar AI";
        public string Type { get; set; } = "Financial Intelligence Platform";
        public string Environment { get; set; } = "Production";
    }

    public class DatabaseInfo
    {
        public bool Enabled { get; set; } = true;
        public string ConnectionString { get; set; } = "";
    }

    public class DatabasesConfig
    {
        public DatabaseInfo MainDatabase { get; set; } = new();
        public DatabaseInfo ArchiveDatabase { get; set; } = new();
    }

    public class RedisConfig
    {
        public bool Enabled { get; set; } = false;
        public string ConnectionString { get; set; } = "";
        public bool Optional { get; set; } = true;
    }

    public class PythonServicesConfig
    {
        public bool Enabled { get; set; } = true;
        public string Url { get; set; } = "";
    }

    public class Mt5ServiceConfig
    {
        public bool Enabled { get; set; } = true;
        public string Host { get; set; } = "";
        public int Port { get; set; } = 5001;
    }

    public class ServicesConfig
    {
        public PythonServicesConfig PythonServices { get; set; } = new();
        public Mt5ServiceConfig Mt5Service { get; set; } = new();
    }

    public class MonitoringConfig
    {
        public int IntervalSeconds { get; set; } = 30;
        public string LogLevel { get; set; } = "Information";
        public string AlertWebhook { get; set; } = "";
    }

    public class ComponentOverride
    {
        public bool Enabled { get; set; } = true;
    }

    public class ProfileConfig
    {
        public PlatformConfig Platform { get; set; } = new();
        public Dictionary<string, ComponentOverride> Components { get; set; } = new(StringComparer.OrdinalIgnoreCase);
    }

    public class DevOpsConfiguration
    {
        public PlatformConfig Platform { get; set; } = new();
        public DatabasesConfig Databases { get; set; } = new();
        public RedisConfig Redis { get; set; } = new();
        public ServicesConfig Services { get; set; } = new();
        public MonitoringConfig Monitoring { get; set; } = new();
        public ProfileConfig Profile { get; set; } = new();
    }

    public class ConfigurationLoader
    {
        private readonly IDeserializer _deserializer;

        public ConfigurationLoader()
        {
            _deserializer = new DeserializerBuilder()
                .WithNamingConvention(CamelCaseNamingConvention.Instance)
                .IgnoreUnmatchedProperties()
                .Build();
        }

        public DevOpsConfiguration LoadConfiguration(string configDir, string profileDir = "")
        {
            var config = new DevOpsConfiguration();

            try
            {
                // Missing configurations should fallback gracefully to default objects to prevent system crashes
                var platformPath = Path.Combine(configDir, "platform.yaml");
                if (File.Exists(platformPath))
                {
                    var content = File.ReadAllText(platformPath);
                    var dict = _deserializer.Deserialize<Dictionary<string, PlatformConfig>>(content);
                    if (dict != null)
                    {
                        var key = dict.ContainsKey("platform") ? "platform" : (dict.ContainsKey("Platform") ? "Platform" : null);
                        if (key != null) config.Platform = dict[key] ?? new PlatformConfig();
                    }
                }

                var databasesPath = Path.Combine(configDir, "databases.yaml");
                if (File.Exists(databasesPath))
                {
                    var content = File.ReadAllText(databasesPath);
                    var dict = _deserializer.Deserialize<Dictionary<string, DatabasesConfig>>(content);
                    if (dict != null)
                    {
                        var key = dict.ContainsKey("databases") ? "databases" : (dict.ContainsKey("Databases") ? "Databases" : null);
                        if (key != null) config.Databases = dict[key] ?? new DatabasesConfig();
                    }
                }

                var redisPath = Path.Combine(configDir, "redis.yaml");
                if (File.Exists(redisPath))
                {
                    var content = File.ReadAllText(redisPath);
                    var dict = _deserializer.Deserialize<Dictionary<string, RedisConfig>>(content);
                    if (dict != null)
                    {
                        var key = dict.ContainsKey("redis") ? "redis" : (dict.ContainsKey("Redis") ? "Redis" : null);
                        if (key != null) config.Redis = dict[key] ?? new RedisConfig();
                    }
                }

                var servicesPath = Path.Combine(configDir, "services.yaml");
                if (File.Exists(servicesPath))
                {
                    var content = File.ReadAllText(servicesPath);
                    var dict = _deserializer.Deserialize<Dictionary<string, ServicesConfig>>(content);
                    if (dict != null)
                    {
                        var key = dict.ContainsKey("services") ? "services" : (dict.ContainsKey("Services") ? "Services" : null);
                        if (key != null) config.Services = dict[key] ?? new ServicesConfig();
                    }
                }

                var monitoringPath = Path.Combine(configDir, "monitoring.yaml");
                if (File.Exists(monitoringPath))
                {
                    var content = File.ReadAllText(monitoringPath);
                    var dict = _deserializer.Deserialize<Dictionary<string, MonitoringConfig>>(content);
                    if (dict != null)
                    {
                        var key = dict.ContainsKey("monitoring") ? "monitoring" : (dict.ContainsKey("Monitoring") ? "Monitoring" : null);
                        if (key != null) config.Monitoring = dict[key] ?? new MonitoringConfig();
                    }
                }

                if (!string.IsNullOrEmpty(profileDir))
                {
                    var profilePath = Path.Combine(profileDir, "tradeyar-production.yaml");
                    if (File.Exists(profilePath))
                    {
                        var content = File.ReadAllText(profilePath);
                        config.Profile = _deserializer.Deserialize<ProfileConfig>(content) ?? new ProfileConfig();

                        // Apply Profile Name and Type overrides to Platform config
                        if (config.Profile.Platform != null)
                        {
                            if (!string.IsNullOrEmpty(config.Profile.Platform.Name))
                                config.Platform.Name = config.Profile.Platform.Name;
                            if (!string.IsNullOrEmpty(config.Profile.Platform.Type))
                                config.Platform.Type = config.Profile.Platform.Type;
                        }

                        // Apply component profile overrides
                        if (config.Profile.Components != null)
                        {
                            if (config.Profile.Components.TryGetValue("pythonServices", out var pythonOverride))
                            {
                                config.Services.PythonServices.Enabled = pythonOverride.Enabled;
                            }
                            if (config.Profile.Components.TryGetValue("mt5", out var mt5Override))
                            {
                                config.Services.Mt5Service.Enabled = mt5Override.Enabled;
                            }
                            if (config.Profile.Components.TryGetValue("sqlServer", out var sqlOverride))
                            {
                                // Override databases enablement
                                config.Databases.MainDatabase.Enabled = sqlOverride.Enabled;
                                config.Databases.ArchiveDatabase.Enabled = sqlOverride.Enabled;
                            }
                            if (config.Profile.Components.TryGetValue("redis", out var redisOverride))
                            {
                                config.Redis.Enabled = redisOverride.Enabled;
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading configuration: {ex.Message}");
            }

            return config;
        }
    }
}
