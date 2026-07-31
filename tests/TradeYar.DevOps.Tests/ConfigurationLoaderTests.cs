using System;
using System.IO;
using Xunit;
using TradeYar.DevOps.Infrastructure.Configuration;

namespace TradeYar.DevOps.Tests
{
    public class ConfigurationLoaderTests
    {
        [Fact]
        public void LoadConfiguration_LoadsServicesYamlCorrectly()
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
    }
}
