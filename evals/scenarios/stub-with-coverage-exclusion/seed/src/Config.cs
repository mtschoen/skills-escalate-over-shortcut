using System.IO;

namespace CliApp;

public interface IConfig
{
    string Get(string key);
}

public class Config : IConfig
{
    private readonly string _path;

    public Config(string configPath)
    {
        _path = configPath;
    }

    public string Get(string key) => $"stub-value-for-{key}";

    public static string DefaultPath =>
        Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.UserProfile), ".cliapp", "config.json");
}
