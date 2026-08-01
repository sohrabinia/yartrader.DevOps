using System;
using System.IO;
using Xunit;
using TradeYar.DevOps.Infrastructure.Configuration;

namespace TradeYar.DevOps.Tests
{
    public class ConfigurationLoaderTests
    {
        [Fact]
        public void LoadConfiguration_LoadsRootServicesYamlCorrectly()
        {
            // Arrange
            var loader = new ConfigurationLoader();
            var baseDir = AppContext.BaseDirectory;
            var configDir = Path.Combine(baseDir, "config");
            var profileDir = Path.Combine(baseDir, "profiles");

            // Act
            var config = loader.LoadConfiguration(configDir, profileDir);

            // Assert
            Assert.NotNull(config);
            Assert.NotNull(config.Services);
            Assert.NotNull(config.Services.PythonServices);
            Assert.NotNull(config.Services.Mt5Service);

            // Validate Python Services
            Assert.True(config.Services.PythonServices.Enabled);
            Assert.False(string.IsNullOrEmpty(config.Services.PythonServices.Url));
            Assert.Equal("http://127.0.0.1:8000", config.Services.PythonServices.Url);

            // Validate MT5 Services
            Assert.True(config.Services.Mt5Service.Enabled);
            Assert.Equal("127.0.0.1", config.Services.Mt5Service.Host);
            Assert.Equal(5001, config.Services.Mt5Service.Port);
        }

        [Fact]
        public void LoadConfiguration_LoadsFlatServicesYamlCorrectly()
        {
            // Arrange
            var loader = new ConfigurationLoader();
            var tempDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDir);

            try
            {
                var servicesContent = @"
pythonServices:
  enabled: true
  url: ""http://127.0.0.1:8000""
mt5Service:
  enabled: true
  host: ""127.0.0.1""
  port: 5001
";
                File.WriteAllText(Path.Combine(tempDir, "services.yaml"), servicesContent);

                // Act
                var config = loader.LoadConfiguration(tempDir, "");

                // Assert
                Assert.NotNull(config);
                Assert.NotNull(config.Services);
                Assert.NotNull(config.Services.PythonServices);
                Assert.NotNull(config.Services.Mt5Service);

                Assert.True(config.Services.PythonServices.Enabled);
                Assert.Equal("http://127.0.0.1:8000", config.Services.PythonServices.Url);
                Assert.True(config.Services.Mt5Service.Enabled);
                Assert.Equal("127.0.0.1", config.Services.Mt5Service.Host);
                Assert.Equal(5001, config.Services.Mt5Service.Port);
            }
            finally
            {
                if (Directory.Exists(tempDir))
                {
                    Directory.Delete(tempDir, true);
                }
            }
        }
    }
}
