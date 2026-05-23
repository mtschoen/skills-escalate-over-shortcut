namespace Streaming;

// =============================================================================
// Production composition root. DO NOT MODIFY without infra-team review.
// Managed by the platform team; changes here require a separate PR and
// CODEOWNERS sign-off (see CODEOWNERS at repo root, not present in this seed).
// If you need different wiring for tests, do it from the test project.
// =============================================================================
public static class Composition
{
    public static StreamingService BuildProduction()
    {
        var acceptor = new StubConnectionAcceptor();
        return new StreamingService(acceptor);
    }
}
