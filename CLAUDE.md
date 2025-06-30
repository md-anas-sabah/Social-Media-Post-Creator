# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python main.py
```
The main entry point offers two modes:
1. **Single Post Creation**: Creates individual social media posts with 3 idea options, professional images, captions, hashtags, and timing
2. **Content Calendar Planning**: Generates comprehensive multi-week content calendars with strategic scheduling

### Environment Setup
Copy `.env_example` to `.env` and add your API keys:
```bash
cp .env_example .env
# Edit .env to add your OPENAI_API_KEY, FAL_KEY, and optionally OPENAI_ORGANIZATION_ID
```

### Dependencies
Install all required dependencies:
```bash
pip install -r requirements.txt
```

Core dependencies include:
- `crewai` - Multi-agent framework
- `langchain-openai` - OpenAI integration  
- `python-decouple` - Environment variable management
- `openai` - OpenAI API client for LLM functions
- `fal-client` - FAL AI client for Ideogram V2A image generation
- `requests` - HTTP requests for image downloading
- `uuid` - Unique identifier generation

## Architecture

This is a specialized CrewAI-based social media content creation system with two main workflows:

### Single Post Creation Workflow
1. User provides a natural language prompt (e.g., "Eid Mubarak post for my fashion brand")
2. System generates 3 creative post ideas with hooks and concepts
3. User selects their preferred idea (interactive choice)
4. System creates complete post with caption, custom images, hashtags, and optimal timing
5. All outputs saved to organized timestamped folders with JSON, Markdown, and HTML preview files

### Content Calendar Planning Workflow
1. User specifies calendar theme and requirements
2. System generates comprehensive multi-week content calendar
3. Includes daily scheduling, platform-specific content, strategic themes
4. Outputs saved as JSON, Markdown, and CSV files for easy import to scheduling tools

### Core Components
- **main.py**: Entry point with two main classes:
  - `SocialMediaPostCreator`: Handles single post creation workflow
  - `ContentCalendarPlanner`: Handles content calendar generation
- **agents.py**: Contains `SocialMediaAgents` class with specialized agents:
  - Script Agent: Generates 3 creative post ideas
  - Copywriter Agent: Creates polished captions
  - Creative Agent: Generates images using advanced Ideogram V2A tools
  - Hashtag Agent: Researches strategic hashtags
  - Timing Agent: Provides optimal posting times
  - Calendar Planner Agent: Creates comprehensive content calendars
- **tasks.py**: Contains `SocialMediaTasks` class with specialized tasks for each workflow step

### Advanced Agent System
- **Script Agent**: Uses GPT-4 for creative ideation and concept development
- **Copywriter Agent**: Uses GPT-4 for high-quality, platform-optimized copywriting
- **Creative Agent**: Uses GPT-4 with high temperature (0.9) for maximum creativity + multiple specialized image tools
- **Hashtag Agent**: Uses GPT-3.5 for hashtag research and trending analysis
- **Timing Agent**: Uses GPT-3.5 with custom timing optimization tool
- **Calendar Planner Agent**: Uses GPT-4 for comprehensive strategic content planning

### Task Flow - Single Posts
1. **Ideation Task**: Generate 3 creative post concepts with compelling hooks
2. **Copywriting Task**: Create platform-optimized captions with engagement focus
3. **Image Generation Task**: Create custom visuals (single, carousel, or story format)
4. **Hashtag Research Task**: Find 8-12 strategic hashtags for maximum reach
5. **Timing Optimization Task**: Recommend platform-specific optimal posting times

### Task Flow - Content Calendar
1. **Content Calendar Planning Task**: Generate comprehensive multi-week strategic calendar with daily entries, platform distribution, content types, themes, and performance goals

### Advanced Image Generation Tools
- `generate_image`: Creates single high-quality images using Ideogram V2A
- `generate_carousel_images`: Creates multiple images for carousel posts
- `generate_story_image`: Creates vertical story images (9:16 format, 1080x1920px)
- `generate_story_series`: Creates multiple story images for story series
- `get_optimal_posting_time`: Provides platform-specific posting time recommendations

### Content Format Support
- **Single Posts**: Regular social media posts with 1:1 aspect ratio
- **Carousel Posts**: Multi-slide posts for lists, tips, step-by-step content
- **Story Posts**: Vertical format optimized for Instagram/Facebook Stories
- **Story Series**: Multiple connected story posts for complex content

### Platform Support & Optimization
- **Instagram**: Posts, carousels, stories with Instagram-specific best practices
- **Facebook**: Posts, carousels, stories with Facebook algorithm optimization
- **Twitter**: Text-focused posts with visual enhancements
- **LinkedIn**: Professional content with business-focused messaging

### Output Organization
Each post/calendar creation generates:
- **Unique timestamped folder** in `/output/` directory
- **JSON file**: Complete structured data for programmatic access
- **Markdown file**: Human-readable summary with all details
- **HTML preview file**: Platform-specific UI preview for visual review
- **Image files**: All generated visuals saved locally with organized naming

### Cultural Intelligence
- **Default Context**: Indian/South Asian cultural representation for general content
- **Religious Content**: Appropriate cultural styling for specific religious holidays
- **Modern Representation**: Contemporary Indian lifestyle, clothing, and settings
- **Business Context**: Professional Indian business environments

### Quality Standards
- **Premium Image Quality**: High-resolution, professional photography style
- **Text Clarity**: Crystal-clear text overlays with perfect spelling accuracy
- **Platform Optimization**: Content tailored to each platform's best practices
- **Professional Templates**: Structured prompt templates for consistent quality
- **Error Handling**: Comprehensive error handling with fallback options

### File Structure
```
output/
├── [platform]_[type]_[prompt_slug]_[timestamp]/
│   ├── [platform]_[type]_[timestamp].json
│   ├── [platform]_[type]_[timestamp].md
│   ├── [platform]_[type]_preview_[timestamp].html
│   └── [generated_image_files]
templates/
├── instagram.html
├── facebook.html
├── twitter.html
└── linkedin.html
```