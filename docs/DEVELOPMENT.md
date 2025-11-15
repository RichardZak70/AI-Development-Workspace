# Development Guide

> Comprehensive guide for developing with the AI Development Workspace template

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Language-Specific Guides](#language-specific-guides)
- [Quality Standards](#quality-standards)
- [AI Integration](#ai-integration)
- [Testing Strategy](#testing-strategy)
- [Debugging Guide](#debugging-guide)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

Ensure you have the following tools installed:

#### Required
- **VS Code** 1.80+ with recommended extensions
- **Git** 2.30+ for version control
- **Python** 3.11+ for project scripts and Python development
- **Node.js** 18+ for JavaScript tools and pre-commit hooks

#### Language-Specific
- **Java** 11+ (OpenJDK or Oracle JDK) for Java projects
- **GCC/Clang** latest stable for C/C++ projects
- **.NET** 6+ SDK for C# projects

#### Optional but Recommended
- **Docker** for containerized development
- **GitHub CLI** for repository management
- **SonarQube** server or SonarCloud account

### Initial Setup

```bash
# Clone the template
git clone https://github.com/yourusername/ai-development-workspace.git
cd ai-development-workspace

# Set up Python environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
python scripts/setup_project.py --check
```

## Development Workflow

### 1. Project Creation

```bash
# List available templates
python scripts/setup_project.py --list-templates

# Create new project
python scripts/setup_project.py my-project python
cd my-project
code .
```

### 2. Daily Development

```bash
# Start development session
.venv\Scripts\Activate.ps1  # Activate Python environment
code .                      # Open VS Code

# Before committing
pre-commit run --all-files  # Run quality checks
git add .
git commit -m "feat: add new feature"
git push
```

### 3. Quality Assurance

```bash
# Python quality checks
ruff check .                # Linting
ruff format .              # Formatting
mypy .                     # Type checking
bandit -r .               # Security analysis
pytest --cov             # Testing with coverage

# C/C++ quality checks
make analyze               # Static analysis
make test                  # Run tests
cppcheck .                # Security analysis

# Java quality checks
mvn checkstyle:check       # Style checking
mvn spotbugs:check        # Bug analysis
mvn test                  # Run tests

# C# quality checks
dotnet format --verify-no-changes  # Formatting
dotnet test                        # Run tests
```

### 4. AI-Assisted Development

```bash
# Generate code with quality enforcement
# 1. Use GitHub Copilot for suggestions
# 2. Review generated code thoroughly
# 3. Run quality checks immediately
ruff check generated_file.py
mypy generated_file.py
pytest tests/test_generated.py
```

## Language-Specific Guides

### Python Development

#### Project Structure
```
my-python-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

#### Best Practices
```python
# Type hints are mandatory
from typing import List, Optional, Dict, Any
from pathlib import Path

def process_data(
    input_file: Path,
    output_file: Optional[Path] = None,
    config: Dict[str, Any] = None
) -> List[str]:
    """Process data with comprehensive error handling.
    
    Args:
        input_file: Path to input data file
        output_file: Optional output file path
        config: Configuration dictionary
        
    Returns:
        List of processed data items
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValidationError: If data format is invalid
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    config = config or {}
    
    # Implementation with proper error handling
    try:
        with input_file.open() as f:
            data = f.read()
        # Process data...
        return processed_items
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise ProcessingError(f"Failed to process {input_file}") from e
```

#### Testing
```python
# tests/test_main.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.my_project.main import process_data

class TestProcessData:
    """Test cases for process_data function."""
    
    def test_process_data_success(self, tmp_path: Path):
        """Test successful data processing."""
        # Arrange
        input_file = tmp_path / "input.txt"
        input_file.write_text("test data")
        
        # Act
        result = process_data(input_file)
        
        # Assert
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_process_data_file_not_found(self):
        """Test handling of missing input file."""
        with pytest.raises(FileNotFoundError):
            process_data(Path("nonexistent.txt"))
    
    @patch('src.my_project.main.logger')
    def test_process_data_error_logging(self, mock_logger, tmp_path: Path):
        """Test error logging."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("invalid data")
        
        with pytest.raises(ProcessingError):
            process_data(input_file)
        
        mock_logger.error.assert_called_once()
```

### C/C++ Development

#### Project Structure
```
my-cpp-project/
├── src/
│   ├── main.cpp
│   └── lib/
│       ├── mylib.h
│       └── mylib.cpp
├── tests/
│   └── test_mylib.cpp
├── include/
├── Makefile
├── CMakeLists.txt
└── README.md
```

#### Best Practices
```cpp
// mylib.h - Header with comprehensive documentation
#pragma once

#include <memory>
#include <string>
#include <vector>
#include <optional>

namespace myproject {

/**
 * @brief Data processor with RAII and error handling
 * 
 * This class provides safe data processing with automatic
 * resource management and comprehensive error handling.
 */
class DataProcessor {
public:
    /**
     * @brief Construct processor with validation
     * @param config Configuration string
     * @throws std::invalid_argument if config is invalid
     */
    explicit DataProcessor(const std::string& config);
    
    /**
     * @brief Process data with error handling
     * @param input Input data vector
     * @return Processed data or nullopt on failure
     */
    std::optional<std::vector<int>> process(
        const std::vector<int>& input
    ) const noexcept;
    
    // Rule of 5
    ~DataProcessor() = default;
    DataProcessor(const DataProcessor&) = delete;
    DataProcessor& operator=(const DataProcessor&) = delete;
    DataProcessor(DataProcessor&&) = default;
    DataProcessor& operator=(DataProcessor&&) = default;

private:
    class Impl;  // PIMPL idiom
    std::unique_ptr<Impl> pimpl_;
};

}  // namespace myproject
```

```cpp
// mylib.cpp - Implementation with error handling
#include "mylib.h"
#include <algorithm>
#include <stdexcept>
#include <syslog.h>

namespace myproject {

class DataProcessor::Impl {
public:
    explicit Impl(const std::string& config) {
        if (config.empty()) {
            throw std::invalid_argument("Configuration cannot be empty");
        }
        // Initialize with config...
        syslog(LOG_INFO, "DataProcessor initialized with config: %s", 
               config.c_str());
    }
    
    std::optional<std::vector<int>> process(
        const std::vector<int>& input
    ) const noexcept {
        try {
            if (input.empty()) {
                syslog(LOG_WARNING, "Empty input provided to process()");
                return std::nullopt;
            }
            
            std::vector<int> result;
            result.reserve(input.size());
            
            std::transform(input.begin(), input.end(), 
                          std::back_inserter(result),
                          [](int x) { return x * 2; });
            
            return result;
        } catch (const std::exception& e) {
            syslog(LOG_ERR, "Processing failed: %s", e.what());
            return std::nullopt;
        }
    }
};

DataProcessor::DataProcessor(const std::string& config)
    : pimpl_(std::make_unique<Impl>(config)) {}

std::optional<std::vector<int>> DataProcessor::process(
    const std::vector<int>& input
) const noexcept {
    return pimpl_->process(input);
}

}  // namespace myproject
```

### Java Development

#### Project Structure
```
my-java-project/
├── src/
│   └── main/java/com/example/
│       └── MyApplication.java
├── src/test/java/com/example/
│   └── MyApplicationTest.java
├── pom.xml
└── README.md
```

#### Best Practices
```java
// MyApplication.java
package com.example;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Data processing application with modern Java features.
 * 
 * @author Your Name
 * @version 1.0
 * @since 1.0
 */
public class MyApplication {
    private static final Logger LOGGER = 
        Logger.getLogger(MyApplication.class.getName());
    
    private final DataProcessor processor;
    
    /**
     * Constructs application with dependency injection.
     * 
     * @param processor the data processor to use
     * @throws IllegalArgumentException if processor is null
     */
    public MyApplication(DataProcessor processor) {
        this.processor = Objects.requireNonNull(processor, 
            "Processor cannot be null");
    }
    
    /**
     * Processes data asynchronously with error handling.
     * 
     * @param data the input data list
     * @return CompletableFuture with processed data or empty Optional
     */
    public CompletableFuture<Optional<List<Integer>>> processDataAsync(
            List<Integer> data) {
        if (data == null || data.isEmpty()) {
            LOGGER.warning("Empty or null data provided");
            return CompletableFuture.completedFuture(Optional.empty());
        }
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                var result = processor.process(data);
                LOGGER.info("Processed " + data.size() + " items");
                return Optional.of(result);
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, "Processing failed", e);
                return Optional.empty();
            }
        });
    }
    
    /**
     * Entry point with proper exception handling.
     */
    public static void main(String[] args) {
        try {
            var processor = new DataProcessorImpl();
            var app = new MyApplication(processor);
            
            var data = List.of(1, 2, 3, 4, 5);
            var future = app.processDataAsync(data);
            
            future.thenAccept(result -> {
                if (result.isPresent()) {
                    System.out.println("Result: " + result.get());
                } else {
                    System.err.println("Processing failed");
                }
            }).join();
            
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Application failed", e);
            System.exit(1);
        }
    }
}
```

### C# Development

#### Project Structure
```
my-csharp-project/
├── src/
│   └── MyApp/
│       ├── Program.cs
│       └── MyApp.csproj
├── tests/
│   └── MyApp.Tests/
│       ├── ProgramTests.cs
│       └── MyApp.Tests.csproj
├── MyApp.sln
└── README.md
```

#### Best Practices
```csharp
// Program.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace MyApp;

/// <summary>
/// Data processing application with async/await and DI.
/// </summary>
public class Program
{
    private readonly ILogger<Program> _logger;
    private readonly IDataProcessor _processor;
    
    /// <summary>
    /// Initializes a new instance of the Program class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    /// <param name="processor">The data processor.</param>
    public Program(ILogger<Program> logger, IDataProcessor processor)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _processor = processor ?? throw new ArgumentNullException(nameof(processor));
    }
    
    /// <summary>
    /// Processes data asynchronously with proper error handling.
    /// </summary>
    /// <param name="data">The input data.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Processed data or null if processing fails.</returns>
    public async Task<List<int>?> ProcessDataAsync(
        IReadOnlyList<int> data, 
        CancellationToken cancellationToken = default)
    {
        if (data is null || data.Count == 0)
        {
            _logger.LogWarning("Empty or null data provided");
            return null;
        }
        
        try
        {
            var result = await _processor.ProcessAsync(data, cancellationToken);
            _logger.LogInformation("Processed {Count} items successfully", data.Count);
            return result;
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Processing was cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process data");
            return null;
        }
    }
    
    /// <summary>
    /// Application entry point with proper DI setup.
    /// </summary>
    public static async Task<int> Main(string[] args)
    {
        try
        {
            using var host = CreateHostBuilder(args).Build();
            
            var program = host.Services.GetRequiredService<Program>();
            var data = new List<int> { 1, 2, 3, 4, 5 };
            
            var result = await program.ProcessDataAsync(data);
            
            if (result is not null)
            {
                Console.WriteLine($"Result: [{string.Join(", ", result)}]");
                return 0;
            }
            else
            {
                Console.Error.WriteLine("Processing failed");
                return 1;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Application failed: {ex.Message}");
            return 1;
        }
    }
    
    /// <summary>
    /// Configures the application host with dependency injection.
    /// </summary>
    private static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureServices((context, services) =>
            {
                services.AddSingleton<IDataProcessor, DataProcessor>();
                services.AddSingleton<Program>();
            });
}
```

## Quality Standards

### Code Quality Metrics

| Metric | Target | Tool | Language |
|--------|--------|------|---------|
| Cognitive Complexity | ≤15 | SonarQube | All |
| Test Coverage | ≥80% | Coverage tools | All |
| Duplication | <3% | SonarQube | All |
| Security Issues | 0 critical/high | Security scanners | All |
| Type Coverage | 100% | Type checkers | Python, TypeScript |

### Quality Gates

All code must pass:
1. **Linting**: No errors, minimal warnings
2. **Formatting**: Consistent style across codebase
3. **Type Checking**: Full type safety (where applicable)
4. **Security Scanning**: No high/critical vulnerabilities
5. **Testing**: Minimum coverage thresholds
6. **Documentation**: All public APIs documented

## AI Integration

### GitHub Copilot Best Practices

#### Effective Prompting
```python
# Good: Clear, specific comments that guide AI
def calculate_fibonacci_memoized(n: int) -> int:
    """Calculate nth Fibonacci number using memoization.
    
    Uses dynamic programming to optimize recursive calls.
    Time complexity: O(n), Space complexity: O(n)
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    # TODO: Implement memoized Fibonacci calculation
    # 1. Validate input (n >= 0)
    # 2. Handle base cases (n=0, n=1)
    # 3. Use cache to store calculated values
    # 4. Return cached result or calculate recursively
```

#### Code Review Checklist for AI-Generated Code
- [ ] **Functionality**: Does it solve the intended problem?
- [ ] **Security**: Are there injection vulnerabilities?
- [ ] **Performance**: Is it efficiently implemented?
- [ ] **Error Handling**: Are edge cases covered?
- [ ] **Type Safety**: Are types correctly specified?
- [ ] **Testing**: Can it be easily tested?
- [ ] **Documentation**: Is it properly documented?
- [ ] **Style**: Does it follow project conventions?

### AI Tool Configuration

#### VS Code Settings
```jsonc
// .vscode/settings.json
{
  "github.copilot.enable": {
    "*": true,
    "markdown": true
  },
  "github.copilot.advanced": {
    "debug.overrideEngine": "claude-3",
    "debug.testPilotModel": true
  },
  "github.copilot.chat.localeOverride": "en",
  "editor.inlineSuggest.enabled": true,
  "editor.suggest.preview": true
}
```

## Testing Strategy

### Test Pyramid

```
        /\     UI Tests (5%)
       /  \    - End-to-end testing
      /____\   - User acceptance testing
     /      \  Integration Tests (25%)
    /        \ - API testing
   /          \- Database integration
  /____________\
  Unit Tests (70%)
  - Function testing
  - Class testing
  - Mock testing
```

### Testing Frameworks by Language

| Language | Framework | Coverage | Mocking |
|----------|-----------|----------|----------|
| Python | pytest | pytest-cov | unittest.mock |
| C/C++ | Google Test | gcov/llvm-cov | Google Mock |
| Java | JUnit 5 | JaCoCo | Mockito |
| C# | xUnit | coverlet | Moq |

### Example Test Structure

```python
# tests/test_example.py
import pytest
from unittest.mock import Mock, patch
from src.example import DataProcessor, ProcessingError

class TestDataProcessor:
    """Test suite for DataProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance for testing."""
        return DataProcessor(config={"timeout": 30})
    
    @pytest.mark.parametrize("input_data,expected", [
        ([1, 2, 3], [2, 4, 6]),
        ([], []),
        ([0], [0]),
    ])
    def test_process_success(self, processor, input_data, expected):
        """Test successful data processing with various inputs."""
        result = processor.process(input_data)
        assert result == expected
    
    def test_process_with_invalid_input(self, processor):
        """Test error handling for invalid input."""
        with pytest.raises(ProcessingError, match="Invalid input"):
            processor.process(None)
    
    @patch('src.example.external_api')
    def test_process_with_external_dependency(self, mock_api, processor):
        """Test processing with mocked external dependency."""
        # Arrange
        mock_api.fetch_data.return_value = {"factor": 2}
        
        # Act
        result = processor.process([1, 2, 3])
        
        # Assert
        assert result == [2, 4, 6]
        mock_api.fetch_data.assert_called_once()
    
    def test_process_performance(self, processor, benchmark):
        """Test processing performance with large datasets."""
        large_data = list(range(10000))
        
        # Use pytest-benchmark for performance testing
        result = benchmark(processor.process, large_data)
        
        assert len(result) == len(large_data)
```

## Performance Optimization

### Language-Specific Optimization

#### Python
```python
# Use appropriate data structures
from collections import defaultdict, deque
from functools import lru_cache
import bisect

# Efficient algorithms
@lru_cache(maxsize=1000)
def expensive_calculation(n: int) -> int:
    """Cache expensive calculations."""
    return sum(i * i for i in range(n))

# Use generators for memory efficiency
def process_large_file(filename: str):
    """Process large files without loading into memory."""
    with open(filename) as f:
        for line in f:
            yield process_line(line)
```

#### C++
```cpp
// Use move semantics and RAII
class OptimizedContainer {
private:
    std::vector<std::unique_ptr<Data>> data_;
    
public:
    // Move constructor
    OptimizedContainer(OptimizedContainer&& other) noexcept
        : data_(std::move(other.data_)) {}
    
    // Reserve capacity to avoid reallocations
    void reserve(size_t capacity) {
        data_.reserve(capacity);
    }
    
    // Use emplace for in-place construction
    template<typename... Args>
    void emplace_data(Args&&... args) {
        data_.emplace_back(std::make_unique<Data>(std::forward<Args>(args)...));
    }
};
```

### Profiling and Benchmarking

```bash
# Python profiling
python -m cProfile -o profile.stats my_script.py
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"

# C++ profiling with valgrind
valgrind --tool=callgrind ./my_program
kcachegrind callgrind.out.*

# Java profiling
java -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s my.jar

# Memory usage monitoring
/usr/bin/time -v ./my_program
```

## Debugging Guide

### VS Code Debugging Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Debug Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "justMyCode": false
        },
        {
            "name": "C++: Debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/debug/main",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "C++: build debug",
            "miDebuggerPath": "/usr/bin/gdb"
        }
    ]
}
```

### Logging Best Practices

```python
# Python structured logging
import logging
import structlog
import json

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def process_data(data_id: str, data: list):
    """Process data with comprehensive logging."""
    logger.info(
        "Processing started",
        data_id=data_id,
        data_size=len(data),
        operation="process_data"
    )
    
    try:
        result = perform_processing(data)
        
        logger.info(
            "Processing completed successfully",
            data_id=data_id,
            result_size=len(result),
            operation="process_data"
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Processing failed",
            data_id=data_id,
            error=str(e),
            error_type=type(e).__name__,
            operation="process_data"
        )
        raise
```

## Troubleshooting

### Common Issues and Solutions

#### Python Environment Issues

**Problem**: Package installation fails
```bash
# Solution: Update pip and clear cache
python -m pip install --upgrade pip
pip cache purge
pip install -r requirements.txt
```

**Problem**: Import errors
```bash
# Solution: Check PYTHONPATH
echo $PYTHONPATH  # Linux/macOS
echo $env:PYTHONPATH  # Windows PowerShell

# Add current directory to path
export PYTHONPATH="${PWD}:${PYTHONPATH}"  # Linux/macOS
$env:PYTHONPATH="${PWD};${env:PYTHONPATH}"  # Windows
```

#### C/C++ Compilation Issues

**Problem**: Missing headers
```bash
# Solution: Install development packages
# Ubuntu/Debian
sudo apt-get install build-essential

# CentOS/RHEL
sudo yum groupinstall "Development Tools"

# macOS
xcode-select --install
```

**Problem**: Linking errors
```bash
# Solution: Check library paths
ldd ./my_program  # Linux
otool -L ./my_program  # macOS

# Add library path
export LD_LIBRARY_PATH="/path/to/libs:$LD_LIBRARY_PATH"
```

#### Java Build Issues

**Problem**: Maven/Gradle build fails
```bash
# Solution: Clear cache and retry
./mvnw clean install -U  # Maven
./gradlew clean build --refresh-dependencies  # Gradle
```

#### VS Code Issues

**Problem**: Extensions not working
```bash
# Solution: Reset VS Code settings
code --disable-extensions
code --reset-settings
```

**Problem**: IntelliSense not working
```bash
# Solution: Reload language server
# Ctrl+Shift+P -> "Reload Window"
# Or restart language servers for specific languages
```

### Performance Troubleshooting

#### Slow Build Times
```bash
# Enable parallel builds
make -j$(nproc)  # Use all CPU cores
./mvnw -T 1C clean install  # Maven parallel
./gradlew build --parallel  # Gradle parallel
```

#### Memory Issues
```bash
# Monitor memory usage
top -o %MEM
htop

# Java memory settings
export MAVEN_OPTS="-Xmx2g -XX:+UseG1GC"
export GRADLE_OPTS="-Xmx2g"
```

### Getting Help

1. **Check logs**: Look at build outputs and error messages
2. **Search issues**: Check GitHub issues for similar problems
3. **Community support**: Use discussions for questions
4. **Documentation**: Review language-specific guides
5. **Stack Overflow**: Search for language-specific solutions

---

**Remember**: Good development practices lead to fewer issues. Follow the quality standards and use the provided tools for the best experience.