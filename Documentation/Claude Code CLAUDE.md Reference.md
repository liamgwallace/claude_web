# Claude Code CLAUDE.md Reference

## Overview

CLAUDE.md is a special instruction file that Claude Code automatically loads into context when starting conversations. This comprehensive reference covers everything you need to know about creating, managing, and optimizing CLAUDE.md files.

## What is CLAUDE.md?

CLAUDE.md is Claude Code's project instruction system that:

- **Automatically loads** into context when Claude starts
- **Provides project-specific guidance** to Claude
- **Supports team collaboration** through shared instructions
- **Enables personal customization** via user-level files
- **Supports file imports** for modular instruction organization

## File Locations and Scope

### Project-Level CLAUDE.md
- **Location**: `./CLAUDE.md` (project root)
- **Scope**: Team-shared project instructions
- **Git Status**: Typically checked into version control
- **Purpose**: Define project-wide conventions, architecture, and workflows

### User-Level CLAUDE.md
- **Location**: `~/.claude/CLAUDE.md`
- **Scope**: Personal preferences across all projects
- **Git Status**: Not checked in (personal file)
- **Purpose**: Individual coding preferences and shortcuts

### Recursive Discovery
Claude searches up the directory tree to find CLAUDE.md files, allowing for:
- **Parent directory instructions** for multi-project repositories
- **Organization-wide standards** at higher directory levels
- **Inherited configurations** from project hierarchies

## File Format and Structure

### Basic Structure
```markdown
# Project Name

## Architecture Overview
Brief description of project structure and key components.

## Development Guidelines
- Code style preferences
- Testing requirements
- Review processes

## Common Commands
- `npm start` - Start development server
- `npm test` - Run test suite
- `npm run build` - Build for production

## File Organization
- `/src` - Source code
- `/tests` - Test files
- `/docs` - Documentation

## Important Notes
Any project-specific warnings or unusual behaviors.
```

### Advanced Features

#### File Imports
Use `@path/to/import` syntax to include other files:

```markdown
# Main Instructions

## Code Standards
@.claude/code-standards.md

## Testing Guidelines  
@.claude/testing-guide.md

## Personal Preferences
@~/.claude/personal-coding-style.md
```

**Import Features:**
- Support both relative and absolute paths
- Can import from user home directory (`~/.claude/`)
- Maximum import depth of 5 hops
- Imports not evaluated inside code blocks
- Useful for separating team vs. personal instructions

#### Structured Organization
```markdown
# Project Instructions

## Code Style
- Use 2-space indentation
- Prefer const over let when possible
- Use descriptive variable names

## Architecture Patterns
- Follow MVC pattern
- Use dependency injection
- Implement repository pattern for data access

## Testing Strategy
- Write unit tests for all business logic
- Use integration tests for API endpoints
- Maintain >80% code coverage

## Deployment Process
- Deploy to staging first
- Run smoke tests
- Require approval for production deploys

## Troubleshooting
Common issues and their solutions...
```

## Content Guidelines

### What to Include

#### Repository Information
- **Branching Strategy**: Git workflow preferences (GitFlow, GitHub Flow, etc.)
- **Merge vs. Rebase**: Team preference for code integration
- **Commit Message Format**: Conventional commits or other standards
- **Code Review Process**: Requirements and expectations

#### Development Environment
- **Required Tools**: Node.js versions, Python environments, etc.
- **Environment Variables**: Required configuration (without secrets)
- **Build Commands**: How to compile, test, and run the project
- **IDE Preferences**: Recommended extensions or configurations

#### Code Standards
- **Formatting Rules**: Indentation, line length, bracket styles
- **Naming Conventions**: Variables, functions, classes, files
- **Code Organization**: File structure, module patterns
- **Documentation Requirements**: JSDoc, docstrings, README updates

#### Testing Guidelines
- **Testing Framework**: Jest, PyTest, etc.
- **Coverage Requirements**: Minimum coverage percentages
- **Test Organization**: Unit, integration, e2e test structure
- **Mock/Stub Strategies**: How to handle external dependencies

#### Project-Specific Context
- **Architecture Patterns**: MVC, microservices, event-driven, etc.
- **Key Dependencies**: Important libraries and their purposes
- **External Services**: APIs, databases, third-party integrations
- **Performance Considerations**: Bottlenecks, optimization strategies

### Writing Best Practices

#### Be Specific
- ❌ "Format code properly"
- ✅ "Use 2-space indentation for JavaScript, 4-space for Python"

#### Use Structure
- Organize with clear markdown headings
- Use bullet points for scannable lists
- Group related information together
- Include examples where helpful

#### Keep Current
- Review and update regularly
- Remove outdated information
- Add new learnings and patterns
- Reflect current project state

#### Make it Actionable
- Provide specific commands to run
- Include code examples
- Link to relevant documentation
- Explain the "why" behind decisions

## Management Commands

### Quick Memory Addition
Use `#` during conversation to quickly add memories:
```
# This adds a memory about the current topic
```

### Memory Management Commands
- `/memory` - Edit memory files directly
- `/init` - Bootstrap a new CLAUDE.md template
- `/help` - List available commands

### CLI Bootstrap
Create initial CLAUDE.md structure:
```bash
claude init
```

This generates a basic template you can customize.

## Advanced Patterns

### Modular Instructions
Split large CLAUDE.md files into focused modules:

**Main CLAUDE.md:**
```markdown
# Project Instructions

## Core Standards
@.claude/coding-standards.md

## API Guidelines
@.claude/api-conventions.md

## Database Patterns
@.claude/database-patterns.md

## Personal Preferences
@~/.claude/personal-preferences.md
```

