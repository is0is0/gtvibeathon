# Contributing to 3DAgency

Thank you for your interest in contributing to 3DAgency! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/3dagency.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate`
5. Install dev dependencies: `pip install -e ".[dev]"`
6. Create a branch: `git checkout -b feature/your-feature-name`

## Development Workflow

### Before Committing

1. **Format your code**
   ```bash
   black src/ tests/
   ```

2. **Lint your code**
   ```bash
   ruff check src/ tests/
   ```

3. **Type check**
   ```bash
   mypy src/
   ```

4. **Run tests**
   ```bash
   pytest
   ```

### Code Style

- Follow PEP 8 guidelines (enforced by Black)
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and modular
- Use descriptive variable names

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Mock external dependencies (Blender, AI APIs)

Example test structure:
```python
def test_agent_response():
    """Test that agent generates valid response."""
    agent = ConceptAgent(config)
    response = agent.generate_response("test prompt")
    assert response.agent_role == AgentRole.CONCEPT
    assert response.content
```

### Documentation

- Update README.md if adding new features
- Update CLAUDE.md for architectural changes
- Add docstrings to all new functions/classes
- Include usage examples in docstrings

## Pull Request Process

1. **Update documentation** - Ensure all docs are current
2. **Write tests** - New code should have tests
3. **Pass CI checks** - All tests and lints must pass
4. **Describe changes** - Write clear PR description
5. **Link issues** - Reference any related issues

### PR Title Format

Use conventional commits format:
- `feat: Add animation support`
- `fix: Resolve texture loading bug`
- `docs: Update installation guide`
- `refactor: Simplify agent base class`
- `test: Add integration tests for orchestrator`

## Adding New Agents

To add a new agent type:

1. Create `src/agency3d/agents/your_agent.py`
2. Inherit from `Agent` base class
3. Implement required methods:
   ```python
   from agency3d.core.agent import Agent, AgentConfig
   from agency3d.core.models import AgentRole, AgentResponse

   class YourAgent(Agent):
       def __init__(self, config: AgentConfig):
           super().__init__(AgentRole.YOUR_ROLE, config)

       def get_system_prompt(self) -> str:
           return """Your agent's system prompt..."""

       def _parse_response(self, response_text: str, context: dict) -> AgentResponse:
           # Parse AI response
           return AgentResponse(...)
   ```
4. Add to `agents/__init__.py`
5. Integrate into workflow in `orchestrator/workflow.py`
6. Write tests
7. Update documentation

## Adding New CLI Commands

1. Add command to `src/agency3d/cli.py`:
   ```python
   @app.command()
   def your_command(
       arg: str = typer.Argument(..., help="Description"),
       option: bool = typer.Option(False, "--flag", help="Description")
   ) -> None:
       """Command description."""
       # Implementation
   ```
2. Add tests for the command
3. Update README.md with usage examples

## Reporting Bugs

Create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Blender version)
- Relevant logs or error messages

## Feature Requests

Create an issue with:
- Clear description of the feature
- Use cases and benefits
- Proposed implementation (if any)
- Examples of similar features elsewhere

## Code Review Guidelines

When reviewing PRs:
- Check code quality and style
- Verify tests are present and passing
- Test functionality locally if possible
- Provide constructive feedback
- Approve when all concerns are addressed

## Community

- Be respectful and constructive
- Help others learn and grow
- Share knowledge and best practices
- Celebrate successes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
