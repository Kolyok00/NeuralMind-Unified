# Core Agent - OpenCode Integration

This directory will contain the OpenCode AI coding assistant integration.

## Setup Instructions

1. After cloning the main repository, add the OpenCode submodule:
```bash
git submodule add https://github.com/opencode-ai/opencode core-agent
```

2. Install OpenCode:
```bash
go install github.com/opencode-ai/opencode@latest
```

3. Configure OpenCode:
```bash
cp config/.opencode.json ~/.opencode/config.json
```

## Features

- Terminal-based AI coding assistant
- Support for multiple LLM providers (OpenAI, Anthropic, Groq, OpenRouter, local Ollama)
- Agentive architecture for code generation and self-correction
- Integration with local development environment

## Configuration

The configuration file should be placed in `~/.opencode/config.json` and should include:

- API keys for various LLM providers
- Model preferences
- Local Ollama endpoint configuration
- Code generation preferences

## Usage

Once configured, use OpenCode by running:
```bash
opencode
```

This will start the interactive terminal interface for AI-assisted coding.
