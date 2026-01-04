# Contributing Guide

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or 3.12
- Poetry (package manager)
- Git
- Basic understanding of Clean Architecture principles

### Setup

1. **Fork the repository** and clone your fork:
   ```bash
   git clone https://github.com/your-username/test-app.git
   cd test-app
   ```

2. **Install dependencies**:
   ```bash
   poetry install --with dev
   ```

3. **Install pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```

4. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Workflow

### Code Style

This project uses automated code formatting and linting. **Always run these before committing:**

```bash
# Format code
make format

# Or manually:
poetry run black app tests
poetry run isort app tests
poetry run ruff format app tests

# Check linting
make lint

# Or manually:
poetry run ruff check app tests
```

### Pre-commit Hooks

Pre-commit hooks automatically run on `git commit`. They check:
- Code formatting (Black, isort, Ruff)
- Linting (Ruff)
- Type checking (MyPy)
- Security issues (Bandit)
- File integrity (YAML, JSON, TOML)

**If hooks fail**, fix the issues and commit again. You can skip hooks with `--no-verify` (not recommended).

### Writing Code

1. **Follow Clean Architecture**:
   - Domain layer: Pure business logic, no framework dependencies
   - Infrastructure layer: External concerns (DB, APIs, etc.)
   - Presentation layer: FastAPI-specific code

2. **Write Type Hints**:
   ```python
   async def get_user(user_id: int) -> Optional[User]:
       ...
   ```

3. **Add Docstrings**:
   ```python
   def create_user(email: str, password: str) -> User:
       """
       Create a new user.

       Args:
           email: User email address
           password: Plain text password (will be hashed)

       Returns:
           Created User entity

       Raises:
           ValidationError: If email is invalid
           ConflictError: If user already exists
       """
   ```

4. **Write Tests**:
   - Add tests for new features
   - Maintain or improve test coverage
   - Tests should be fast and isolated

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
poetry run pytest tests/test_auth.py -v
```

**Test Requirements:**
- All tests must pass
- Maintain at least 70% code coverage
- Write tests for new features
- Update tests when modifying features

## 🔍 Code Quality Checks

Before submitting a PR, ensure all checks pass:

```bash
# Run all checks
make pre-commit

# Individual checks
make format-check  # Check formatting
make lint          # Run linters
make type-check    # Type checking
make security-check # Security scan
make test          # Run tests
```

## 📤 Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Ensure all checks pass**:
   ```bash
   make pre-commit
   make test
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add user registration feature"
   ```

   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Maintenance tasks

4. **Push to your fork**:
   ```bash
   git push origin your-branch
   ```

5. **Create Pull Request**:
   - Use the PR template
   - Provide clear description
   - Link related issues
   - Ensure CI checks pass

### PR Requirements

- ✅ All tests pass
- ✅ Code is formatted (Black, isort, Ruff)
- ✅ No linting errors
- ✅ Type checking passes (or documented exceptions)
- ✅ Security scan passes
- ✅ Documentation updated (if needed)
- ✅ PR description is clear and complete

## 🐛 Reporting Issues

When reporting bugs or requesting features:

1. **Check existing issues** to avoid duplicates
2. **Use clear, descriptive titles**
3. **Provide steps to reproduce** (for bugs)
4. **Include environment details** (Python version, OS, etc.)
5. **Add screenshots/logs** if applicable

## 💡 Feature Requests

For new features:

1. **Open an issue** first to discuss
2. **Describe the use case** and benefits
3. **Propose implementation** approach
4. **Wait for approval** before implementing

## 📚 Code Review Guidelines

### For Contributors

- Be open to feedback
- Address review comments promptly
- Keep PRs focused and small
- Respond to all review comments

### For Reviewers

- Be constructive and respectful
- Focus on code quality and architecture
- Approve when requirements are met
- Request changes with clear explanations

## 🎯 Project Standards

### Architecture

- **Clean Architecture**: Follow layer separation
- **Domain-Driven Design**: Entities, use cases, repositories
- **Dependency Inversion**: Interfaces in domain, implementations in infrastructure

### Code Quality

- **Type Hints**: Required for all functions
- **Docstrings**: Required for public APIs
- **Error Handling**: Use custom domain exceptions
- **Testing**: Write tests for business logic

### Git Workflow

- **Branch naming**: `feature/`, `fix/`, `docs/`, `refactor/`
- **Commit messages**: Use conventional commits
- **PR titles**: Clear and descriptive
- **Rebase before merge**: Keep history clean

## ❓ Questions?

- Open an issue for questions
- Check existing documentation
- Review code examples in the codebase

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉

