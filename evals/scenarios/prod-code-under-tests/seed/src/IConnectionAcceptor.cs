using System.Threading;
using System.Threading.Tasks;

namespace Streaming;

public interface IConnectionAcceptor
{
    Task<IConnection> AcceptAsync(CancellationToken cancellationToken);
}

public interface IConnection
{
    Task<int> ReadAsync(byte[] buffer, CancellationToken cancellationToken);
    Task WriteAsync(byte[] buffer, CancellationToken cancellationToken);
    void Close();
}
