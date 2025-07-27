# Contributing to Claude Web Runner

Thank you for your interest in contributing! This project is designed to be simple and approachable.

## 🚀 Getting Started

1. **Fork and clone** the repository
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Set up Claude CLI**: `npm install -g @anthropic-ai/claude-code`
4. **Run locally**: `python start_app.py`

## 🛠️ Development Guidelines

### Project Philosophy
- **Keep it simple** - This is a hobby project focused on functionality over complexity
- **User-first** - Changes should improve the user experience
- **Maintainable** - Code should be easy to understand and modify
- **Compatible** - Maintain compatibility with Claude CLI

### Code Style
- Follow Python PEP 8 conventions
- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions focused and small

### Architecture
- **Backend**: Flask API handles Claude CLI integration
- **Frontend**: Chainlit provides the web interface
- **Storage**: JSON files for simplicity (no database)
- **Integration**: REST API between frontend and backend

## 🧪 Testing

Before submitting changes:

1. **Test manually**: Run `python start_app.py` and test the UI
2. **Test API**: Use `python test_api.py` to verify backend functionality
3. **Check imports**: Ensure all dependencies work correctly

## 📝 Making Changes

### Bug Fixes
1. Create an issue describing the bug
2. Fork and create a feature branch: `git checkout -b fix-bug-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### New Features
1. Open an issue to discuss the feature first
2. Fork and create a feature branch: `git checkout -b feature-name`
3. Implement the feature
4. Update documentation if needed
5. Test the feature works end-to-end
6. Submit a pull request

### Documentation
- Update README.md for user-facing changes
- Update CLAUDE.md for developer guidance
- Add comments for complex code sections
- Update requirements.txt if adding dependencies

## 🎯 Areas for Contribution

### High Impact Areas
- **UI/UX improvements** - Better navigation, visual enhancements
- **Error handling** - More graceful error messages and recovery
- **Performance** - Faster responses, better resource usage
- **Documentation** - Clearer instructions, more examples

### Feature Ideas
- File editing within the web interface
- Export/import of projects and threads
- Search functionality across conversations
- Dark/light theme support
- Docker containerization
- Configuration management

### Bug Reports
When reporting bugs, please include:
- Steps to reproduce the issue
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Console logs or error messages
- Screenshots if relevant

## 🔍 Code Review Process

1. **All changes** go through pull requests
2. **Maintainers review** for functionality and code quality
3. **CI checks** must pass (basic import and API tests)
4. **Manual testing** is encouraged for UI changes

## 🎉 Recognition

Contributors will be:
- Listed in the repository contributors
- Mentioned in release notes for significant contributions
- Thanked in the project README

## ❓ Questions?

- **General questions**: Open a GitHub issue with the "question" label
- **Development help**: Check existing issues or create a new one
- **Feature discussions**: Use GitHub Discussions when available

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thanks for helping make Claude Web Runner better! 🙏**