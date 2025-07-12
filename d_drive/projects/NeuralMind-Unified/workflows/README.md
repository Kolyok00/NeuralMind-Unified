# Workflows - n8n Automation and Ottomator Agents

This directory contains the workflow automation components using n8n and ottomator agents.

## Setup Instructions

1. Add the ottomator-agents submodule:
```bash
git submodule add https://github.com/coleam00/ottomator-agents workflows
```

2. The n8n service is automatically started via Docker Compose
3. Access n8n interface at: http://localhost:5678

## Components

### n8n Workflow Engine
- Visual workflow builder
- API integrations
- Webhook support
- Scheduled executions
- Error handling and retries

### Ottomator Agents
- Pre-built AI agent workflows
- Task automation templates
- Integration with various AI services
- Custom agent development framework

## Pre-built Workflows

### AI Agent Workflows
- **Code Review Agent**: Automated code review using AI
- **Documentation Generator**: Auto-generate docs from code
- **Bug Triaging Agent**: Classify and prioritize issues
- **Content Moderator**: AI-powered content filtering

### Integration Workflows
- **GitHub Integration**: PR reviews, issue management
- **Slack/Discord Bots**: AI-powered chat assistance
- **Email Processing**: Smart email categorization and response
- **Data Pipeline**: ETL workflows with AI enhancement

### Monitoring Workflows
- **System Health**: Monitor services and alert on issues
- **Performance Tracking**: Collect and analyze metrics
- **Error Reporting**: Automated bug reporting and categorization

## Configuration

Key environment variables:
- `N8N_HOST`: n8n server host
- `N8N_PORT`: n8n server port
- `N8N_BASIC_AUTH_USER`: Basic auth username
- `N8N_BASIC_AUTH_PASSWORD`: Basic auth password
- `WEBHOOK_URL`: Base URL for webhooks

## Usage

### Accessing n8n Interface
1. Open http://localhost:5678 in your browser
2. Log in with credentials from .env file
3. Import workflow templates from the `templates/` directory

### Creating Custom Workflows
1. Use the visual workflow editor
2. Connect to AI services (Ollama, OpenAI, etc.)
3. Set up triggers (webhooks, schedules, file watchers)
4. Configure error handling and notifications

### API Usage
```bash
# Trigger a workflow via webhook
curl -X POST http://localhost:5678/webhook/your-workflow-id \
  -H "Content-Type: application/json" \
  -d '{"data": "your input data"}'
```

## Workflow Templates

Located in `templates/` directory:
- `ai-code-review.json` - AI-powered code review workflow
- `document-qa.json` - Document Q&A with RAG
- `web-scraping-pipeline.json` - Automated web scraping
- `social-media-monitoring.json` - Social media sentiment analysis
- `automated-testing.json` - AI-enhanced testing workflows

## Integration Points

- **Ollama**: Local LLM inference
- **OpenAI/Anthropic**: Cloud AI services
- **Supabase**: Database operations
- **Neo4j**: Knowledge graph queries
- **Crawl4AI**: Web scraping operations
- **Langfuse**: Workflow monitoring and tracing
