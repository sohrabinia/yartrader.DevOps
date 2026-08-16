using System;

namespace YarTrader.DevOps.Shared
{
    public static class DateTimeUtils
    {
        public static string GetIsoTimestamp()
        {
            return DateTime.UtcNow.ToString("o");
        }
    }
}
