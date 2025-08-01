# /test - Run Project Tests

Runs the project's test suite with appropriate configuration.

## Usage
```
/test [pattern] [--watch] [--coverage]
```

## Examples
- `/test` - Run all tests
- `/test unit` - Run tests matching "unit" pattern
- `/test --watch` - Run tests in watch mode
- `/test --coverage` - Run tests with coverage report

## Implementation

This command:

- Detects the testing framework used in the project
- Runs tests with appropriate configuration
- Provides clear output formatting
- Supports common testing patterns and options
- Handles different project types (Node.js, Python, etc.)

Common test commands supported:
- `npm test` / `yarn test` for Node.js projects
- `pytest` for Python projects
- `cargo test` for Rust projects
- `go test` for Go projects