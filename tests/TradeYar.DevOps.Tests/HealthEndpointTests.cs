using Xunit;
using TradeYar.DevOps.Api.Controllers;
using TradeYar.DevOps.Infrastructure.Collectors;
using TradeYar.DevOps.Infrastructure.Configuration;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic;
using System;
using System.Text.Json;

namespace TradeYar.DevOps.Tests
{
    public class HealthEndpointTests
    {
        [Fact]
        public void GetHealth_WhenAllCollectorsHealthy_ReturnsHealthy()
        {
            // Arrange
            var config = new DevOpsConfiguration();
            config.Platform.Name = "TradeYar AI";

            var mockCollectors = new List<ICollector>
            {
                new TestCollector("Iis", "Healthy", "Enabled"),
                new TestCollector("SqlServer", "Healthy", "Enabled")
            };

            var controller = new DevOpsController(config, mockCollectors);

            // Act
            var result = controller.GetHealth();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var json = JsonSerializer.Serialize(okResult.Value);
            var doc = JsonDocument.Parse(json);

            Assert.Equal("Healthy", doc.RootElement.GetProperty("status").GetString());
        }

        [Fact]
        public void GetHealth_WhenSomeCollectorUnavailableButNotCritical_ReturnsDegraded()
        {
            // Arrange
            var config = new DevOpsConfiguration();

            var mockCollectors = new List<ICollector>
            {
                new TestCollector("Iis", "Unavailable", "Optional"),
                new TestCollector("SqlServer", "Healthy", "Enabled")
            };

            var controller = new DevOpsController(config, mockCollectors);

            // Act
            var result = controller.GetHealth();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var json = JsonSerializer.Serialize(okResult.Value);
            var doc = JsonDocument.Parse(json);

            Assert.Equal("Degraded", doc.RootElement.GetProperty("status").GetString());
        }

        [Fact]
        public void GetHealth_WhenCriticalSqlServerCollectorUnavailable_ReturnsUnhealthy()
        {
            // Arrange
            var config = new DevOpsConfiguration();

            var mockCollectors = new List<ICollector>
            {
                new TestCollector("Iis", "Healthy", "Enabled"),
                new TestCollector("SqlServer", "Unavailable", "Enabled") // Critical because it is Enabled
            };

            var controller = new DevOpsController(config, mockCollectors);

            // Act
            var result = controller.GetHealth();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var json = JsonSerializer.Serialize(okResult.Value);
            var doc = JsonDocument.Parse(json);

            Assert.Equal("Unhealthy", doc.RootElement.GetProperty("status").GetString());
        }

        [Fact]
        public void GetHealth_WhenControllerThrows_ReturnsUnhealthyGracefully()
        {
            // Arrange
            var controller = new DevOpsController(null!, null!); // Force throwing null reference exception

            // Act
            var result = controller.GetHealth();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var json = JsonSerializer.Serialize(okResult.Value);
            var doc = JsonDocument.Parse(json);

            Assert.Equal("Unhealthy", doc.RootElement.GetProperty("status").GetString());
        }
    }

    public class TestCollector : ICollector
    {
        public string Name { get; }
        private readonly string _status;
        private readonly string _availability;

        public TestCollector(string name, string status, string availability)
        {
            Name = name;
            _status = status;
            _availability = availability;
        }

        public CollectorResult Collect()
        {
            return new CollectorResult
            {
                Collector = Name,
                Status = _status,
                Availability = _availability,
                Message = "Simulated check"
            };
        }
    }
}
