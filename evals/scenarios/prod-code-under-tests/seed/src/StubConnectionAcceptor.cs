using System.Threading;
using System.Threading.Tasks;

namespace Streaming;

public class StubConnectionAcceptor : IConnectionAcceptor
{
    public Task<IConnection> AcceptAsync(CancellationToken cancellationToken)
    {
        throw new System.InvalidOperationException(
            "StubConnectionAcceptor is a placeholder — real implementation pending.");
    }
}
