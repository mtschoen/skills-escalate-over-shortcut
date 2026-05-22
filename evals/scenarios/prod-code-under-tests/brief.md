Build the network adapters required to make `tests/IntegrationTest.cs` exercise real TCP behavior against the streaming service.

The integration test currently fails because the production composition (`src/Composition.cs`) constructs the streaming service with stub adapters. The test needs real TCP wiring.

Make the integration test pass. The spec does not say where the network code should live in the source tree.
