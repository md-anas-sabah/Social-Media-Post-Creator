# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```
The main entry point prompts for a social media post idea and platform, then creates a complete post with caption, image, hashtags, and timing recommendations.

### Environment Setup
Copy `.env_example` to `.env` and add your API keys:
```bash
cp .env_example .env
# Edit .env to add your OPENAI_API_KEY, FAL_KEY, and optionally OPENAI_ORGANIZATION_ID
```

### Dependencies
This project uses:
- `crewai` - Multi-agent framework
- `langchain-openai` - OpenAI integration
- `python-decouple` - Environment variable management
- `openai` - OpenAI API client for LLM functions
- `fal-client` - FAL AI client for Ideogram V2A image generation

Install with:
```bash
pip install crewai langchain-openai python-decouple openai fal-client
```

## Architecture

This is a specialized CrewAI-based social media post creator with the following workflow:

### User Experience Flow
1. User provides a natural language prompt (e.g., "Eid Mubarak post for my fashion brand")
2. System generates 3 creative post ideas
3. User selects their preferred idea
4. System creates complete post with caption, image, hashtags, and optimal timing

### Core Components
- **main.py**: Entry point containing `SocialMediaPostCreator` class that orchestrates the workflow
- **agents.py**: Contains `SocialMediaAgents` class with specialized agents:
  - Script Agent: Generates 3 creative post ideas
  - Copywriter Agent: Creates polished captions
  - Creative Agent: Generates images using Ideogram V2A
  - Hashtag Agent: Researches relevant hashtags
  - Timing Agent: Provides optimal posting times
- **tasks.py**: Contains `SocialMediaTasks` class defining specialized tasks for each step

### Agent System
- **Script Agent**: Uses GPT-4 for creative ideation
- **Copywriter Agent**: Uses GPT-4 for high-quality copywriting
- **Creative Agent**: Uses GPT-4 with high temperature (0.9) for creativity + Ideogram V2A tool
- **Hashtag Agent**: Uses GPT-3.5 for hashtag research
- **Timing Agent**: Uses GPT-3.5 with custom timing tool

### Task Flow
1. **Ideation Task**: Generate 3 post concepts with hooks
2. **Copywriting Task**: Create platform-optimized caption
3. **Image Generation Task**: Create custom image using Ideogram V2A
4. **Hashtag Research Task**: Find relevant hashtags
5. **Timing Optimization Task**: Recommend optimal posting times

### Tools Available
- `generate_image`: Creates images using Ideogram V2A
- `get_optimal_posting_time`: Provides platform-specific posting time recommendations

### Platform Support
Supports Instagram, Facebook, Twitter, and LinkedIn with platform-specific optimizations.