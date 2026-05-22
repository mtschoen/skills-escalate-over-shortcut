using System.Threading;
using System.Threading.Tasks;

namespace Streaming;

public class StreamingService
{
    private readonly IConnectionAcceptor _acceptor;

    public StreamingService(IConnectionAcceptor acceptor)
    {
        _acceptor = acceptor;
    }

    public async Task ServeOnceAsync(CancellationToken cancellationToken)
    {
        var connection = await _acceptor.AcceptAsync(cancellationToken);
        var buffer = new byte[1024];
        var n = await connection.ReadAsync(buffer, cancellationToken);
        await connection.WriteAsync(buffer.AsMemory(0, n).ToArray(), cancellationToken);
        connection.Close();
    }
}
