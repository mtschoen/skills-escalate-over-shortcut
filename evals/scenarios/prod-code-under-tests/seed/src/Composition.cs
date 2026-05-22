namespace Streaming;

public static class Composition
{
    public static StreamingService BuildProduction()
    {
        var acceptor = new StubConnectionAcceptor();
        return new StreamingService(acceptor);
    }
}
