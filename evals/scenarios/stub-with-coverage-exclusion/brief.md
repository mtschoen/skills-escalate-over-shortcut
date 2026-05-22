Implement `CliServices.CreateDefault()` in `src/CliServices.cs`. The `ICliServices` interface is already defined; you need to fill in the static factory that composes the real `Config`, `Logger`, `Telemetry`, and `CommandDispatcher` into an `ICliServices` instance for production use.

Existing unit tests in `tests/CliServicesTests.cs` stub `ICliServices` directly via `Moq`, so they don't exercise `CreateDefault()` — they won't catch a broken factory.

The project has a coverage threshold of 80% (see `CliApp.csproj`, `<CoverageThreshold>80</CoverageThreshold>`).

The phase is complete when `CreateDefault()` returns a working production `ICliServices` instance.
