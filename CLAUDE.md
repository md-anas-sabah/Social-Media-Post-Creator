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
# Edit .env to add your OPENAI_API_KEY, FAL_KEY, CLAUDE_API_KEY, and optionally OPENAI_ORGANIZATION_ID
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
- `anthropic` - Claude API client for content refinement
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
  - Copywriter Agent: Creates polished captions with Claude refinement
  - Creative Agent: Generates images using advanced Ideogram V2A tools with Claude prompt refinement
  - Hashtag Agent: Researches strategic hashtags with Claude optimization
  - Timing Agent: Provides optimal posting times
  - Calendar Planner Agent: Creates comprehensive content calendars
- **tasks.py**: Contains `SocialMediaTasks` class with specialized tasks for each workflow step
- **claude_refinement.py**: Claude API integration service for content refinement

### Advanced Agent System
- **Script Agent**: Uses GPT-4 for creative ideation and concept development
- **Copywriter Agent**: Uses GPT-4 for high-quality, platform-optimized copywriting + Claude Sonnet 3.5 for advanced caption refinement
- **Creative Agent**: Uses GPT-4 with high temperature (0.9) for maximum creativity + Claude Sonnet 3.5 for world-class image prompt refinement + multiple specialized image tools
- **Hashtag Agent**: Uses GPT-3.5 for hashtag research and trending analysis + Claude Sonnet 3.5 for hashtag strategy optimization
- **Timing Agent**: Uses GPT-3.5 with custom timing optimization tool
- **Calendar Planner Agent**: Uses GPT-4 for comprehensive strategic content planning

### Claude AI Integration
- **Prompt Refinement**: Claude Sonnet 3.5 refines all image generation prompts before sending to FAL.ai for world-class visual results
- **Caption Enhancement**: Claude Sonnet 3.5 optimizes captions for maximum engagement and viral potential
- **Hashtag Strategy**: Claude Sonnet 3.5 analyzes and optimizes hashtag strategies for maximum reach
- **Professional Templates**: Uses structured prompt templates for consistent, high-quality outputs

### Task Flow - Single Posts
1. **Ideation Task**: Generate 3 creative post concepts with compelling hooks
2. **Copywriting Task**: Create platform-optimized captions with engagement focus → Claude refinement for maximum engagement
3. **Image Generation Task**: Create custom visuals (single, carousel, or story format) → Claude prompt refinement for world-class results
4. **Hashtag Research Task**: Find 8-12 strategic hashtags for maximum reach → Claude optimization for viral potential
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

## Latest Updates - Claude AI Integration (December 2024)

### 🚀 Major Enhancement: Claude-Powered Content Refinement

We've integrated **Claude Sonnet 3.5** as a content refinement layer to elevate every aspect of content creation to world-class standards.

#### New Capabilities Added:

**1. World-Class Image Prompt Refinement**
- Every image prompt is now refined by Claude before being sent to FAL.ai
- Transforms basic prompts into detailed, professional specifications
- Uses structured template format for consistent, high-quality results
- Ensures perfect text clarity, realistic proportions, and professional composition
- All original and refined prompts are preserved for comparison

**2. Advanced Caption Enhancement**
- Copywriter Agent now uses Claude to refine all captions for maximum engagement
- Hook-driven content with emotional storytelling techniques
- Platform-specific optimization for Instagram, Facebook, LinkedIn, Twitter
- Strategic call-to-actions and viral potential optimization
- Authentic, conversational tone with strategic formatting

**3. Strategic Hashtag Optimization**
- Hashtag Agent leverages Claude for intelligent hashtag strategy
- Mix of trending, niche, and audience-targeted hashtags
- Platform-specific hashtag counts and strategies
- Community engagement and discoverability optimization
- Brand positioning and target audience alignment

#### Technical Implementation:

**New Files Added:**
- `claude_refinement.py`: Core Claude API integration service
- Enhanced `agents.py`: Integrated Claude tools into existing agents
- Updated environment setup with `CLAUDE_API_KEY` requirement

**Enhanced Workflow:**
1. **Original Content Creation** → **Claude Refinement** → **Final Output**
2. **Dual-AI Approach**: GPT-4 for creativity + Claude for refinement
3. **Quality Tracking**: All original and refined versions preserved
4. **Error Handling**: Graceful fallbacks if Claude refinement fails

#### Benefits:
- ✅ **World-Class Image Quality**: Professional, detailed image prompts
- ✅ **Maximum Engagement**: Optimized captions for viral potential
- ✅ **Strategic Reach**: Intelligent hashtag strategies
- ✅ **Professional Output**: Consistent, high-quality content
- ✅ **Platform Optimization**: Tailored for each social media platform

#### Setup Requirements:
- Add `CLAUDE_API_KEY` to your `.env` file
- Install `anthropic>=0.34.0` package
- Claude API account with Sonnet 3.5 access

This upgrade transforms the system from good to exceptional, ensuring every piece of content meets professional marketing standards with maximum engagement potential.

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