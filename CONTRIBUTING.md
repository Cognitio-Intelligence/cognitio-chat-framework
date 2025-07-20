# Contributing to Cognitio Chat Framework

Thank you for your interest in contributing to the Cognitio Chat Framework! This guide will help you get started with contributing to this open-source project.

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/your-username/django-react-webllm-application.git
cd django-react-webllm-application
```

2. **Set up the development environment:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. **Set up the project:**
```bash
python manage.py setup_webllm --create-env --mode dev
```

4. **Start development servers:**
```bash
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: React frontend (hot reload)
cd src/cognitio_app/backend/frontend-src
npm run dev
```

## 📋 Project Structure

```
django-react-webllm-application/
├── src/cognitio_app/
│   ├── backend/
│   │   ├── api/                    # Django REST API
│   │   │   ├── models/            # Database models
│   │   │   ├── views/             # API views
│   │   │   ├── serializers.py     # Data serializers
│   │   │   └── urls.py            # URL routing
│   │   ├── frontend-src/          # React TypeScript frontend
│   │   │   ├── src/
│   │   │   │   ├── components/    # React components
│   │   │   │   ├── services/      # API services
│   │   │   │   └── types/         # TypeScript types
│   │   │   ├── package.json
│   │   │   └── vite.config.ts
│   │   └── settings.py            # Django settings
├── requirements.txt               # Python dependencies
├── pyproject.toml                # Briefcase configuration
├── README.md
├── DEPLOYMENT.md
└── CONTRIBUTING.md
```

## 🛠️ Development Guidelines

### Code Style

#### Python (Backend)
- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Add docstrings to all functions and classes

```python
def create_chat_session(user_id: int, title: str) -> ChatSession:
    """
    Create a new chat session for the given user.
    
    Args:
        user_id: The ID of the user creating the session
        title: The title for the new session
        
    Returns:
        ChatSession: The newly created chat session
        
    Raises:
        ValueError: If user_id is invalid
    """
    # Implementation here
    pass
```

#### TypeScript/React (Frontend)
- Use [Prettier](https://prettier.io/) for code formatting
- Follow [Airbnb React Style Guide](https://github.com/airbnb/javascript/tree/master/react)
- Use TypeScript for all new code
- Use functional components with hooks

```typescript
interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  // Component implementation
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      {message.content}
    </div>
  );
};
```

### Testing

#### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test api.tests.test_chat_views

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

#### Frontend Tests
```bash
cd src/cognitio_app/backend/frontend-src
npm run test
npm run test:coverage
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Examples:
- `feat(chat): add message streaming support`
- `fix(api): resolve CORS issues with frontend`
- `docs: update deployment guide`
- `refactor(webllm): improve error handling`

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment information:**
   - Operating system
   - Python version
   - Node.js version
   - Browser version

2. **Steps to reproduce:**
   - Clear step-by-step instructions
   - Expected behavior
   - Actual behavior

3. **Additional context:**
   - Screenshots or screen recordings
   - Error messages and logs
   - Browser console output

### Feature Requests

When requesting features, please include:

1. **Problem description:**
   - What problem does this solve?
   - Why is it important?

2. **Proposed solution:**
   - How should it work?
   - Alternative solutions considered

3. **Additional context:**
   - Examples from other applications
   - Mockups or diagrams if helpful

## 💻 Development Areas

### Backend (Django)

**Skills needed:** Python, Django, REST APIs, WebLLM integration

**Areas to contribute:**
- API endpoints for new features
- WebLLM bridge improvements
- Database models and migrations
- Authentication and authorization
- Performance optimizations

### Frontend (React/TypeScript)

**Skills needed:** TypeScript, React, CSS, UI/UX design

**Areas to contribute:**
- Chat interface improvements
- New UI components
- Responsive design enhancements
- Accessibility improvements
- WebLLM client integration

### Documentation

**Skills needed:** Technical writing, Markdown

**Areas to contribute:**
- API documentation
- User guides and tutorials
- Code documentation
- Deployment guides
- Video tutorials

### Testing

**Skills needed:** Python testing, JavaScript testing

**Areas to contribute:**
- Unit tests for backend
- Integration tests
- Frontend component tests
- End-to-end tests
- Performance tests

### DevOps & Deployment

**Skills needed:** Docker, CI/CD, Cloud platforms

**Areas to contribute:**
- Docker configurations
- CI/CD pipelines
- Cloud deployment guides
- Monitoring and logging
- Performance optimization

## 🔄 Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
```bash
# Backend tests
python manage.py test

# Frontend tests
cd src/cognitio_app/backend/frontend-src
npm run test

# Manual testing
python manage.py runserver
```

4. **Commit and push:**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

5. **Create a Pull Request:**
   - Use the PR template
   - Provide clear description of changes
   - Link to related issues
   - Request reviews from maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or properly documented)
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Steps

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag
4. Build and test release
5. Publish to package repositories

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on the code, not the person
- Help others learn and grow

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** General questions, ideas
- **Pull Requests:** Code reviews, discussions

### Getting Help

- Check existing issues and documentation first
- Provide minimal reproducible examples
- Be patient and respectful
- Help others when you can

## 🎯 Contribution Ideas

### Good First Issues

- Fix typos in documentation
- Add unit tests for existing code
- Improve error messages
- Add TypeScript types
- Update dependencies

### Advanced Contributions

- WebLLM model optimization
- Real-time collaboration features
- Plugin/extension system
- Advanced chat features (voice, images)
- Performance monitoring

### Documentation Improvements

- Video tutorials
- API examples
- Deployment guides
- Architecture diagrams
- Best practices guides

## 📊 Metrics and Analytics

We track the following metrics to understand project health:

- **Code coverage:** Aim for >80%
- **Performance:** API response times, frontend load times
- **User experience:** Accessibility, usability
- **Documentation:** Completeness, clarity

## 🙏 Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributor graphs
- Project documentation

Thank you for contributing to the Cognitio Chat Framework! Your contributions help make local AI more accessible to everyone. 🚀
