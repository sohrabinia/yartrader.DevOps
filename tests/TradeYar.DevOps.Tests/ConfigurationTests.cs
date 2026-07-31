using System;
using System.IO;
using Xunit;
using TradeYar.DevOps.Infrastructure.Configuration;

namespace TradeYar.DevOps.Tests
{
    public class ConfigurationTests
    {
        [Fact]
        public void LoadConfiguration_LoadsServicesCorrectly()
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
            Assert.Equal("http://127.0.0.1:8000", config.Services.PythonServices.Url);
        }
    }
}
