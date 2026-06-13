# Contributing to L-System Renderer

Thank you for your interest in contributing! This guide will help you get started.

## Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/lsystem-renderer-q4m7.git`
3. Create a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
4. Install dev dependencies: `pip install -e ".[dev]"`
5. Create a feature branch: `git checkout -b feature/my-feature`
6. Make your changes
7. Run tests: `pytest`
8. Commit and push
9. Open a Pull Request

## Development Setup

```bash
# Install with all dev dependencies
pip install -e ".[dev]"

# Or install with just what you need
pip install -e .           # Core only
pip install -e ".[png]"    # + PNG support
pip install -e ".[yaml]"  # + YAML config support
pip install -e ".[all]"    # Everything
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lsystem_renderer --cov-report=html

# Run specific test file
pytest tests/test_engine.py -v

# Run specific test
pytest tests/test_engine.py::TestLSystemEngine::test_koch_curve -v
```

## Code Style

- Follow PEP 8 conventions
- Use type hints for all function signatures
- Add docstrings to all public classes and methods
- Keep functions focused and small
- Use descriptive variable names

## Adding New Presets

To add a new preset, add an entry to `lsystem_renderer/core/presets.py`:

```python
"my_preset": LSystemDefinition(
    name="My Preset",
    axiom="F",
    rules=[LSystemRule("F", "F+F-F+F")],
    angle=90.0,
    step_size=5.0,
    iterations=4,
),
```

Then add corresponding tests in `tests/test_presets.py`.

## Adding New Renderers

1. Create a new file in `lsystem_renderer/renderers/`
2. Implement a class with a `render(segments, output_path, **kwargs) -> str` method
3. Add the backend to the `RenderBackend` enum in `core/types.py`
4. Update `LSystemRenderer.render()` to handle the new backend
5. Add tests

## Adding New Features

- Start with a GitHub Issue describing the feature
- Discuss the approach before implementing
- Write tests first (TDD encouraged)
- Update documentation and README

## Bug Reports

When filing a bug report, please include:

1. Python version (`python3 --version`)
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Error output (if any)

## Pull Request Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation for user-facing changes
- Ensure all tests pass before submitting
- Write clear commit messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.