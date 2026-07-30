using System;

namespace TradeYar.DevOps.Shared
{
    public static class DateTimeUtils
    {
        public static string GetIsoTimestamp()
        {
            return DateTime.UtcNow.ToString("o");
        }
    }
}
