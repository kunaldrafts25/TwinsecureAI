# Contributing to TwinSecure

Thank you for your interest in contributing to TwinSecure! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Follow the existing code style and patterns
- Write clear, descriptive commit messages
- Test your changes before submitting

## Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/kunaldrafts25/TwinsecureAI.git
   cd TwinsecureAI
   ```

2. **Set Up Environment**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install --legacy-peer-deps
   ```

3. **Configure Environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

### Backend Development

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Check coverage: `pytest --cov=app`
5. Lint code: `pylint app/`
6. Commit: `git commit -m "feat: add your feature"`
7. Push: `git push origin feature/your-feature`
8. Create a Pull Request

### Frontend Development

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `npm test`
4. Lint code: `npm run lint`
5. Build: `npm run build`
6. Commit with clear messages
7. Push and create a Pull Request

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints for functions
- Write docstrings for classes and public methods
- Use logging instead of print statements
- Keep functions focused and concise

Example:
```python
async def create_alert(
    db: AsyncSession,
    alert_data: AlertCreate
) -> Alert:
    """
    Create a new security alert.
    
    Args:
        db: Database session
        alert_data: Alert creation schema
        
    Returns:
        Created Alert instance
        
    Raises:
        ValueError: If alert data is invalid
    """
    # Implementation...
```

### TypeScript/React

- Follow ESLint configuration
- Use functional components with hooks
- Write prop interfaces for components
- Use meaningful variable names
- Keep components small and focused
- Add comments for complex logic

Example:
```typescript
interface AlertProps {
  id: string;
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  onDismiss: () => void;
}

const Alert: React.FC<AlertProps> = ({ 
  id, 
  severity, 
  message, 
  onDismiss 
}) => {
  // Implementation...
};
```

## Testing

- Write tests for new features
- Maintain test coverage above 80%
- Use descriptive test names
- Mock external dependencies
- Test both success and error cases

### Backend Tests
```bash
cd backend
pytest tests/                    # Run all tests
pytest tests/test_alerts.py      # Run specific test file
pytest -v                        # Verbose output
pytest --cov=app                 # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test                         # Run all tests
npm test -- src/component.test   # Run specific test
npm run test:coverage            # With coverage
```

## Commit Message Guidelines

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without feature changes
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling changes

Examples:
```
feat(honeypot): add attack detection for port scans
fix(alerts): resolve timing issue in alert deduplication
docs: update README installation instructions
refactor(auth): simplify token validation logic
```

## Pull Request Process

1. **Before submitting:**
   - Test locally
   - Update documentation if needed
   - Run linting and tests
   - Rebase on main branch if needed

2. **PR Description:**
   - Describe what changes were made
   - Explain why these changes are needed
   - Reference related issues
   - Include any breaking changes

3. **Review Process:**
   - Code will be reviewed for quality and security
   - Address feedback promptly
   - Discussions are welcome

4. **Merging:**
   - Squash commits into logical units
   - Use conventional commit messages
   - Delete feature branch after merge

## Security

- **Never commit secrets** (API keys, passwords, credentials)
- Always use environment variables for sensitive data
- Follow OWASP guidelines for security features
- Report security issues privately (see SECURITY.md)

## License

By contributing to TwinSecure, you agree that your contributions will be licensed under the same proprietary license as TwinSecure.

For questions or more information:
kunalsingh2514@gmail.com
