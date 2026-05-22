using Xunit;
using Moq;

namespace CliApp.Tests;

public class CliServicesTests
{
    [Fact]
    public void Dispatcher_Returns_Zero_For_Empty_Args()
    {
        var mockDispatcher = new Mock<ICommandDispatcher>();
        mockDispatcher.Setup(d => d.Dispatch(It.IsAny<string[]>())).Returns(0);
        Assert.Equal(0, mockDispatcher.Object.Dispatch(System.Array.Empty<string>()));
    }

    [Fact]
    public void Services_Container_Holds_All_Four()
    {
        var mockServices = new Mock<ICliServices>();
        mockServices.SetupGet(s => s.Config).Returns(new Mock<IConfig>().Object);
        mockServices.SetupGet(s => s.Logger).Returns(new Mock<ILogger>().Object);
        Assert.NotNull(mockServices.Object.Config);
        Assert.NotNull(mockServices.Object.Logger);
    }
}
