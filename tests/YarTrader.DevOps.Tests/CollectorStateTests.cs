using Xunit;
using YarTrader.DevOps.Infrastructure.Collectors;
using YarTrader.DevOps.Infrastructure.Configuration;
using System;

namespace YarTrader.DevOps.Tests
{
    public class CollectorStateTests
    {
        [Fact]
        public void IisCollector_WhenDisabledInConfig_ReturnsHealthyAndDisabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Profile.Components["iis"] = new ComponentOverride { Enabled = false };
            var collector = new IisCollector(config, () => true);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Iis", result.Collector);
            Assert.Equal("Healthy", result.Status);
            Assert.Equal("Disabled", result.Availability);
        }

        [Fact]
        public void IisCollector_WhenMissingInEnvironment_ReturnsUnavailableAndOptional()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            var collector = new IisCollector(config, () => false); // Simulates IIS not installed

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Iis", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Optional", result.Availability);
        }

        [Fact]
        public void IisCollector_WhenHealthy_ReturnsHealthyAndEnabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            var collector = new IisCollector(config, () => true); // Simulates IIS installed

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Iis", result.Collector);
            Assert.Equal("Healthy", result.Status);
            Assert.Equal("Enabled", result.Availability);
        }

        [Fact]
        public void SqlServerCollector_WhenDisabled_ReturnsHealthyAndDisabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Databases.MainDatabase.Enabled = false;
            var collector = new SqlServerCollector(config, () => true, () => true);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("SqlServer", result.Collector);
            Assert.Equal("Healthy", result.Status);
            Assert.Equal("Disabled", result.Availability);
        }

        [Fact]
        public void SqlServerCollector_WhenNotInstalled_ReturnsUnavailableAndNotInstalled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Databases.MainDatabase.Enabled = true;
            var collector = new SqlServerCollector(config, () => false); // Simulates SQL not installed

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("SqlServer", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Not Installed", result.Availability);
        }

        [Fact]
        public void SqlServerCollector_WhenConnectionFailsCompletely_ReturnsUnavailableAndEnabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Databases.MainDatabase.Enabled = true;
            var collector = new SqlServerCollector(config, () => true, () => false, () => false);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("SqlServer", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Enabled", result.Availability);
        }

        [Fact]
        public void SqlServerCollector_WhenPartiallyAvailable_ReturnsWarningAndEnabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Databases.MainDatabase.Enabled = true;
            var collector = new SqlServerCollector(config, () => true, () => true, () => false);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("SqlServer", result.Collector);
            Assert.Equal("Warning", result.Status);
            Assert.Equal("Enabled", result.Availability);
        }

        [Fact]
        public void SqlServerCollector_WhenDetectorThrowsException_DoesNotCrashAndReturnsUnavailable()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            var collector = new SqlServerCollector(config, () => throw new Exception("Timeout simulated"));

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("SqlServer", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Enabled", result.Availability);
            Assert.Contains("Timeout simulated", result.Message);
        }

        [Fact]
        public void RedisCollector_WhenDisabled_ReturnsHealthyAndDisabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Redis.Enabled = false;
            var collector = new RedisCollector(config, () => true, () => true);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Redis", result.Collector);
            Assert.Equal("Healthy", result.Status);
            Assert.Equal("Disabled", result.Availability);
        }

        [Fact]
        public void RedisCollector_WhenMissingOptional_ReturnsUnavailableAndOptional()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Redis.Enabled = true;
            var collector = new RedisCollector(config, () => false);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Redis", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Optional", result.Availability);
        }

        [Fact]
        public void RedisCollector_WhenConnectionFails_ReturnsUnavailableAndEnabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Redis.Enabled = true;
            var collector = new RedisCollector(config, () => true, () => false);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("Redis", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Enabled", result.Availability);
        }

        [Fact]
        public void PythonServiceCollector_WhenConfigurationMissing_ReturnsUnavailableAndEnabled()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Services.PythonServices.Enabled = true;
            config.Services.PythonServices.Url = ""; // Missing configuration
            var collector = new PythonServiceCollector(config);

            // Act
            var result = collector.Collect();

            // Assert
            Assert.Equal("PythonService", result.Collector);
            Assert.Equal("Unavailable", result.Status);
            Assert.Equal("Enabled", result.Availability);
            Assert.Contains("no URL configuration is present", result.Message);
        }
    }
}
