# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Alembic database migration system
- CORS middleware configuration
- Enhanced health check endpoint with database connectivity check
- `.editorconfig` for consistent code formatting across editors
- `CHANGELOG.md` for version tracking
- Environment management commands in Makefile (`make env-*`)

### Changed
- Replaced deprecated `@app.on_event("startup")` with lifespan context manager
- Updated Pydantic Settings to use `model_config` (Pydantic v2)
- Added default values for `database_url` and `secret_key` in Settings (development only)
- Enhanced logout use case with proper documentation
- Removed `poetry.lock` from `.gitignore` (should be committed for reproducible builds)

### Fixed
- Startup error when `.env` file is missing (now uses sensible defaults)
- Deprecated FastAPI event handler warnings

## [1.0.0] - 2024-12-31

### Added
- Initial FastAPI Clean Architecture boilerplate
- User authentication (register, login, logout, refresh token)
- JWT authentication with access and refresh tokens
- Password hashing with Argon2
- Clean Architecture with Domain-Driven Design
- Repository pattern with adapters
- Global exception handling with structured error responses
- Trace ID middleware for request tracking
- Rate limiting (global and per-endpoint)
- Pre-commit hooks for code quality
- GitHub Actions CI/CD workflows
- Docker and Docker Compose setup
- Comprehensive test suite with pytest
- Code quality tools (Black, isort, Ruff, MyPy, Bandit)
- Makefile with common development commands
- Comprehensive documentation (README, CONTRIBUTING)

[Unreleased]: https://github.com/keniiy/test-app/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/keniiy/test-app/releases/tag/v1.0.0

