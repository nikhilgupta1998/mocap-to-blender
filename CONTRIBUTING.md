# Contributing to Motion Capture to Blender

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/mocap-to-blender.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python test_backend.py  # Run tests
```

### Frontend

```bash
cd frontend
npm install
npm run dev  # Start development server
```

## Code Style

### Python
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Maximum line length: 100 characters

### JavaScript/React
- Use ES6+ features
- Prefer functional components with hooks
- Use meaningful variable names
- Add comments for complex logic
- Format with Prettier (if available)

## Testing

### Backend Tests

Run the test suite:
```bash
cd backend
python test_backend.py
```

Add tests for new features in `test_backend.py`

### Frontend Tests

Currently manual testing is used. When adding features:
- Test in Chrome, Firefox, and Edge
- Test with different camera setups
- Verify responsive design
- Check error handling

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No console errors
- [ ] Commits are atomic and well-described

### PR Description

Include:
- What changes were made
- Why the changes were needed
- How to test the changes
- Screenshots (for UI changes)
- Related issue numbers

## Areas for Contribution

### High Priority

- [ ] Add unit tests for frontend components
- [ ] Implement FBX export
- [ ] Add hand tracking support
- [ ] Improve pose detection accuracy
- [ ] Performance optimizations

### Medium Priority

- [ ] Add face tracking
- [ ] Multi-camera support
- [ ] Mobile app version
- [ ] Cloud storage integration
- [ ] Animation preview playback

### Documentation

- [ ] Video tutorials
- [ ] More examples
- [ ] Troubleshooting guides
- [ ] Performance benchmarks
- [ ] API examples

### Bug Fixes

Check the Issues tab for reported bugs. Small bug fixes are always welcome!

## Reporting Bugs

When reporting bugs, include:
- Operating system and version
- Python version
- Node.js version
- Browser (for frontend issues)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs
- Screenshots if applicable

## Feature Requests

For feature requests:
- Check existing issues first
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity
- Discuss alternatives

## Code Review Process

1. Automated checks run on PR
2. Maintainer reviews code
3. Feedback provided if needed
4. Approval and merge when ready

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort! 🎉
