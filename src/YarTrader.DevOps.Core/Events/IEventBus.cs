using System;
using System.Threading.Tasks;

namespace YarTrader.DevOps.Core.Events
{
    public interface IEventBus
    {
        Task PublishAsync<T>(T @event) where T : class;
        void Subscribe<T>(Func<T, Task> handler) where T : class;
    }

    public class InMemoryEventBus : IEventBus
    {
        private readonly System.Collections.Concurrent.ConcurrentDictionary<Type, System.Collections.Generic.List<Delegate>> _handlers = new();

        public Task PublishAsync<T>(T @event) where T : class
        {
            if (_handlers.TryGetValue(typeof(T), out var handlers))
            {
                foreach (var handler in handlers)
                {
                    var typedHandler = (Func<T, Task>)handler;
                    Task.Run(() => typedHandler(@event));
                }
            }
            return Task.CompletedTask;
        }

        public void Subscribe<T>(Func<T, Task> handler) where T : class
        {
            _handlers.AddOrUpdate(typeof(T),
                new System.Collections.Generic.List<Delegate> { handler },
                (key, list) => { list.Add(handler); return list; });
        }
    }
}
