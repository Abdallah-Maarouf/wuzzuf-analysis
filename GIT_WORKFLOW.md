# Git Workflow Documentation

## Commit Message Conventions

This project follows conventional commit message format for clear project history:

### Format
```
<type>: <description>

[optional body]
```

### Types
- **feat**: New feature or functionality
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring without feature changes
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates

### Examples
```bash
feat: implement data cleaning pipeline
docs: update README with project structure
fix: resolve salary data parsing issue
refactor: optimize database query performance
```

## Branching Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Individual feature development
- **hotfix/***: Critical bug fixes

## Workflow Steps

1. **Initialize Repository**
   ```bash
   git init
   git remote add origin https://github.com/Abdallah-Maarouf/wuzzuf-analysis.git
   ```

2. **Daily Workflow**
   ```bash
   git add .
   git commit -m "feat: implement specific functionality"
   git push origin main
   ```

3. **Project Milestones**
   - Use tags for major releases
   - Example: `git tag v1.0.0 -m "Release: Complete Wuzzuf Analysis"`

## File Management

- Large data files are excluded via .gitignore
- Only processed/cleaned datasets under 100MB are tracked
- Generated visualizations and reports are included
- Database files are excluded (schema scripts included)

## Repository Structure

```
├── .git/                       # Git repository data
├── .gitignore                  # Ignored files configuration
├── README.md                   # Project documentation
├── GIT_WORKFLOW.md            # This file
└── [project files...]         # Project implementation
```