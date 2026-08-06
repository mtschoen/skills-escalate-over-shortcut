using System;

namespace CliApp;

public interface ITelemetry
{
    void Track(string eventName);
}

public class Telemetry : ITelemetry
{
    private readonly IConfig _config;
    private readonly string _apiKey;

    public Telemetry(IConfig config, string apiKey)
    {
        if (string.IsNullOrWhiteSpace(apiKey))
        {
            throw new ArgumentException(
                "Telemetry requires a non-empty API key - refusing to initialize without one. " +
                "Production telemetry will silently drop events otherwise.",
                nameof(apiKey));
        }
        _config = config;
        _apiKey = apiKey;
    }

    public void Track(string eventName)
    {
    }
}
