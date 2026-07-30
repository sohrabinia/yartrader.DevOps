using System;
using System.Threading.Tasks;

namespace TradeYar.DevOps.Core.Logging
{
    public interface IAuditLogger
    {
        Task LogActionAsync(string user, string action, string resource, string details);
    }

    public class ConsoleAuditLogger : IAuditLogger
    {
        public Task LogActionAsync(string user, string action, string resource, string details)
        {
            Console.WriteLine($"[AUDIT] {DateTime.UtcNow:o} | User: {user} | Action: {action} | Resource: {resource} | Details: {details}");
            return Task.CompletedTask;
        }
    }
}
