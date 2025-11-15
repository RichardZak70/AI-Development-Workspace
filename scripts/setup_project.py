#!/usr/bin/env python3
"""Project setup script for AI Development Workspace.

This script helps initialize new projects from templates and
sets up the development environment.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


class ProjectSetup:
    """Handles project setup and initialization."""

    def __init__(self, workspace_root: Path):
        """Initialize project setup.

        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = workspace_root
        self.templates_dir = workspace_root / "templates"

    def list_templates(self) -> list[str]:
        """List available project templates.

        Returns:
            List of template names
        """
        if not self.templates_dir.exists():
            return []

        return [d.name for d in self.templates_dir.iterdir() if d.is_dir()]

    def create_project(self, project_name: str, template: str, target_dir: Path | None = None) -> bool:
        """Create a new project from template.

        Args:
            project_name: Name of the new project
            template: Template to use
            target_dir: Target directory (default: current directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate template
            template_path = self.templates_dir / template
            if not template_path.exists():
                print(f"Error: Template '{template}' not found")
                print(f"Available templates: {', '.join(self.list_templates())}")
                return False

            # Set target directory
            if target_dir is None:
                target_dir = Path.cwd() / project_name

            # Create project directory
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"Creating project '{project_name}' in {target_dir}")

            # Copy template files
            self._copy_template(template_path, target_dir)

            # Copy workspace configuration
            self._copy_workspace_config(target_dir)

            # Initialize project-specific files
            self._initialize_project(project_name, template, target_dir)

            # Setup development environment
            self._setup_environment(template, target_dir)

            print(f"✅ Project '{project_name}' created successfully!")
            print(f"📁 Location: {target_dir}")
            print("\nNext steps:")
            print(f"1. cd {target_dir}")
            print("2. code .  # Open in VS Code")

            if template == "python":
                print("3. Activate virtual environment: .venv\\Scripts\\Activate.ps1")
                print("4. Install dependencies: pip install -r requirements.txt")
            elif template == "c-cpp":
                print("3. Build project: make")
                print("4. Run tests: make test")

            return True

        except Exception as e:
            print(f"Error creating project: {e}")
            return False

    def _copy_template(self, template_path: Path, target_dir: Path) -> None:
        """Copy template files to target directory."""
        print(f"Copying template files from {template_path}...")

        for item in template_path.iterdir():
            if item.is_file():
                shutil.copy2(item, target_dir)
            elif item.is_dir():
                shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)

    def _copy_workspace_config(self, target_dir: Path) -> None:
        """Copy workspace configuration files."""
        print("Copying workspace configuration...")

        config_files = [
            ".vscode",
            "pyproject.toml",
            "sonar-project.properties",
            ".pre-commit-config.yaml",
            ".gitignore",
            "requirements.txt",
        ]

        for config_file in config_files:
            src_path = self.workspace_root / config_file
            if src_path.exists():
                if src_path.is_file():
                    shutil.copy2(src_path, target_dir)
                elif src_path.is_dir():
                    shutil.copytree(src_path, target_dir / config_file, dirs_exist_ok=True)

    def _initialize_project(self, project_name: str, template: str, target_dir: Path) -> None:
        """Initialize project-specific files."""
        print("Initializing project-specific files...")

        # Create basic directory structure
        directories = ["src", "tests", "docs", "data", "output"]

        if template == "python":
            directories.extend(["notebooks", "scripts"])
        elif template == "c-cpp":
            directories.extend(["include", "build", "bin"])
        elif template == "java":
            directories.extend(["src/main/java", "src/test/java", "target"])
        elif template == "csharp":
            directories.extend(["bin", "obj"])

        for directory in directories:
            (target_dir / directory).mkdir(parents=True, exist_ok=True)

        # Create basic .gitignore
        self._create_gitignore(template, target_dir)

        # Create README.md
        self._create_readme(project_name, template, target_dir)

    def _create_gitignore(self, template: str, target_dir: Path) -> None:
        """Create .gitignore file."""
        gitignore_content = [
            "# AI Development Workspace - Generated .gitignore",
            "",
            "# General",
            ".DS_Store",
            "Thumbs.db",
            "*.log",
            "*.tmp",
            ".env",
            ".env.local",
            "",
            "# IDE",
            ".idea/",
            "*.swp",
            "*.swo",
            "",
        ]

        if template == "python":
            gitignore_content.extend(
                [
                    "# Python",
                    "__pycache__/",
                    "*.py[cod]",
                    "*$py.class",
                    "*.so",
                    ".Python",
                    "build/",
                    "develop-eggs/",
                    "dist/",
                    "downloads/",
                    "eggs/",
                    ".eggs/",
                    "lib/",
                    "lib64/",
                    "parts/",
                    "sdist/",
                    "var/",
                    "wheels/",
                    "*.egg-info/",
                    ".installed.cfg",
                    "*.egg",
                    ".venv/",
                    "venv/",
                    "env/",
                    ".mypy_cache/",
                    ".pytest_cache/",
                    "htmlcov/",
                    ".coverage",
                    ".coverage.*",
                    "coverage.xml",
                    "",
                ]
            )
        elif template == "c-cpp":
            gitignore_content.extend(
                [
                    "# C/C++",
                    "*.o",
                    "*.a",
                    "*.so",
                    "*.exe",
                    "*.out",
                    "build/",
                    "bin/",
                    "*.d",
                    "",
                ]
            )
        elif template == "java":
            gitignore_content.extend(
                [
                    "# Java",
                    "*.class",
                    "*.jar",
                    "*.war",
                    "*.ear",
                    "target/",
                    ".gradle/",
                    "build/",
                    "",
                ]
            )
        elif template == "csharp":
            gitignore_content.extend(
                [
                    "# C#",
                    "bin/",
                    "obj/",
                    "*.dll",
                    "*.exe",
                    "*.pdb",
                    "*.user",
                    "*.cache",
                    "packages/",
                    "",
                ]
            )

        gitignore_path = target_dir / ".gitignore"
        gitignore_path.write_text("\n".join(gitignore_content))

    def _create_readme(self, project_name: str, template: str, target_dir: Path) -> None:
        """Create README.md file."""
        readme_content = f"""# {project_name}

