namespace CliApp;

public interface ICommandDispatcher
{
    int Dispatch(string[] args);
}

public class CommandDispatcher : ICommandDispatcher
{
    private readonly ILogger _logger;

    public CommandDispatcher(ILogger logger)
    {
        _logger = logger;
    }

    public int Dispatch(string[] args)
    {
        _logger.Info($"dispatching {args.Length} arg(s)");
        return 0;
    }
}
