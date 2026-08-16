using System.Net;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;
using YarTrader.DevOps.Api;
using YarTrader.DevOps.Infrastructure.Collectors;
using System.Collections.Generic;

namespace YarTrader.DevOps.Tests
{
    public class IntegrationTests : IClassFixture<WebApplicationFactory<IApiMarker>>
    {
        private readonly WebApplicationFactory<IApiMarker> _factory;

        public IntegrationTests(WebApplicationFactory<IApiMarker> factory)
        {
            _factory = factory;
        }

        [Fact]
        public async Task GetHealthEndpoint_ReturnsSuccessAndValidContract()
        {
            // Arrange
            var client = _factory.CreateClient();

            // Act
            var response = await client.GetAsync("/api/devops/health");

            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);

            var content = await response.Content.ReadFromJsonAsync<HealthResponse>();
            Assert.NotNull(content);
            Assert.NotNull(content.Status);
            Assert.NotNull(content.Timestamp);
            Assert.NotNull(content.Components);

            // Ensure the main standard components exist in response
            Assert.True(content.Components.ContainsKey("Iis"));
            Assert.True(content.Components.ContainsKey("SqlServer"));
            Assert.True(content.Components.ContainsKey("Redis"));
            Assert.True(content.Components.ContainsKey("WindowsSystem"));
            Assert.True(content.Components.ContainsKey("PythonService"));
            Assert.True(content.Components.ContainsKey("MT5Collector"));
            Assert.True(content.Components.ContainsKey("PythonAICollector"));
            Assert.True(content.Components.ContainsKey("FastAPICollector"));
            Assert.True(content.Components.ContainsKey("ModelHealthCollector"));
        }

        private class HealthResponse
        {
            public string Status { get; set; } = "";
            public string Timestamp { get; set; } = "";
            public Dictionary<string, CollectorDetail> Components { get; set; } = new();
        }

        private class CollectorDetail
        {
            public string Status { get; set; } = "";
            public string Availability { get; set; } = "";
            public string Message { get; set; } = "";
        }
    }
}