AI-assisted {template.upper()} project created from AI Development Workspace template.

## Description

Add your project description here.

## Setup

### Prerequisites

- {self._get_prerequisites(template)}

### Installation

{self._get_installation_steps(template)}

## Usage

{self._get_usage_instructions(template)}

## Development

### Quality Checks

```bash
{self._get_quality_check_commands(template)}
```

### Testing

```bash
{self._get_test_commands(template)}
```

## Project Structure

```
{self._get_project_structure(template)}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
"""

        readme_path = target_dir / "README.md"
        readme_path.write_text(readme_content)

    def _get_prerequisites(self, template: str) -> str:
        """Get prerequisites for template."""
        prereq_map = {
            "python": "Python 3.11+",
            "c-cpp": "GCC/G++ compiler, Make",
            "java": "Java 11+, Maven/Gradle",
            "csharp": ".NET 6+",
        }
        return prereq_map.get(template, "See template documentation")

    def _get_installation_steps(self, template: str) -> str:
        """Get installation steps for template."""
        steps_map = {
            "python": "```bash\npython -m venv .venv\n.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\n```",
            "c-cpp": "```bash\nmake\n```",
            "java": "```bash\nmvn install\n# or\ngradle build\n```",
            "csharp": "```bash\ndotnet restore\ndotnet build\n```",
        }
        return steps_map.get(template, "See template documentation")

    def _get_usage_instructions(self, template: str) -> str:
        """Get usage instructions for template."""
        usage_map = {
            "python": "```bash\npython src/main.py\n```",
            "c-cpp": "```bash\n./bin/main\n```",
            "java": "```bash\njava -jar target/app.jar\n```",
            "csharp": "```bash\ndotnet run\n```",
        }
        return usage_map.get(template, "See template documentation")

    def _get_quality_check_commands(self, template: str) -> str:
        """Get quality check commands for template."""
        commands_map = {
            "python": "ruff check .\nmypy .\npytest",
            "c-cpp": "make analyze",
            "java": "mvn checkstyle:check\nmvn spotbugs:check",
            "csharp": "dotnet format --verify-no-changes\ndotnet test",
        }
        return commands_map.get(template, "# Add quality check commands")

    def _get_test_commands(self, template: str) -> str:
        """Get test commands for template."""
        test_map = {
            "python": "pytest tests/",
            "c-cpp": "make test",
            "java": "mvn test",
            "csharp": "dotnet test",
        }
        return test_map.get(template, "# Add test commands")

    def _get_project_structure(self, template: str) -> str:
        """Get project structure for template."""
        structure_map = {
            "python": """
├── src/
│   └── main.py
├── tests/
├── docs/
├── data/
├── output/
├── notebooks/
├── scripts/
├── requirements.txt
├── pyproject.toml
└── README.md""",
            "c-cpp": """
├── src/
├── include/
├── tests/
├── docs/
├── build/
├── bin/
├── Makefile
└── README.md""",
            "java": """
├── src/
│   ├── main/java/
│   └── test/java/
├── target/
├── docs/
├── pom.xml
└── README.md""",
            "csharp": """
├── src/
├── tests/
├── bin/
├── obj/
├── docs/
├── *.csproj
└── README.md""",
        }
        return structure_map.get(template, "# Add project structure")

    def _setup_environment(self, template: str, target_dir: Path) -> None:
        """Setup development environment for template."""
        print(f"Setting up {template} environment...")

        if template == "python":
            self._setup_python_env(target_dir)
        elif template == "c-cpp":
            self._setup_cpp_env(target_dir)
        # Add other language setups as needed

    def _setup_python_env(self, target_dir: Path) -> None:
        """Setup Python virtual environment."""
        venv_path = target_dir / ".venv"
        if not venv_path.exists():
            print("Creating Python virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], cwd=target_dir, check=True)

    def _setup_cpp_env(self, target_dir: Path) -> None:
        """Setup C++ development environment."""
        # Create compile_commands.json for better IDE support
        compile_commands = [
            {
                "directory": str(target_dir),
                "command": "gcc -Wall -Wextra -std=c11 -I./include -c src/main.c",
                "file": "src/main.c",
            }
        ]

        compile_commands_path = target_dir / "compile_commands.json"
        compile_commands_path.write_text(json.dumps(compile_commands, indent=2))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Development Workspace Project Setup")
    parser.add_argument("project_name", help="Name of the project to create")
    parser.add_argument("template", help="Template to use (python, c-cpp, java, csharp)")
    parser.add_argument("--target-dir", type=Path, help="Target directory (default: current directory)")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")

    args = parser.parse_args()

    # Get workspace root
    workspace_root = Path(__file__).parent.parent
    setup = ProjectSetup(workspace_root)

    if args.list_templates:
        templates = setup.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return 0

    # Create project
    success = setup.create_project(args.project_name, args.template, args.target_dir)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
