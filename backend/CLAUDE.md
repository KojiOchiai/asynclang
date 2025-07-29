# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the backend for AsyncLang, a Python project using FastAPI, SQLAlchemy, and Uvicorn. The project uses `uv` as the package manager and follows Clean Architecture principles with Domain-Driven Design.

## Development Commands

Use uv command instead of editing pyproject.toml directly.
The project uses `uv` for dependency management and development tasks:

- **Install dependencies**: `uv sync`
- **Run linting**: `uv run ruff check`
- **Format code**: `uv run ruff format`
- **Run tests**: `uv run pytest`
- **Run single test**: `uv run pytest path/to/test_file.py::test_function_name`
- **Start development server**: `uv run uvicorn main:app --reload` (when main.py exists)

## Configuration

- **Python version**: >=3.10 (as specified in pyproject.toml)
- **Linting**: Ruff is configured with E, F, I, W rule sets and 88-character line length
- **Testing**: pytest is used for testing
- **Dependencies**: FastAPI for web framework, SQLAlchemy for ORM, Uvicorn for ASGI server

## Important Notes

- The project structure is set up but currently contains empty directories (no Python files have been implemented yet)
- All source code should go in the `src/` directory following the established layer structure
- Ruff allows unused imports in `__init__.py` files as per configuration