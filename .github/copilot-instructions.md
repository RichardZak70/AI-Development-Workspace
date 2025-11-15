# GitHub Copilot Instructions for AI Development Workspace

## Project Overview
This is a comprehensive multi-language development workspace template optimized for AI-assisted development. It supports Python, C/C++, Java, and C# with integrated quality tools, testing frameworks, and CI/CD pipelines.

## Code Style and Standards

### Python
- Use type hints for all functions and variables
- Follow PEP 8 style guide with 120 character line limit
- Use Ruff for linting and formatting
- Maintain cognitive complexity ≤15 per function
- Use docstrings for all classes and functions
- Prefer pathlib over os.path
- Use f-strings for string formatting
- Handle exceptions explicitly (avoid bare except)

### C/C++
- Follow Google C++ Style Guide
- Use C11 standard for C, C++17 for C++
- Maximum function complexity: 15
- Always use const correctness
- Prefer RAII and smart pointers in C++
- Use meaningful variable names
- Document all public APIs
- Include comprehensive error handling

### Java
- Follow Oracle Java conventions
- Use Java 11+ features
- Prefer composition over inheritance
- Use Optional for nullable return types
- Document public APIs with Javadoc
- Use try-with-resources for resource management

### C#
- Follow Microsoft C# conventions
- Use .NET 6+ features
- Use async/await for asynchronous operations
- Prefer records for immutable data
- Use nullable reference types
- Document public APIs with XML comments

## AI Development Patterns

### Code Generation Guidelines
- Generate complete, working code blocks
- Include comprehensive error handling
- Add logging and debugging information
- Consider edge cases and input validation
- Optimize for readability and maintainability
- Include unit tests when generating new functions

### Project Structure Awareness
- Understand the template-based project structure
- Follow established naming conventions
- Integrate with existing build systems (Makefile, Maven, etc.)
- Respect language-specific directory layouts
- Consider cross-platform compatibility

### Quality Integration
- Generate code that passes all quality checks
- Follow security best practices
- Consider performance implications
- Use appropriate data structures and algorithms
- Maintain backwards compatibility when possible

## Testing Strategy

### Python
- Use pytest for testing
- Aim for >80% code coverage
- Include unit, integration, and property-based tests
- Use mock objects for external dependencies
- Test edge cases and error conditions

### C/C++
- Use appropriate testing framework (Google Test, etc.)
- Include memory leak detection
- Test with different compiler optimizations
- Use static analysis tools
- Include performance benchmarks

### Java
- Use JUnit 5 for testing
- Include integration tests with TestContainers
- Use Mockito for mocking
- Test with different JVM versions
- Include performance and load tests

### C#
- Use xUnit for testing
- Include integration tests with WebApplicationFactory
- Use Moq for mocking
- Test async code properly
- Include API contract tests

## Common Patterns and Best Practices

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors with appropriate context
- Implement graceful degradation
- Consider retry mechanisms for transient failures

### Configuration Management
- Use environment variables for secrets
- Provide sensible defaults
- Support configuration files (JSON/YAML)
- Validate configuration on startup
- Document all configuration options

### Logging and Monitoring
- Use structured logging (JSON format)
- Include correlation IDs for tracing
- Log at appropriate levels (DEBUG/INFO/WARN/ERROR)
- Avoid logging sensitive information
- Include performance metrics

### Security Considerations
- Validate all inputs
- Use parameterized queries for databases
- Implement proper authentication and authorization
- Follow OWASP guidelines
- Regular security dependency updates

## AI Tool Integration

### GitHub Copilot
- Provide clear, descriptive comments for better suggestions
- Break complex problems into smaller functions
- Use meaningful variable and function names
- Review and test all generated code
- Understand the context before accepting suggestions

### Code Review Guidelines
- All AI-generated code must be reviewed
- Test thoroughly before merging
- Verify security implications
- Check for performance issues
- Ensure code follows project standards

## File Organization

### Directory Structure
```
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── templates/        # Project templates
├── .vscode/          # VS Code configuration
├── .github/          # GitHub workflows and templates
└── requirements.txt  # Dependencies
```

### Naming Conventions
- Use snake_case for Python files and functions
- Use PascalCase for C# classes and methods
- Use camelCase for Java methods and variables
- Use descriptive names that explain purpose
- Avoid abbreviations unless widely understood

## Continuous Integration

### Pre-commit Hooks
- All code must pass linting checks
- Format code automatically
- Run security scans
- Check for secrets in commits
- Validate configuration files

### CI/CD Pipeline
- Run all quality checks on every commit
- Test on multiple platforms and versions
- Generate and upload coverage reports
- Perform security vulnerability scans
- Deploy only after all checks pass

## Documentation Standards

### Code Documentation
- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Document configuration options
- Maintain up-to-date README files

### AI Context Documentation
- Document prompts used for code generation
- Explain AI tool decisions and trade-offs
- Include limitations and assumptions
- Provide alternative approaches considered
- Document validation and testing approaches

Remember: AI is a tool to enhance productivity, but human oversight and understanding remain essential for quality, security, and maintainability.
