using System;

namespace CliApp;

public interface ICliServices
{
    IConfig Config { get; }
    ILogger Logger { get; }
    ITelemetry Telemetry { get; }
    ICommandDispatcher Dispatcher { get; }
}

public class CliServicesContainer : ICliServices
{
    public IConfig Config { get; }
    public ILogger Logger { get; }
    public ITelemetry Telemetry { get; }
    public ICommandDispatcher Dispatcher { get; }

    public CliServicesContainer(IConfig config, ILogger logger, ITelemetry telemetry, ICommandDispatcher dispatcher)
    {
        Config = config;
        Logger = logger;
        Telemetry = telemetry;
        Dispatcher = dispatcher;
    }
}

public static class CliServices
{
    public static ICliServices CreateDefault()
    {
        throw new NotImplementedException("TODO: compose production services");
    }
}
