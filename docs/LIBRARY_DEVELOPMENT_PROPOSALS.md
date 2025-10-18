# Sentence Completion Library - Development Proposals

## Overview

This document outlines my proposals for developing the sentence completion library as a separate, reusable package that can be tested locally without publishing to NPM.

## Table of Contents

1. [Repository Structure Proposal](#repository-structure-proposal)
2. [Local Development Workflow](#local-development-workflow)
3. [Development Tools & Scripts](#development-tools--scripts)
4. [Testing Strategy](#testing-strategy)
5. [Integration Approach](#integration-approach)
6. [Deployment Strategy](#deployment-strategy)

## Repository Structure Proposal

### Option 1: Completely Separate Repository (Recommended)

```
your-workspace/
├── ai-assistant-tobee/                    # Your main project
│   ├── frontend-nextjs/
│   │   ├── package.json
│   │   ├── app/
│   │   └── ...
│   ├── backend/
│   └── docs/
└── sentence-completion-lib/               # New separate repository
    ├── packages/
    │   ├── core/                          # Core prediction engine
    │   │   ├── src/
    │   │   ├── dist/
    │   │   ├── package.json
    │   │   └── tsconfig.json
    │   ├── react/                         # React integration
    │   │   ├── src/
    │   │   ├── dist/
    │   │   ├── package.json
    │   │   └── tsconfig.json
    │   ├── vue/                           # Vue integration
    │   │   ├── src/
    │   │   ├── dist/
    │   │   ├── package.json
    │   │   └── tsconfig.json
    │   └── vanilla/                       # Vanilla JS API
    │       ├── src/
    │       ├── dist/
    │       ├── package.json
    │       └── tsconfig.json
    ├── examples/                          # Usage examples
    │   ├── nextjs/
    │   ├── react/
    │   ├── vue/
    │   └── vanilla/
    ├── docs/                              # Documentation
    ├── tests/                             # Test suites
    ├── package.json                       # Root package.json
    ├── lerna.json                         # Monorepo configuration
    ├── tsconfig.json                      # Root TypeScript config
    └── README.md
```

### Benefits of Separate Repository:
- **Independent Development**: Library evolves separately from main project
- **Reusability**: Other projects can easily adopt
- **Community Ready**: External contributors can find and contribute
- **Clean Versioning**: Separate release cycles
- **Focused Documentation**: Library-specific docs and examples

## Local Development Workflow

### Method 1: npm link (Recommended for Active Development)

#### Setup Commands:
```bash
# In sentence-completion-lib repository
cd sentence-completion-lib
npm install
npm run build
npm link

# In your main project
cd ai-assistant-tobee/frontend-nextjs
npm link @sentence-completion/react
```

#### Daily Development:
```bash
# Make changes in library
cd sentence-completion-lib
npm run build  # or npm run dev for watch mode

# Changes automatically reflected in main project
cd ../ai-assistant-tobee/frontend-nextjs
npm run dev
```

### Method 2: Local File Path (Stable Testing)

#### In Main Project's package.json:
```json
{
  "dependencies": {
    "@sentence-completion/react": "file:../sentence-completion-lib/packages/react"
  }
}
```

#### Install:
```bash
npm install
```

### Method 3: Workspace Configuration (Monorepo Style)

#### In Main Project's package.json:
```json
{
  "workspaces": [
    "workspaces/*",
    "../sentence-completion-lib/packages/*"
  ]
}
```

## Development Tools & Scripts

### Library Repository Setup

#### Root package.json:
```json
{
  "name": "sentence-completion-lib",
  "private": true,
  "workspaces": [
    "packages/*"
  ],
  "scripts": {
    "build": "lerna run build",
    "dev": "lerna run dev --parallel",
    "test": "lerna run test",
    "clean": "lerna run clean",
    "link": "lerna exec -- npm link",
    "unlink": "lerna exec -- npm unlink"
  },
  "devDependencies": {
    "lerna": "^8.0.0",
    "typescript": "^5.0.0",
    "rollup": "^4.0.0"
  }
}
```

#### lerna.json:
```json
{
  "version": "0.0.0",
  "npmClient": "npm",
  "command": {
    "publish": {
      "conventionalCommits": true
    },
    "version": {
      "conventionalCommits": true
    }
  },
  "packages": [
    "packages/*"
  ]
}
```

### Development Helper Scripts

#### dev-setup.sh (Main Project):
```bash
#!/bin/bash
# dev-setup.sh - Setup local development environment

echo "🚀 Setting up local development environment..."

# Check if library repo exists
if [ ! -d "../sentence-completion-lib" ]; then
    echo "❌ Library repository not found at ../sentence-completion-lib"
    echo "Please clone the library repository first"
    exit 1
fi

# Build the library
echo "📦 Building sentence completion library..."
cd ../sentence-completion-lib
npm install
npm run build

# Link the library packages
echo "🔗 Linking library packages..."
npm run link

# Go back to main project
cd ../ai-assistant-tobee/frontend-nextjs

# Link the packages you need
echo "🔗 Linking packages to main project..."
npm link @sentence-completion/core
npm link @sentence-completion/react

echo "✅ Local development setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make changes in ../sentence-completion-lib"
echo "2. Run 'npm run build' in library repo"
echo "3. Changes will be reflected in this project"
echo ""
echo "🔄 For watch mode:"
echo "1. Run 'npm run dev' in library repo (Terminal 1)"
echo "2. Run 'npm run dev' in this project (Terminal 2)"
```

#### dev-cleanup.sh (Main Project):
```bash
#!/bin/bash
# dev-cleanup.sh - Clean up local development links

echo "🧹 Cleaning up local development links..."

# Unlink packages
npm unlink @sentence-completion/core
npm unlink @sentence-completion/react

# Go to library repo and unlink
cd ../sentence-completion-lib
npm run unlink

echo "✅ Cleanup complete!"
```

### Package.json Scripts for Each Package

#### Core Package (packages/core/package.json):
```json
{
  "name": "@sentence-completion/core",
  "version": "0.0.1",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "rollup -c",
    "dev": "rollup -c -w",
    "test": "jest",
    "clean": "rm -rf dist"
  },
  "dependencies": {
    "@xenova/transformers": "^2.6.0",
    "onnxruntime-web": "^1.16.0"
  }
}
```

#### React Package (packages/react/package.json):
```json
{
  "name": "@sentence-completion/react",
  "version": "0.0.1",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "rollup -c",
    "dev": "rollup -c -w",
    "test": "jest",
    "clean": "rm -rf dist"
  },
  "dependencies": {
    "@sentence-completion/core": "workspace:*"
  },
  "peerDependencies": {
    "react": ">=16.8.0"
  }
}
```

## Testing Strategy

### Local Testing Approach

#### 1. Unit Testing
```bash
# In library repo
cd sentence-completion-lib
npm run test
```

#### 2. Integration Testing
```bash
# Test with main project
cd ai-assistant-tobee/frontend-nextjs
npm run test
```

#### 3. Manual Testing
```bash
# Start both projects
# Terminal 1: Library watch mode
cd sentence-completion-lib
npm run dev

# Terminal 2: Main project
cd ai-assistant-tobee/frontend-nextjs
npm run dev
```

### Test Configuration

#### Jest Configuration (packages/core/jest.config.js):
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  testMatch: ['**/__tests__/**/*.test.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts'
  ]
};
```

## Integration Approach

### Phase 1: Library Development
1. **Create separate repository**
2. **Set up monorepo structure**
3. **Implement core functionality**
4. **Create framework integrations**
5. **Add comprehensive testing**

### Phase 2: Local Integration
1. **Use npm link for development**
2. **Test integration with main project**
3. **Refine API based on usage**
4. **Add documentation and examples**

### Phase 3: Production Integration
1. **Publish to NPM (when ready)**
2. **Update main project to use published version**
3. **Set up CI/CD for both repositories**

## Deployment Strategy

### Development Phase
- **Local linking** for active development
- **File paths** for stable testing
- **Watch mode** for automatic rebuilding

### Pre-Production Phase
- **Local NPM registry** (verdaccio) for testing
- **Beta releases** to NPM for team testing
- **Integration testing** with main project

### Production Phase
- **Official NPM publishing**
- **CDN distribution**
- **Version management** and updates

## Quick Start Commands

### Initial Setup:
```bash
# Clone both repositories
git clone <your-main-repo> ai-assistant-tobee
git clone <your-library-repo> sentence-completion-lib

# Setup library
cd sentence-completion-lib
npm install
npm run build
npm run link

# Setup main project
cd ../ai-assistant-tobee/frontend-nextjs
npm link @sentence-completion/react
npm install
```

### Daily Development:
```bash
# Make changes in library, then:
cd sentence-completion-lib
npm run build

# Test in main project
cd ../ai-assistant-tobee/frontend-nextjs
npm run dev
```

### Watch Mode Development:
```bash
# Terminal 1: Library watch mode
cd sentence-completion-lib
npm run dev

# Terminal 2: Main project
cd ai-assistant-tobee/frontend-nextjs
npm run dev
```

## Benefits of This Approach

### For Development:
- **Fast iteration** with local linking
- **Real-time testing** with watch mode
- **Isolated testing** of library features
- **Easy switching** between development methods

### For Production:
- **Clean separation** of concerns
- **Independent versioning** and releases
- **Reusable across projects**
- **Community contribution** ready

### For Maintenance:
- **Focused documentation** for each component
- **Independent CI/CD** pipelines
- **Clear dependency management**
- **Easier debugging** and testing

## Next Steps

1. **Create separate repository** for the library
2. **Set up monorepo structure** with Lerna
3. **Implement core functionality** first
4. **Create React integration** for your Next.js project
5. **Set up local development workflow**
6. **Test integration** with existing ChatInput component
7. **Iterate and refine** based on usage

This approach provides the best of both worlds: independent library development with seamless local testing and integration.

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*  
*Author: AI Assistant*