**Module files:**
- `.claude/coding-standards.md` - Code formatting and style
- `.claude/api-conventions.md` - REST API design patterns
- `.claude/database-patterns.md` - Database schema and query guidelines
- `~/.claude/personal-preferences.md` - Individual developer preferences

### Context-Specific Instructions
Use conditional or contextual instructions:

```markdown
# Project Instructions

## Frontend Development
When working on React components:
- Use functional components with hooks
- Implement proper PropTypes
- Follow accessibility guidelines

## Backend Development  
When working on API endpoints:
- Validate all inputs
- Use proper HTTP status codes
- Implement rate limiting

## Database Changes
When modifying database schema:
- Write migration scripts
- Update documentation
- Consider backward compatibility
```

### Template-Based Instructions
Create instruction templates for different project types:

**Web Application Template:**
```markdown
# Web Application Instructions

## Tech Stack
- Frontend: React/Vue/Angular
- Backend: Node.js/Python/Java
- Database: PostgreSQL/MongoDB
- Deployment: Docker/Kubernetes

## Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Run CI/CD pipeline
4. Request code review
5. Merge to main branch

## Code Standards
[Standard formatting and style guidelines]

## Testing Strategy
[Unit, integration, and e2e testing approaches]
```

## Integration with Other Tools

### Version Control Integration
Include git-specific instructions:

```markdown
# Git Workflow

## Branch Naming
- feature/description-of-feature
- bugfix/description-of-fix
- hotfix/critical-issue-fix

## Commit Messages
Follow conventional commits:
- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code restructuring
- test: adding tests
- chore: maintenance tasks

## Pull Request Process
1. Ensure CI passes
2. Request review from team lead
3. Address feedback
4. Squash commits before merge
```

### CI/CD Integration
Document build and deployment processes:

```markdown
# CI/CD Pipeline

## Build Process
- Runs on all pull requests
- Includes linting, testing, and security scans
- Must pass before merge allowed

## Deployment Stages
1. Development: Auto-deploy from develop branch
2. Staging: Manual deploy from release branches  
3. Production: Manual deploy with approval

## Environment Variables
Required for deployment:
- API_KEY (external service authentication)
- DATABASE_URL (database connection)
- REDIS_URL (caching service)
```

### IDE Integration
Provide IDE-specific guidance:

```markdown
# IDE Configuration

## VS Code
Recommended extensions:
- ESLint for code linting
- Prettier for code formatting
- GitLens for git integration
- Thunder Client for API testing

Settings:
- Enable format on save
- Use workspace settings file
- Configure debugging for Node.js

## IntelliJ IDEA
- Enable automatic import optimization
- Configure code style scheme
- Set up run configurations
```

## Troubleshooting Common Issues

### Memory Not Loading
If CLAUDE.md isn't being recognized:
1. Check file location (project root or ~/.claude/)
2. Verify file name is exactly "CLAUDE.md"
3. Ensure file has content (not empty)
4. Try restarting Claude Code session

### Import Paths Not Working
If @imports aren't loading:
1. Verify file paths are correct
2. Check maximum import depth (5 hops)
3. Ensure imported files exist and are readable
4. Use absolute paths for home directory imports

### Instructions Not Being Applied
If Claude isn't following instructions:
1. Make instructions more specific and actionable
2. Use examples to clarify expectations
3. Break complex instructions into smaller parts
4. Test with `/memory` command to verify content

### Performance Issues with Large Files
If CLAUDE.md files are too large:
1. Split into smaller, focused modules
2. Use imports to organize content
3. Remove outdated or redundant information
4. Keep core instructions concise

## Examples by Project Type

### React Application
```markdown
# React Project Instructions

## Component Standards
- Use functional components with hooks
- Implement PropTypes for all props
- Use CSS Modules for styling
- Follow accessibility guidelines (WCAG 2.1)

## State Management
- Use useState for local state
- Use useContext for shared state
- Consider Redux for complex state trees
- Avoid prop drilling

## Testing
- Test components with React Testing Library
- Mock external dependencies
- Test user interactions, not implementation details
- Maintain >80% coverage

## File Organization
- `/src/components` - Reusable UI components
- `/src/pages` - Page-level components  
- `/src/hooks` - Custom React hooks
- `/src/utils` - Utility functions
- `/src/services` - API client code
```

### Python API Project
```markdown
# Python API Instructions

## Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Use descriptive variable names
- Maximum line length: 88 characters

## Framework Patterns
- Use FastAPI for REST APIs
- Implement dependency injection
- Use Pydantic models for validation
- Follow repository pattern for data access

## Testing
- Use pytest for all tests
- Mock external services with responses
- Test both success and error cases
- Use fixtures for test data setup

## Database
- Use SQLAlchemy ORM
- Write Alembic migrations for schema changes
- Use async/await for database operations
- Implement proper connection pooling
```

### Node.js Microservice
```markdown
# Node.js Microservice Instructions

## Architecture
- Follow hexagonal architecture pattern
- Separate business logic from infrastructure
- Use dependency injection with containers
- Implement proper error handling

## API Design
- Follow RESTful conventions
- Use OpenAPI/Swagger documentation
- Implement proper HTTP status codes
- Add request/response validation

## Error Handling
- Use custom error classes
- Implement global error middleware
- Log errors with proper severity levels
- Return consistent error responses

## Performance
- Use connection pooling for databases
- Implement caching where appropriate
- Add request rate limiting
- Monitor with APM tools
```

This comprehensive reference should help you create effective CLAUDE.md files that provide Claude with the context and instructions needed to work effectively on your projects.