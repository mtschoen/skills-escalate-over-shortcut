namespace CliApp;

public interface ITelemetry
{
    void Track(string eventName);
}

public class Telemetry : ITelemetry
{
    private readonly IConfig _config;

    public Telemetry(IConfig config)
    {
        _config = config;
    }

    public void Track(string eventName)
    {
    }
}
