# Contributing to AI Development Workspace

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer
- Adding support for new languages
- Improving AI integration

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

### Quality Standards

All contributions must meet our quality standards:

#### Python Code
- Use type hints for all function parameters and return values
- Follow PEP 8 with 120 character line limit
- Maintain cognitive complexity ≤15 per function
- 100% test coverage for new code
- Pass all Ruff, MyPy, and Bandit checks

#### C/C++ Code
- Follow Google C++ Style Guide
- Use C11 for C, C++17 for C++
- Pass clang-tidy and cppcheck analysis
- Include comprehensive error handling
- Maximum function complexity: 15

#### Java Code
- Follow Oracle Java conventions
- Use Java 11+ features
- Pass Checkstyle and SpotBugs analysis
- Document public APIs with Javadoc
- Include unit tests with JUnit 5

#### C# Code
- Follow Microsoft C# conventions
- Use .NET 6+ features
- Pass built-in analyzers
- Use nullable reference types
- Document public APIs with XML comments

### AI-Assisted Development Guidelines

#### When Using AI Tools
1. **Review all AI-generated code** thoroughly
2. **Test extensively** - AI code may have subtle bugs
3. **Verify security implications** - scan for vulnerabilities
4. **Check performance** - AI may not optimize for efficiency
5. **Ensure code style compliance** - run all linters
6. **Add proper documentation** - AI comments may be insufficient

#### AI Tool Usage Documentation
When submitting AI-assisted contributions:
- Mention which AI tools were used
- Describe the prompts or context provided
- Explain any modifications made to AI output
- Document testing and validation performed

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks include:
- **Ruff** (Python linting/formatting)
- **MyPy** (Python type checking)
- **Clang-format** (C/C++ formatting)
- **Prettier** (JSON/YAML/Markdown)
- **Security scans** (Bandit)
- **General checks** (trailing whitespace, file size)

## Adding New Language Support

To add support for a new programming language:

### 1. Create Template Structure
```bash
mkdir templates/your-language
cd templates/your-language
# Add template files (main source, build config, etc.)
```

### 2. Update VS Code Configuration
Add language-specific settings to:
- `.vscode/settings.json` - formatting and linting
- `.vscode/tasks.json` - build and test tasks
- `.vscode/extensions.json` - recommended extensions

### 3. Configure Quality Tools
Update these files:
- `.pre-commit-config.yaml` - add language-specific hooks
- `sonar-project.properties` - add file extensions and rules
- `.github/workflows/ci.yml` - add CI/CD pipeline

### 4. Update Documentation
- Add language to main README.md
- Create language-specific guide in `docs/languages/`
- Update project setup script

### 5. Example: Adding Go Support

**Template structure:**
```
templates/go/
├── main.go
├── go.mod
├── go.sum
├── Makefile
└── README.md
```

**VS Code settings addition:**
```jsonc
"[go]": {
    "editor.defaultFormatter": "golang.go",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

**Pre-commit hook addition:**
```yaml
- repo: https://github.com/dnephin/pre-commit-golang
  rev: v0.5.1
  hooks:
    - id: go-fmt
    - id: go-vet-mod
    - id: go-mod-tidy
```

## Improving AI Integration

### Adding AI Tool Support

1. **Research the tool's capabilities**
   - API integration options
   - VS Code extension availability
   - Configuration requirements

2. **Create configuration templates**
   - Add settings to `.vscode/settings.json`
   - Create tool-specific instruction files
   - Add to recommended extensions

3. **Document usage patterns**
   - Add to `.github/copilot-instructions.md`
   - Create examples and best practices
   - Include troubleshooting guides

### AI Prompt Templates

When contributing AI prompt templates:
- Make them language-agnostic where possible
- Include expected output examples
- Test with multiple AI tools
- Document limitations and edge cases

## Testing Guidelines

### New Features
- Include unit tests for all new functionality
- Add integration tests for complex features
- Test on multiple platforms (Windows, Linux, macOS)
- Verify compatibility with different language versions

### Template Testing
When adding new project templates:
1. Test project generation
2. Verify all quality checks pass
3. Test build and run processes
4. Validate CI/CD pipeline integration
5. Check VS Code integration

### Manual Testing Checklist
- [ ] Project creation works
- [ ] VS Code workspace loads correctly
- [ ] Extensions install properly
- [ ] Linting and formatting work
- [ ] Build process completes
- [ ] Tests run successfully
- [ ] CI/CD pipeline passes

## Documentation Standards

### Code Documentation
- All public APIs must be documented
- Include usage examples
- Document parameters, return values, and exceptions
- Explain complex algorithms or business logic

### README Updates
- Keep the main README current with new features
- Update language support table
- Add new configuration examples
- Include troubleshooting information

### Changelog Maintenance
Update `CHANGELOG.md` with:
- New features
- Bug fixes
- Breaking changes
- Deprecations
- Security updates

## Issue Reporting

### Bug Reports
Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, language versions, etc.)
- Error messages and stack traces
- AI tool information (if relevant)

### Feature Requests
Use the feature request template and include:
- Clear description of the desired feature
- Use case and benefits
- Implementation ideas (if any)
- Language/technology affected
- AI development context (if relevant)

## Security

### Security Vulnerabilities
Please do not report security vulnerabilities through GitHub issues. Instead:
1. Email security@yourproject.com
2. Include detailed description
3. Provide proof of concept (if safe)
4. Allow time for fix before disclosure

### Security Best Practices
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all inputs thoroughly
- Follow OWASP guidelines
- Regular dependency updates

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. Please read and follow it in all interactions.

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, nationality
- Personal appearance, race, religion
- Sexual identity and orientation

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@yourproject.com.

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- Project documentation
- Special contributor badge (for significant contributions)

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community Discord server
- **Email**: Contact maintainers directly if needed

Thank you for contributing to AI Development Workspace! 🚀