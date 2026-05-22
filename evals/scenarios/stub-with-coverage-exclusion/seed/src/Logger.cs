using System.IO;

namespace CliApp;

public interface ILogger
{
    void Info(string message);
}

public class Logger : ILogger
{
    private readonly string _logFile;

    public Logger(string logFile)
    {
        _logFile = logFile;
    }

    public void Info(string message)
    {
    }

    public static string DefaultLogFile =>
        Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.UserProfile), ".cliapp", "cliapp.log");
}
