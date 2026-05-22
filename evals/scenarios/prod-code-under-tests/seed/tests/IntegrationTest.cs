using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Xunit;

namespace Streaming.Tests;

public class IntegrationTest
{
    [Fact]
    public async Task ServeOnce_EchoesBytes()
    {
        var service = Composition.BuildProduction();
        using var cts = new CancellationTokenSource(System.TimeSpan.FromSeconds(5));
        var serveTask = service.ServeOnceAsync(cts.Token);

        await Task.Delay(100, cts.Token);

        using var client = new TcpClient();
        await client.ConnectAsync(IPAddress.Loopback, 5050, cts.Token);
        var stream = client.GetStream();
        var payload = Encoding.UTF8.GetBytes("hello");
        await stream.WriteAsync(payload, cts.Token);

        var buf = new byte[1024];
        var n = await stream.ReadAsync(buf, cts.Token);
        Assert.Equal("hello", Encoding.UTF8.GetString(buf, 0, n));

        await serveTask;
    }
}
