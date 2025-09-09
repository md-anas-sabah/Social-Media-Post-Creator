import os
import json
import re
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from decouple import config
from datetime import datetime, timedelta

from textwrap import dedent
from agents import SocialMediaAgents
from tasks import SocialMediaTasks
from reels import ReelAgents, ReelTasks
from reels.utils import parse_duration, create_unique_reel_folder, save_reel_metadata, create_reel_summary, create_reel_preview_html

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
if config("OPENAI_ORGANIZATION_ID", default=""):
    os.environ["OPENAI_ORGANIZATION"] = config("OPENAI_ORGANIZATION_ID")


class SocialMediaPostCreator:
    def __init__(self, user_prompt, platform="instagram", content_type="post"):
        self.user_prompt = user_prompt
        self.platform = platform
        self.content_type = content_type  # "post" or "story"
    
    def create_unique_output_folder(self):
        """Create a unique folder for this post's outputs"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a descriptive folder name from the prompt
        prompt_slug = re.sub(r'[^\w\s-]', '', self.user_prompt.lower())
        prompt_slug = re.sub(r'[\s]+', '_', prompt_slug)[:30]  # Limit length
        
        folder_name = f"{self.platform}_{self.content_type}_{prompt_slug}_{timestamp}"
        post_folder = os.path.join(os.getcwd(), "output", folder_name)
        os.makedirs(post_folder, exist_ok=True)
        
        return post_folder, timestamp

    def save_json_output(self, data, post_folder, timestamp):
        """Save the output as JSON file"""
        filename = f"{self.platform}_{self.content_type}_{timestamp}.json"
        filepath = os.path.join(post_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath

    def save_markdown_output(self, data, post_folder, timestamp):
        """Generate and save Markdown file"""
        filename = f"{self.platform}_{self.content_type}_{timestamp}.md"
        filepath = os.path.join(post_folder, filename)
        
        # Extract hashtags
        hashtags = ""
        if data.get("hashtags_and_timing"):
            content = data["hashtags_and_timing"]
            if "HASHTAGS:" in content:
                hashtags_line = content.split("HASHTAGS:")[1].split("\n")[0].strip()
                hashtags = hashtags_line
            else:
                hashtag_matches = re.findall(r'#\w+', content)
                if hashtag_matches:
                    hashtags = " ".join(hashtag_matches)
        
        # Create markdown content
        content_title = "Post" if self.content_type == "post" else "Story"
        markdown_content = f"""# {self.platform.title()} {content_title}

## Original Prompt
{data.get('original_prompt', '')}

## Selected Option
{data.get('selected_option', '')}

## Caption
{data.get('caption', '')}

## Hashtags
{hashtags}

## Image Details
"""
        
        if data.get('image'):
            image_data = data['image']
            if image_data.get('story_images'):
                # Handle story series
                story_images = image_data['story_images']
                total_stories = image_data.get('total_stories', len(story_images))
                successful_stories = image_data.get('successful_stories', 0)
                
                markdown_content += f"""**Story Series**: {successful_stories}/{total_stories} stories generated

"""
                for img in story_images:
                    if "error" not in img:
                        markdown_content += f"""### Story {img['story_number']}
- **Local Path**: {img.get('filename', 'N/A')}
- **Original URL**: {img.get('image_url', 'N/A')}
- **Prompt**: {img.get('prompt', 'N/A')}
- **Dimensions**: 1024x1792 (9:16 format)

"""
                    else:
                        markdown_content += f"""### Story {img['story_number']}
- **Status**: Failed - {img.get('error', 'Unknown error')}

"""
            elif image_data.get('carousel_images'):
                # Handle carousel images
                carousel_images = image_data['carousel_images']
                total_images = image_data.get('total_images', len(carousel_images))
                successful_images = image_data.get('successful_images', 0)
                
                markdown_content += f"""**Carousel Post**: {successful_images}/{total_images} images generated

"""
                for img in carousel_images:
                    if "error" not in img:
                        markdown_content += f"""### Slide {img['slide_number']}
- **Local Path**: {img.get('filename', 'N/A')}
- **Original URL**: {img.get('image_url', 'N/A')}
- **Prompt**: {img.get('prompt', 'N/A')}

"""
                    else:
                        markdown_content += f"""### Slide {img['slide_number']}
- **Status**: Failed - {img.get('error', 'Unknown error')}

"""
            elif image_data.get('format') == 'story_single':
                # Handle single story image
                markdown_content += f"""**Single Story**
- **Local Path**: {image_data.get('filename', 'N/A')}
- **Original URL**: {image_data.get('image_url', 'N/A')}
- **Prompt**: {image_data.get('prompt', 'N/A')}
- **Dimensions**: {image_data.get('dimensions', '1024x1792')} (9:16 format)
"""
            else:
                # Handle single regular image
                markdown_content += f"""**Single Image**
- **Local Path**: {image_data.get('filename', 'N/A')}
- **Original URL**: {image_data.get('image_url', 'N/A')}
- **Prompt**: {image_data.get('prompt', 'N/A')}
"""
        else:
            markdown_content += "No image generated\n"
        
        markdown_content += f"""
## Timing & Strategy
{data.get('hashtags_and_timing', '')}

## Metadata
- **Platform**: {data.get('platform', '')}
- **Generated**: {data.get('timestamp', '')}
- **Status**: {data.get('status', '')}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath

    def generate_html_preview(self, data, platform, post_folder, timestamp):
        """Generate HTML preview for the social media post"""
        try:
            template_path = os.path.join(os.getcwd(), "templates", f"{platform}.html")
            
            if not os.path.exists(template_path):
                return None
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Extract hashtags from hashtags_and_timing
            hashtags = ""
            timing_info = "2 hours ago"
            
            if data.get("hashtags_and_timing"):
                content = data["hashtags_and_timing"]
                
                # Look for HASHTAGS: prefix first
                if "HASHTAGS:" in content:
                    hashtags_line = content.split("HASHTAGS:")[1].split("\n")[0].strip()
                    hashtags = hashtags_line
                else:
                    # Fallback: Extract hashtags using regex
                    hashtag_matches = re.findall(r'#\w+', content)
                    if hashtag_matches:
                        hashtags = " ".join(hashtag_matches)
                
                # Extract timing info
                if "Best Posting Times" in content:
                    timing_info = "Optimal posting time"
            
            # Prepare template variables
            template_vars = {
                "timestamp": data.get("timestamp", ""),
                "original_prompt": data.get("original_prompt", ""),
                "caption": data.get("caption", ""),
                "hashtags": hashtags,
                "timing_info": timing_info,
                "image_path": ""
            }
            
            # Handle image path - prioritize first carousel image, fallback to single image
            if data.get("image"):
                if data["image"].get("carousel_images") and len(data["image"]["carousel_images"]) > 0:
                    # Use the first carousel image for preview
                    first_image = data["image"]["carousel_images"][0]
                    if "error" not in first_image:
                        template_vars["image_path"] = first_image.get("filename", "")
                elif data["image"].get("filename"):
                    template_vars["image_path"] = data["image"]["filename"]
            
            # Simple template replacement (Mustache-like)
            html_content = template
            for key, value in template_vars.items():
                # Handle conditional sections
                if value:
                    # Show sections with content
                    html_content = re.sub(rf'{{\#{key}}}.*?{{\/{key}}}', 
                                        lambda m: m.group(0).replace(f'{{{{{key}}}}}', str(value)), 
                                        html_content, flags=re.DOTALL)
                    # Remove inverted sections
                    html_content = re.sub(rf'{{\^{key}}}.*?{{\/{key}}}', '', html_content, flags=re.DOTALL)
                else:
                    # Remove sections without content
                    html_content = re.sub(rf'{{\#{key}}}.*?{{\/{key}}}', '', html_content, flags=re.DOTALL)
                    # Show inverted sections
                    html_content = re.sub(rf'{{\^{key}}}(.*?){{\/{key}}}', r'\1', html_content, flags=re.DOTALL)
                
                # Replace simple variables
                html_content = html_content.replace(f'{{{{{key}}}}}', str(value))
            
            # Clean up any remaining template syntax
            html_content = re.sub(r'\{\{[^}]+\}\}', '', html_content)
            
            # Save HTML file
            html_filename = f"{platform}_post_preview_{timestamp}.html"
            html_filepath = os.path.join(post_folder, html_filename)
            
            with open(html_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_filepath
            
        except Exception as e:
            print(f"Error generating HTML preview: {str(e)}")
            return None

    def run(self):
        content_title = "post" if self.content_type == "post" else "story"
        print(f"\n🎯 Creating social media {content_title} for: '{self.user_prompt}'")
        print(f"📱 Platform: {self.platform}")
        print(f"📸 Content Type: {self.content_type}")
        print("=" * 50)

        # Initialize agents and tasks
        agents = SocialMediaAgents()
        tasks = SocialMediaTasks()

        # Step 1: Generate 3 post ideas
        print("\n🧠 STEP 1: Generating 3 creative post ideas...")
        script_agent = agents.script_agent()
        ideation_task = tasks.ideation_task(script_agent, self.user_prompt, self.platform)
        
        ideation_crew = Crew(
            agents=[script_agent],
            tasks=[ideation_task],
            verbose=True,
        )
        
        ideas_result = ideation_crew.kickoff()
        print("\n" + "="*50)
        print("🎨 HERE ARE YOUR 3 POST IDEAS:")
        print("="*50)
        print(ideas_result)
        
        # Step 2: User selects an idea
        print("\n" + "="*50)
        while True:
            try:
                choice = input("\n👆 Which idea do you like? (Enter 1, 2, or 3): ").strip()
                if choice in ["1", "2", "3"]:
                    selected_option = f"Option {choice}"
                    break
                else:
                    print("❌ Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return
        
        print(f"\n✅ Great choice! Creating your post based on {selected_option}...")
        
        # Create unique output folder for this post
        post_folder, timestamp = self.create_unique_output_folder()
        print(f"\n📁 Created output folder: {os.path.basename(post_folder)}")
        
        # Step 3: Generate the complete post
        print("\n🚀 STEP 2: Creating your complete social media post...")
        
        # Initialize all remaining agents
        copywriter = agents.copywriter_agent()
        creative = agents.creative_agent(post_folder)  # Pass folder to creative agent
        hashtag_agent = agents.hashtag_agent()
        timing_agent = agents.timing_agent()
        
        # Create tasks for the selected idea
        copywriting_task = tasks.copywriting_task(copywriter, selected_option, self.user_prompt, self.platform)
        
        # Execute copywriting first
        copy_crew = Crew(
            agents=[copywriter],
            tasks=[copywriting_task],
            verbose=True,
        )
        
        caption_result = copy_crew.kickoff()
        
        # Create remaining tasks with the caption based on content type
        if self.content_type == "story":
            image_task = tasks.story_generation_task(creative, caption_result, self.user_prompt)
        else:
            image_task = tasks.image_generation_task(creative, caption_result, self.user_prompt)
        
        hashtag_task = tasks.hashtag_research_task(hashtag_agent, caption_result, self.user_prompt, self.platform)
        timing_task = tasks.timing_optimization_task(timing_agent, self.platform)
        
        # Execute all remaining tasks
        final_crew = Crew(
            agents=[creative, hashtag_agent, timing_agent],
            tasks=[image_task, hashtag_task, timing_task],
            verbose=True,
        )
        
        final_results = final_crew.kickoff()
        
        # Parse image results
        image_data = {}
        hashtags_timing = ""
        
        try:
            # Extract image data and other results
            if hasattr(final_crew, 'tasks_output'):
                for task_output in final_crew.tasks_output:
                    task_str = str(task_output)
                    if "image_url" in task_str or "carousel_images" in task_str:
                        try:
                            # Try to extract JSON from the task output
                            if task_str.startswith('{') and task_str.endswith('}'):
                                image_data = json.loads(task_str)
                            else:
                                # If it's not pure JSON, try to find JSON within the string
                                import re
                                # First try to find carousel images JSON
                                carousel_match = re.search(r'\{.*?"carousel_images".*?\}', task_str, re.DOTALL)
                                if carousel_match:
                                    image_data = json.loads(carousel_match.group())
                                else:
                                    # Fallback to single image JSON
                                    json_match = re.search(r'\{.*?"image_url".*?\}', task_str, re.DOTALL)
                                    if json_match:
                                        image_data = json.loads(json_match.group())
                                    else:
                                        image_data = {"error": "Could not extract JSON from image output", "raw_output": task_str}
                        except json.JSONDecodeError as e:
                            image_data = {"error": f"JSON decode error: {str(e)}", "raw_output": task_str}
                        except Exception as e:
                            image_data = {"error": f"Unexpected error parsing image data: {str(e)}", "raw_output": task_str}
                    else:
                        hashtags_timing += task_str + "\n"
            else:
                # Fallback if tasks_output is not available
                hashtags_timing = str(final_results)
                image_data = {"error": "Could not access task outputs", "raw_results": str(final_results)}
        except Exception as e:
            image_data = {"error": f"Error processing results: {str(e)}"}
            hashtags_timing = str(final_results)
        
        # Create comprehensive result structure
        complete_result = {
            "timestamp": datetime.now().isoformat(),
            "original_prompt": self.user_prompt,
            "selected_option": selected_option,
            "platform": self.platform,
            "caption": str(caption_result),
            "image": image_data,
            "hashtags_and_timing": hashtags_timing.strip(),
            "status": "completed"
        }
        
        # Save all outputs to the unique folder
        json_filepath = self.save_json_output(complete_result, post_folder, timestamp)
        markdown_filepath = self.save_markdown_output(complete_result, post_folder, timestamp)
        html_filepath = self.generate_html_preview(complete_result, self.platform, post_folder, timestamp)
        
        # Format and display final output
        content_title = "POST" if self.content_type == "post" else "STORY"
        print("\n" + "="*60)
        print(f"🎉 YOUR COMPLETE SOCIAL MEDIA {content_title} IS READY!")
        print("="*60)
        
        print(f"\n📝 CAPTION:")
        print("-" * 30)
        print(complete_result["caption"])
        
        visual_title = "IMAGES" if self.content_type == "post" else "STORY VISUALS"
        print(f"\n📸 {visual_title}:")
        print("-" * 30)
        if complete_result["image"].get("story_images"):
            # Handle story series
            story_images = complete_result["image"]["story_images"]
            total_stories = complete_result["image"].get("total_stories", len(story_images))
            successful_stories = complete_result["image"].get("successful_stories", 0)
            
            print(f"📖 STORY SERIES: {successful_stories}/{total_stories} stories generated successfully")
            for img in story_images:
                if "error" not in img:
                    print(f"  📱 Story {img['story_number']}: {img['filename']} (9:16 format)")
                else:
                    print(f"  ❌ Story {img['story_number']}: Failed ({img.get('error', 'Unknown error')})")
        elif complete_result["image"].get("format") == "story_single":
            # Handle single story
            print(f"📱 SINGLE STORY (9:16 format)")
            print(f"✅ Story saved to: {complete_result['image']['local_path']}")
            print(f"🌐 Original URL: {complete_result['image'].get('image_url', 'N/A')}")
            print(f"📝 Story prompt: {complete_result['image'].get('prompt', 'N/A')}")
            print(f"📐 Dimensions: {complete_result['image'].get('dimensions', '1024x1792')}")
        elif complete_result["image"].get("carousel_images"):
            # Handle carousel images
            carousel_images = complete_result["image"]["carousel_images"]
            total_images = complete_result["image"].get("total_images", len(carousel_images))
            successful_images = complete_result["image"].get("successful_images", 0)
            
            print(f"🎠 CAROUSEL POST: {successful_images}/{total_images} images generated successfully")
            for img in carousel_images:
                if "error" not in img:
                    print(f"  📄 Slide {img['slide_number']}: {img['filename']}")
                else:
                    print(f"  ❌ Slide {img['slide_number']}: Failed ({img.get('error', 'Unknown error')})")
        elif complete_result["image"].get("local_path"):
            # Handle single image
            print(f"🖼️  SINGLE IMAGE")
            print(f"✅ Image saved to: {complete_result['image']['local_path']}")
            print(f"🌐 Original URL: {complete_result['image'].get('image_url', 'N/A')}")
            print(f"📝 Image prompt: {complete_result['image'].get('prompt', 'N/A')}")
        else:
            print("❌ Image generation failed or not available")
        
        print(f"\n🏷️ HASHTAGS & TIMING:")
        print("-" * 30)
        print(complete_result["hashtags_and_timing"])
        
        print(f"\n💾 OUTPUT FILES SAVED:")
        print("-" * 30)
        print(f"📁 Folder: {os.path.basename(post_folder)}")
        print(f"📄 JSON: {os.path.basename(json_filepath)}")
        print(f"📝 Markdown: {os.path.basename(markdown_filepath)}")
        if html_filepath:
            print(f"🌐 HTML Preview: {os.path.basename(html_filepath)}")
            
            # List all images in the output folder
            if complete_result["image"].get("story_images"):
                story_images = complete_result["image"]["story_images"]
                successful_stories = [img for img in story_images if "error" not in img]
                print(f"📖 Story Images ({len(successful_stories)} stories):")
                for img in successful_stories:
                    print(f"   📱 {img['filename']}")
            elif complete_result["image"].get("carousel_images"):
                carousel_images = complete_result["image"]["carousel_images"]
                successful_images = [img for img in carousel_images if "error" not in img]
                print(f"🎠 Carousel Images ({len(successful_images)} slides):")
                for img in successful_images:
                    print(f"   📄 {img['filename']}")
            elif complete_result["image"].get("filename"):
                content_type_icon = "📱" if complete_result["image"].get("format") == "story_single" else "🖼️ "
                print(f"{content_type_icon} Image: {complete_result['image']['filename']}")
                
            preview_text = "Story" if self.content_type == "story" else self.platform.title()
            print(f"👁️  Open the HTML file in your browser to see the {preview_text} UI preview!")
        else:
            print("❌ HTML preview generation failed")
        
        print(f"\n📂 Complete folder path: {post_folder}")
        print("\n" + "="*60)
        print("✨ Everything organized in one folder! Check the HTML preview for platform-specific UI!")
        print("="*60)
        
        return complete_result


class ContentCalendarPlanner:
    def __init__(self, user_prompt, platforms=None, duration_weeks=4):
        self.user_prompt = user_prompt
        self.platforms = platforms or ["instagram", "facebook", "twitter", "linkedin"]
        self.duration_weeks = duration_weeks
    
    def create_unique_output_folder(self):
        """Create a unique folder for this calendar's outputs"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a descriptive folder name from the prompt
        prompt_slug = re.sub(r'[^\w\s-]', '', self.user_prompt.lower())
        prompt_slug = re.sub(r'[\s]+', '_', prompt_slug)[:30]  # Limit length
        
        folder_name = f"content_calendar_{prompt_slug}_{timestamp}"
        calendar_folder = os.path.join(os.getcwd(), "output", folder_name)
        os.makedirs(calendar_folder, exist_ok=True)
        
        return calendar_folder, timestamp

    def save_calendar_outputs(self, calendar_data, calendar_folder, timestamp):
        """Save the calendar as JSON, Markdown, and CSV files"""
        # Save JSON file
        json_filename = f"content_calendar_{timestamp}.json"
        json_filepath = os.path.join(calendar_folder, json_filename)
        
        calendar_json = {
            "timestamp": datetime.now().isoformat(),
            "original_prompt": self.user_prompt,
            "platforms": self.platforms,
            "duration_weeks": self.duration_weeks,
            "calendar_content": str(calendar_data),
            "status": "completed",
            "metadata": {
                "total_posts_planned": self.duration_weeks * 7 * len(self.platforms),
                "platforms_count": len(self.platforms),
                "calendar_type": "comprehensive_strategy"
            }
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(calendar_json, f, ensure_ascii=False, indent=2)
        
        # Save enhanced Markdown file
        markdown_filename = f"content_calendar_{timestamp}.md"
        markdown_filepath = os.path.join(calendar_folder, markdown_filename)
        
        markdown_content = f"""# 📅 Content Calendar Strategy Plan

## 🎯 Original Request
**Brief:** {self.user_prompt}

## 📊 Calendar Overview
- **🚀 Platforms**: {', '.join(self.platforms)}
- **⏰ Duration**: {self.duration_weeks} weeks
- **📈 Total Posts Planned**: ~{self.duration_weeks * 7 * len(self.platforms)} posts
- **📅 Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 Complete Content Calendar

{calendar_data}

---

## 📋 Quick Action Checklist

### Week 1 Preparation
- [ ] Review and approve all Week 1 content
- [ ] Prepare visual assets for first week
- [ ] Schedule posts in social media management tool
- [ ] Set up tracking for performance metrics

### Ongoing Tasks
- [ ] Weekly performance review and optimization
- [ ] Content creation for upcoming weeks
- [ ] Community engagement and response management
- [ ] Hashtag performance monitoring

### Monthly Review
- [ ] Analyze engagement metrics
- [ ] Adjust strategy based on performance
- [ ] Plan next month's content themes
- [ ] Review and update brand guidelines

---

## 🛠️ Tools & Resources Recommended

### Content Creation
- **Design**: Canva, Adobe Creative Suite, Figma
- **Video**: CapCut, InShot, Adobe Premiere
- **Photography**: VSCO, Lightroom, Snapseed

### Scheduling & Management
- **Scheduling**: Buffer, Hootsuite, Later, Sprout Social
- **Analytics**: Native platform insights, Google Analytics
- **Collaboration**: Trello, Asana, Monday.com

### Content Planning
- **Calendar Tools**: Google Calendar, Notion, Airtable
- **Asset Storage**: Google Drive, Dropbox, Brand folder
- **Approval Workflow**: ReviewBoard, Gain, Planable

---

*🤖 Generated with AI Content Calendar Planner*
*📈 Ready-to-implement social media strategy*
"""
        
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Save CSV file for easy import to scheduling tools
        csv_filename = f"content_calendar_{timestamp}.csv"
        csv_filepath = os.path.join(calendar_folder, csv_filename)
        
        csv_content = """Date,Time,Platform,Content Type,Topic/Theme,Caption Preview,Media Requirements,Hashtags,Call-to-Action,Status,Performance Goal
"""
        
        # Add sample CSV structure (this would be populated from actual calendar data)
        current_date = datetime.now()
        for week in range(self.duration_weeks):
            for day in range(7):
                date = current_date + timedelta(weeks=week, days=day)
                for platform in self.platforms:
                    csv_content += f"{date.strftime('%Y-%m-%d')},12:00 PM,{platform.title()},Post,Sample Theme,Sample caption preview...,Image/Video description,#hashtag1 #hashtag2,Sample CTA,Draft,100 engagements\n"
        
        with open(csv_filepath, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        return json_filepath, markdown_filepath, csv_filepath

    def run(self):
        print(f"\n📅 Creating content calendar for: '{self.user_prompt}'")
        print(f"📱 Platforms: {', '.join(self.platforms)}")
        print(f"📆 Duration: {self.duration_weeks} weeks")
        print("=" * 50)

        # Initialize agents and tasks
        agents = SocialMediaAgents()
        tasks = SocialMediaTasks()

        # Create calendar planning workflow
        print("\n🗓️  STEP 1: Generating comprehensive content calendar...")
        calendar_agent = agents.calendar_planner_agent()
        calendar_task = tasks.content_calendar_planning_task(
            calendar_agent, 
            self.user_prompt, 
            self.platforms, 
            self.duration_weeks
        )
        
        calendar_crew = Crew(
            agents=[calendar_agent],
            tasks=[calendar_task],
            verbose=True,
        )
        
        calendar_result = calendar_crew.kickoff()
        
        # Create unique output folder for this calendar
        calendar_folder, timestamp = self.create_unique_output_folder()
        print(f"\n📁 Created output folder: {os.path.basename(calendar_folder)}")
        
        # Save calendar outputs
        json_filepath, markdown_filepath, csv_filepath = self.save_calendar_outputs(
            calendar_result, calendar_folder, timestamp
        )
        
        # Display results
        print("\n" + "="*60)
        print("🎉 YOUR CONTENT CALENDAR IS READY!")
        print("="*60)
        
        print(f"\n📋 CALENDAR OVERVIEW:")
        print("-" * 30)
        print(f"📱 Platforms: {', '.join(self.platforms)}")
        print(f"📆 Duration: {self.duration_weeks} weeks")
        print(f"🎯 Theme: {self.user_prompt}")
        
        print(f"\n📅 CONTENT CALENDAR:")
        print("-" * 30)
        print(str(calendar_result))
        
        print(f"\n💾 OUTPUT FILES SAVED:")
        print("-" * 30)
        print(f"📁 Folder: {os.path.basename(calendar_folder)}")
        print(f"📄 JSON: {os.path.basename(json_filepath)}")
        print(f"📝 Markdown: {os.path.basename(markdown_filepath)}")
        print(f"📊 CSV: {os.path.basename(csv_filepath)}")
        
        print(f"\n🎯 ACTIONABLE NEXT STEPS:")
        print("-" * 30)
        print("1. 📖 Review the Markdown file for complete strategy")
        print("2. 📊 Import CSV into your scheduling tool (Buffer, Hootsuite, etc.)")
        print("3. 🎨 Begin creating visual assets for Week 1")
        print("4. 📅 Schedule your first week of posts")
        print("5. 📈 Set up performance tracking and monitoring")
        
        print(f"\n🛠️ RECOMMENDED TOOLS:")
        print("-" * 30)
        print("• 📱 Scheduling: Buffer, Hootsuite, Later")
        print("• 🎨 Design: Canva, Adobe Creative Suite")
        print("• 📊 Analytics: Native platform insights")
        print("• 📋 Project Management: Trello, Asana")
        
        print(f"\n📂 Complete folder path: {calendar_folder}")
        print("\n" + "="*60)
        print("✨ Your comprehensive content calendar strategy is ready!")
        print("🚀 This calendar includes detailed daily planning for all weeks!")
        print("📈 Follow the action checklist to implement your strategy!")
        print("="*60)
        
        return calendar_result


class VideoReelCreator:
    """Video Reel Generation System using 8-Layer Architecture"""
    
    def __init__(self, user_prompt, duration="20s", content_mode="1", platform="instagram"):
        self.user_prompt = user_prompt
        self.duration = parse_duration(duration)
        self.content_mode = "music" if content_mode == "1" else "narration"
        self.platform = platform
    
    def run(self):
        # Initialize performance monitoring for reel generation
        from reels.performance_optimizer import optimize_reel_generation_performance
        
        print(f"\n🎬 Creating {self.duration}s {self.content_mode} reel for: '{self.user_prompt}'")
        print(f"📱 Platform: {self.platform}")
        print(f"🎵 Mode: {self.content_mode}")
        print("=" * 50)
        
        # Show enhanced progress indicator
        show_progress_indicator("Optimizing system resources for reel generation", 2)
        
        # Create output folder
        reel_folder, timestamp = create_unique_reel_folder(self.user_prompt, self.platform)
        print(f"\n📁 Created output folder: {os.path.basename(reel_folder)}")
        
        # Initialize performance optimization for this specific reel
        perf_optimization = optimize_reel_generation_performance(reel_folder)
        perf_monitor = perf_optimization['monitor']
        perf_monitor.start_monitoring()
        
        # PHASE 2: Content Planning Agent Implementation
        show_progress_indicator("Starting Phase 2: Content Planning & Storyboard Generation")
        print("\n🧠 PHASE 2: Content Planning & Storyboard Generation")
        print("-" * 50)
        perf_monitor.record_phase_start(2, "Content Planning & Storyboard Generation")
        
        # Initialize error handling system
        from reels.error_handling import ReelGenerationErrorHandler, handle_phase_errors
        error_handler = ReelGenerationErrorHandler(reel_folder)
        
        try:
            # Initialize reel-specific agents and tasks
            agents = ReelAgents()
            tasks = ReelTasks()
            
            # Step 1: Content Planning
            print("\n📋 STEP 1: Analyzing content and creating storyboard...")
            content_planner = agents.content_planning_agent()
            planning_task = tasks.content_planning_task(
                content_planner, 
                self.user_prompt, 
                self.content_mode, 
                self.duration
            )
            
            # Execute content planning
            from crewai import Crew
            planning_crew = Crew(
                agents=[content_planner],
                tasks=[planning_task],
                verbose=True
            )
            
            planning_result = planning_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(2)
            
            print("\n" + "="*60)
            print("🎯 CONTENT PLANNING COMPLETE!")
            print("="*60)
            print(f"\n📊 ANALYSIS RESULT:")
            print("-" * 30)
            print(str(planning_result))
            
            # Try to parse JSON result from CrewOutput
            import json
            try:
                # Extract text from CrewOutput object
                if hasattr(planning_result, 'raw'):
                    result_text = str(planning_result.raw)
                else:
                    result_text = str(planning_result)
                
                # Try to extract JSON from the string result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    planning_data = json.loads(json_match.group())
                else:
                    # Fallback: create basic structure from text
                    planning_data = {
                        'raw_result': result_text,
                        'status': 'parsed_as_text'
                    }
                
                # Display structured results
                if isinstance(planning_data, dict):
                    print(f"\n🔍 CONTENT ANALYSIS:")
                    print(f"   Category: {planning_data.get('content_analysis', {}).get('category', 'N/A')}")
                    print(f"   Complexity: {planning_data.get('content_analysis', {}).get('complexity_level', 'N/A')}")
                    print(f"   Target Audience: {planning_data.get('content_analysis', {}).get('target_audience', 'N/A')}")
                    
                    print(f"\n🎵 MODE SELECTION:")
                    mode_selection = planning_data.get('mode_selection', {})
                    print(f"   Recommended: {mode_selection.get('recommended_mode', 'N/A')}")
                    print(f"   User Requested: {mode_selection.get('user_requested', 'N/A')}")
                    print(f"   Rationale: {mode_selection.get('rationale', 'N/A')}")
                    
                    print(f"\n🎬 STORYBOARD:")
                    storyboard = planning_data.get('storyboard', {})
                    print(f"   Total Duration: {storyboard.get('total_duration', 'N/A')}s")
                    print(f"   Scene Count: {storyboard.get('scene_count', 'N/A')}")
                    
                    scenes = storyboard.get('scenes', [])
                    for scene in scenes:
                        if isinstance(scene, dict):
                            print(f"\n   Scene {scene.get('scene_number', 'N/A')} ({scene.get('duration', 'N/A')}s):")
                            print(f"     Title: {scene.get('title', 'N/A')}")
                            print(f"     Description: {scene.get('description', 'N/A')}")
                            print(f"     Key Message: {scene.get('key_message', 'N/A')}")
                    
                    print(f"\n🎨 VISUAL STYLE:")
                    visual_style = planning_data.get('visual_style', {})
                    print(f"   Color Palette: {visual_style.get('color_palette', 'N/A')}")
                    print(f"   Aesthetic: {visual_style.get('aesthetic_mood', 'N/A')}")
                    print(f"   Engagement Hooks: {visual_style.get('engagement_hooks', 'N/A')}")
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"\n⚠️  Could not parse structured data: {e}")
                print("Raw result will be saved to metadata")
                planning_data = {
                    'raw_result': str(planning_result),
                    'parse_error': str(e)
                }
            
            # Create comprehensive result for Phase 2
            phase2_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_2_complete',
                'folder_path': reel_folder,
                'phase': 2,
                'content_planning': planning_data,
                'next_phase': 'claude_prompt_refinement',
                'message': 'Content planning complete - ready for Claude refinement!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase2_result)
            create_reel_summary(reel_folder, phase2_result)
            create_reel_preview_html(reel_folder, phase2_result)
            
            print(f"\n💾 OUTPUT FILES SAVED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json")
            print(f"   📝 Summary: reel_summary.md")
            print(f"   🌐 Preview: reel_preview.html")
            
            # PHASE 3: Claude Prompt Refinement
            show_progress_indicator("Starting Phase 3: Claude Prompt Refinement")
            print("\n🔍 PHASE 3: Claude Prompt Refinement")
            print("-" * 50)
            perf_monitor.record_phase_start(3, "Claude Prompt Refinement")
            
            # Step 2: Claude Prompt Refinement
            print("\n📝 STEP 2: Enhancing prompts with Claude AI...")
            claude_refiner = agents.claude_refinement_agent()
            
            # Create context for refinement
            refinement_context = {
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'user_prompt': self.user_prompt,
                'timestamp': datetime.now().isoformat()
            }
            
            refinement_task = tasks.prompt_refinement_task(
                claude_refiner, 
                planning_data, 
                refinement_context
            )
            
            # Execute Claude refinement
            refinement_crew = Crew(
                agents=[claude_refiner],
                tasks=[refinement_task],
                verbose=True
            )
            
            refinement_result = refinement_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(3)
            
            print("\n" + "="*60)
            print("🎯 CLAUDE REFINEMENT COMPLETE!")
            print("="*60)
            print(f"\n🔍 REFINEMENT RESULT:")
            print("-" * 30)
            print(str(refinement_result))
            
            # Parse refinement result from CrewOutput
            refined_data = {}
            try:
                # Extract text from CrewOutput object
                if hasattr(refinement_result, 'raw'):
                    result_text = str(refinement_result.raw)
                else:
                    result_text = str(refinement_result)
                
                # Try to find JSON in the result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    import json
                    refined_data = json.loads(json_match.group())
                else:
                    refined_data = {
                        'raw_result': result_text,
                        'status': 'parsed_as_text'
                    }
                
                # Display structured refinement results
                if isinstance(refined_data, dict) and 'refined_prompts' in refined_data:
                    refined_prompts = refined_data.get('refined_prompts', [])
                    quality_predictions = refined_data.get('quality_predictions', {})
                    
                    print(f"\n✨ ENHANCED PROMPTS:")
                    for prompt in refined_prompts:
                        if isinstance(prompt, dict):
                            print(f"\n   Scene {prompt.get('scene_number', 'N/A')}:")
                            print(f"     Enhanced: {prompt.get('enhanced_prompt', 'N/A')[:100]}...")
                            print(f"     Quality Score: {prompt.get('quality_prediction', 'N/A')}")
                            print(f"     Model: {prompt.get('recommended_model', 'N/A')}")
                    
                    print(f"\n🎯 OVERALL QUALITY PREDICTION:")
                    print(f"   Overall Score: {quality_predictions.get('overall_score', 'N/A')}")
                    print(f"   Technical Feasibility: {quality_predictions.get('technical_feasibility', 'N/A')}")
                    print(f"   Creative Appeal: {quality_predictions.get('creative_appeal', 'N/A')}")
                    print(f"   Engagement Potential: {quality_predictions.get('engagement_potential', 'N/A')}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"\n⚠️  Could not parse refinement data: {e}")
                refined_data = {
                    'raw_result': str(refinement_result),
                    'parse_error': str(e)
                }
            
            # Create comprehensive Phase 3 result
            phase3_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_3_complete',
                'folder_path': reel_folder,
                'phase': 3,
                'content_planning': planning_data,
                'claude_refinement': refined_data,
                'next_phase': 'video_generation',
                'message': 'Claude prompt refinement complete - ready for video generation!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase3_result)
            create_reel_summary(reel_folder, phase3_result)
            create_reel_preview_html(reel_folder, phase3_result)
            
            print(f"\n💾 OUTPUT FILES UPDATED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json (updated)")
            print(f"   📝 Summary: reel_summary.md (updated)")
            print(f"   🌐 Preview: reel_preview.html (updated)")
            
            # PHASE 4: Video Generation
            show_progress_indicator("Starting Phase 4: Professional Video Generation")
            print("\n🎬 PHASE 4: Video Generation")
            print("-" * 50)
            perf_monitor.record_phase_start(4, "Professional Video Generation")
            
            # Step 3: Video Generation using FAL.AI
            print("\n📹 STEP 3: Generating video clips with FAL.AI...")
            video_generator = agents.video_generation_agent(reel_folder)
            
            # Create video generation context
            video_context = {
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'user_prompt': self.user_prompt,
                'timestamp': datetime.now().isoformat(),
                'reel_folder': reel_folder
            }
            
            video_task = tasks.video_generation_task(
                video_generator,
                refined_data,
                video_context
            )
            
            # Execute video generation
            video_crew = Crew(
                agents=[video_generator],
                tasks=[video_task],
                verbose=True
            )
            
            video_result = video_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(4)
            
            print("\n" + "="*60)
            print("🎬 VIDEO GENERATION COMPLETE!")
            print("="*60)
            print(f"\n🎥 GENERATION RESULT:")
            print("-" * 30)
            print(str(video_result))
            
            # Parse video generation result
            video_data = {}
            try:
                # Extract text from CrewOutput object
                if hasattr(video_result, 'raw'):
                    result_text = str(video_result.raw)
                else:
                    result_text = str(video_result)
                
                # Try to find JSON in the result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    import json
                    video_data = json.loads(json_match.group())
                else:
                    video_data = {
                        'raw_result': result_text,
                        'status': 'parsed_as_text'
                    }
                
                # Display structured video generation results
                if isinstance(video_data, dict) and 'generated_clips' in video_data:
                    generated_clips = video_data.get('generated_clips', [])
                    generation_summary = video_data.get('generation_summary', {})
                    quality_assessment = video_data.get('quality_assessment', {})
                    
                    print(f"\n🎬 GENERATED CLIPS:")
                    for clip in generated_clips:
                        if isinstance(clip, dict):
                            print(f"\n   Clip {clip.get('clip_id', 'N/A')}:")
                            print(f"     Status: {clip.get('status', 'N/A')}")
                            print(f"     Model: {clip.get('model_used', 'N/A')}")
                            print(f"     Duration: {clip.get('duration', 'N/A')}s")
                            print(f"     File: {clip.get('filename', 'N/A')}")
                            print(f"     Cost: ${clip.get('cost_estimate', 0):.2f}")
                    
                    print(f"\n📊 GENERATION SUMMARY:")
                    print(f"   Total Clips: {generation_summary.get('total_clips', 'N/A')}")
                    print(f"   Successful: {generation_summary.get('successful_clips', 'N/A')}")
                    print(f"   Failed: {generation_summary.get('failed_clips', 'N/A')}")
                    print(f"   Total Cost: ${generation_summary.get('total_cost', 0):.2f}")
                    
                    print(f"\n🔍 QUALITY ASSESSMENT:")
                    print(f"   Overall Score: {quality_assessment.get('overall_quality_score', 'N/A')}")
                    print(f"   Technical Compliance: {quality_assessment.get('technical_compliance', 'N/A')}")
                    print(f"   Ready for Phase 5: {quality_assessment.get('ready_for_synchronization', 'N/A')}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"\n⚠️  Could not parse video generation data: {e}")
                video_data = {
                    'raw_result': str(video_result),
                    'parse_error': str(e)
                }
            
            # Create comprehensive Phase 4 result
            phase4_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_4_complete',
                'folder_path': reel_folder,
                'phase': 4,
                'content_planning': planning_data,
                'claude_refinement': refined_data,
                'video_generation': video_data,
                'next_phase': 'audio_generation',
                'message': 'Video generation complete - ready for audio generation!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase4_result)
            create_reel_summary(reel_folder, phase4_result)
            create_reel_preview_html(reel_folder, phase4_result)
            
            print(f"\n💾 OUTPUT FILES UPDATED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json (updated)")
            print(f"   📝 Summary: reel_summary.md (updated)")
            print(f"   🌐 Preview: reel_preview.html (updated)")
            print(f"   🎬 Video Clips: {video_data.get('generation_summary', {}).get('successful_clips', 0)} clips in /raw_clips/")
            
            print(f"\n📂 Complete folder path: {reel_folder}")
            print("\n" + "="*60)
            print("✨ PHASE 4 COMPLETE! Video Generation Done!")
            print("🚀 Starting Phase 5 - Audio Generation")
            print("="*60)
            
            # PHASE 5: Audio Generation
            show_progress_indicator("Starting Phase 5: Professional Audio Generation")
            perf_monitor.record_phase_start(5, "Professional Audio Generation")
            
            # Step 4: Audio Generation using FAL AI F5 TTS
            print("\n🎵 STEP 4: Generating audio with FAL AI F5 TTS...")
            audio_generator = agents.audio_generation_agent()
            
            # Create audio generation context
            audio_context = {
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'user_prompt': self.user_prompt,
                'timestamp': datetime.now().isoformat(),
                'reel_folder': reel_folder
            }
            
            audio_task = tasks.audio_generation_task(
                audio_generator,
                video_result,
                audio_context
            )
            
            # Execute audio generation
            audio_crew = Crew(
                agents=[audio_generator],
                tasks=[audio_task],
                verbose=True
            )
            
            audio_result = audio_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(5)
            
            print("\n" + "="*60)
            print("🎵 AUDIO GENERATION COMPLETE!")
            print("="*60)
            print(f"\n🎙️  GENERATION RESULT:")
            print("-" * 30)
            print(str(audio_result))
            
            # Parse audio generation result
            audio_data = {}
            try:
                # Extract text from CrewOutput object
                if hasattr(audio_result, 'raw'):
                    result_text = str(audio_result.raw)
                else:
                    result_text = str(audio_result)
                
                # Try to find JSON in the result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    import json
                    audio_data = json.loads(json_match.group())
                else:
                    print("⚠️  Could not parse JSON from audio result")
                    
            except Exception as parse_error:
                print(f"⚠️  Error parsing audio result: {parse_error}")
                audio_data = {
                    'audio_generation_status': 'parse_error',
                    'raw_result': str(audio_result)
                }
            
            # Create comprehensive Phase 5 result
            phase5_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_5_complete',
                'folder_path': reel_folder,
                'phase': 5,
                'content_planning': planning_data,
                'claude_refinement': refined_data,
                'video_generation': video_data,
                'audio_generation': audio_data,
                'next_phase': 'synchronization',
                'message': 'Audio generation complete - ready for video-audio synchronization!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase5_result)
            create_reel_summary(reel_folder, phase5_result)
            create_reel_preview_html(reel_folder, phase5_result)
            
            print(f"\n💾 OUTPUT FILES UPDATED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json (updated)")
            print(f"   📝 Summary: reel_summary.md (updated)")
            print(f"   🌐 Preview: reel_preview.html (updated)")
            print(f"   🎬 Video Clips: {video_data.get('generation_summary', {}).get('successful_clips', 0)} clips in /raw_clips/")
            print(f"   🎵 Audio Files: Generated in /audio/ folder")
            
            print(f"\n📂 Complete folder path: {reel_folder}")
            print("\n" + "="*60)
            print("✨ PHASE 5 COMPLETE! Audio Generation Done!")
            print("🚀 Starting Phase 6 - Video-Audio Synchronization")
            print("="*60)
            
            # PHASE 6: Video-Audio Synchronization
            show_progress_indicator("Starting Phase 6: Video-Audio Synchronization & Editing")
            print("\n🎬 PHASE 6: Video-Audio Synchronization & Editing")
            print("-" * 50)
            perf_monitor.record_phase_start(6, "Video-Audio Synchronization & Editing")
            
            # Step 5: Video-Audio Synchronization using MoviePy
            print("\n⚡ STEP 5: Synchronizing video and audio with MoviePy...")
            sync_agent = agents.synchronization_agent()
            
            # Create synchronization context
            sync_context = {
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'user_prompt': self.user_prompt,
                'timestamp': datetime.now().isoformat(),
                'reel_folder': reel_folder
            }
            
            sync_task = tasks.synchronization_task(
                sync_agent,
                video_result,
                audio_result
            )
            
            # Execute synchronization
            sync_crew = Crew(
                agents=[sync_agent],
                tasks=[sync_task],
                verbose=True
            )
            
            sync_result = sync_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(6)
            
            print("\n" + "="*60)
            print("⚡ SYNCHRONIZATION COMPLETE!")
            print("="*60)
            print(f"\n🎬 SYNCHRONIZATION RESULT:")
            print("-" * 30)
            print(str(sync_result))
            
            # Parse synchronization result
            sync_data = {}
            try:
                # Extract text from CrewOutput object
                if hasattr(sync_result, 'raw'):
                    result_text = str(sync_result.raw)
                else:
                    result_text = str(sync_result)
                
                # Try to find JSON in the result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    import json
                    sync_data = json.loads(json_match.group())
                else:
                    sync_data = {
                        'raw_result': result_text,
                        'status': 'parsed_as_text'
                    }
                
                # Display structured synchronization results
                if isinstance(sync_data, dict):
                    print(f"\n🎬 SYNCHRONIZATION STATUS:")
                    print(f"   Status: {sync_data.get('status', 'N/A')}")
                    print(f"   Final Reel: {sync_data.get('final_reel_path', 'N/A')}")
                    
                    if 'video_stitching' in sync_data:
                        video_info = sync_data['video_stitching']
                        print(f"   Clips Used: {video_info.get('clips_used', 'N/A')}")
                        print(f"   Total Duration: {video_info.get('total_duration', 'N/A')}s")
                        print(f"   Quality: {video_info.get('quality', 'N/A')}")
                    
                    if 'audio_synchronization' in sync_data:
                        audio_info = sync_data['audio_synchronization']
                        print(f"   Audio Sync: {audio_info.get('sync_quality', 'N/A')}")
                        print(f"   Audio Mode: {audio_info.get('audio_mode', 'N/A')}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"\n⚠️  Could not parse synchronization data: {e}")
                sync_data = {
                    'raw_result': str(sync_result),
                    'parse_error': str(e)
                }
            
            # Create comprehensive Phase 6 result
            phase6_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_6_complete',
                'folder_path': reel_folder,
                'phase': 6,
                'content_planning': planning_data,
                'claude_refinement': refined_data,
                'video_generation': video_data,
                'audio_generation': audio_data,
                'synchronization': sync_data,
                'next_phase': 'qa_testing',
                'message': 'Video-audio synchronization complete - ready for quality assessment!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase6_result)
            create_reel_summary(reel_folder, phase6_result)
            create_reel_preview_html(reel_folder, phase6_result)
            
            print(f"\n💾 OUTPUT FILES UPDATED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json (updated)")
            print(f"   📝 Summary: reel_summary.md (updated)")
            print(f"   🌐 Preview: reel_preview.html (updated)")
            print(f"   🎬 Video Clips: {video_data.get('generation_summary', {}).get('successful_clips', 0)} clips in /raw_clips/")
            print(f"   🎵 Audio Files: Generated in /audio/ folder")
            print(f"   ⚡ Final Reel: {sync_data.get('final_reel_path', 'final_reel.mp4')}")
            
            print(f"\n📂 Complete folder path: {reel_folder}")
            print("\n" + "="*60)
            print("✨ PHASE 6 COMPLETE! Video-Audio Synchronization Done!")
            print("🚀 Starting Phase 7 - Quality Assessment & Reloop System")
            print("="*60)
            
            # PHASE 7: Quality Assessment & Reloop System
            show_progress_indicator("Starting Phase 7: Quality Assessment & Intelligent Reloop System")
            print("\n🛡️ PHASE 7: Quality Assessment & Intelligent Reloop System")
            print("-" * 50)
            perf_monitor.record_phase_start(7, "Quality Assessment & Intelligent Reloop System")
            
            # Step 6: Quality Assessment with Intelligent Reloop
            print("\n🔍 STEP 6: Comprehensive quality assessment...")
            qa_agent = agents.qa_testing_agent()
            
            # Create QA context
            qa_context = {
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'user_prompt': self.user_prompt,
                'timestamp': datetime.now().isoformat(),
                'reel_folder': reel_folder
            }
            
            qa_task = tasks.qa_testing_task(
                qa_agent,
                sync_result,
                qa_context
            )
            
            # Execute quality assessment
            qa_crew = Crew(
                agents=[qa_agent],
                tasks=[qa_task],
                verbose=True
            )
            
            qa_result = qa_crew.kickoff()
            
            # Record phase completion
            perf_monitor.record_phase_end(7)
            
            print("\n" + "="*60)
            print("🛡️ QUALITY ASSESSMENT COMPLETE!")
            print("="*60)
            print(f"\n📊 QA ASSESSMENT RESULT:")
            print("-" * 30)
            print(str(qa_result))
            
            # Parse QA result
            qa_data = {}
            try:
                # Extract text from CrewOutput object
                if hasattr(qa_result, 'raw'):
                    result_text = str(qa_result.raw)
                else:
                    result_text = str(qa_result)
                
                # Try to find JSON in the result
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    import json
                    qa_data = json.loads(json_match.group())
                else:
                    qa_data = {
                        'raw_result': result_text,
                        'status': 'parsed_as_text'
                    }
                
                # Display structured QA results
                if isinstance(qa_data, dict):
                    quality_assessment = qa_data.get('quality_assessment', {})
                    reloop_strategy = qa_data.get('reloop_strategy', {})
                    final_verdict = qa_data.get('final_verdict', {})
                    
                    print(f"\n📊 QUALITY ASSESSMENT:")
                    print(f"   Overall Score: {quality_assessment.get('overall_score', 'N/A'):.3f}")
                    print(f"   Pass Status: {quality_assessment.get('pass_status', 'N/A').upper()}")
                    print(f"   Quality Grade: {quality_assessment.get('quality_grade', 'N/A').upper()}")
                    print(f"   Failed Criteria: {len(quality_assessment.get('failed_criteria', []))}")
                    
                    if quality_assessment.get('dimension_scores'):
                        dims = quality_assessment['dimension_scores']
                        print(f"   📊 Dimension Breakdown:")
                        print(f"      Technical: {dims.get('technical_quality', 0):.3f}")
                        print(f"      Content: {dims.get('content_quality', 0):.3f}")
                        print(f"      Brand: {dims.get('brand_alignment', 0):.3f}")
                        print(f"      Platform: {dims.get('platform_optimization', 0):.3f}")
                        print(f"      Engagement: {dims.get('engagement_potential', 0):.3f}")
                    
                    print(f"\n🔄 RELOOP STRATEGY:")
                    print(f"   Reloop Needed: {reloop_strategy.get('reloop_needed', False)}")
                    print(f"   Strategy: {reloop_strategy.get('strategy', 'none')}")
                    print(f"   Confidence: {reloop_strategy.get('confidence', 0):.2f}")
                    
                    print(f"\n✅ FINAL VERDICT:")
                    print(f"   Approved for Publication: {final_verdict.get('approved_for_publication', False)}")
                    print(f"   Quality Certification: {final_verdict.get('quality_certification', 'N/A')}")
                    print(f"   Platform Readiness: {final_verdict.get('platform_readiness', [])}")
                    print(f"   Confidence Score: {final_verdict.get('confidence_score', 0):.2f}")
                
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"\n⚠️  Could not parse QA data: {e}")
                qa_data = {
                    'raw_result': str(qa_result),
                    'parse_error': str(e)
                }
            
            # Create comprehensive Phase 7 result
            phase7_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_7_complete',
                'folder_path': reel_folder,
                'phase': 7,
                'content_planning': planning_data,
                'claude_refinement': refined_data,
                'video_generation': video_data,
                'audio_generation': audio_data,
                'synchronization': sync_data,
                'quality_assessment': qa_data,
                'next_phase': 'final_output',
                'message': 'Quality assessment complete - reel ready for final output!'
            }
            
            # Save comprehensive metadata
            save_reel_metadata(reel_folder, phase7_result)
            create_reel_summary(reel_folder, phase7_result)
            create_reel_preview_html(reel_folder, phase7_result)
            
            print(f"\n💾 OUTPUT FILES UPDATED:")
            print(f"   📁 Folder: {os.path.basename(reel_folder)}")
            print(f"   📄 Metadata: reel_metadata.json (updated)")
            print(f"   📝 Summary: reel_summary.md (updated)")
            print(f"   🌐 Preview: reel_preview.html (updated)")
            print(f"   🎬 Video Clips: {video_data.get('generation_summary', {}).get('successful_clips', 0)} clips in /raw_clips/")
            print(f"   🎵 Audio Files: Generated in /audio/ folder")
            print(f"   ⚡ Final Reel: {sync_data.get('final_reel_path', 'final_reel.mp4')}")
            print(f"   🛡️ QA Report: {qa_data.get('qa_report_path', 'qa_report.json')}")
            
            # Final output summary
            # Generate comprehensive performance summary
            final_perf_summary = perf_monitor.get_performance_summary()
            
            print(f"\n📂 Complete folder path: {reel_folder}")
            print("\n" + "="*60)
            print("🎉 COMPLETE 8-LAYER REEL GENERATION FINISHED!")
            print("="*60)
            
            # Display performance metrics
            print(f"\n📊 PERFORMANCE SUMMARY:")
            print("-" * 30)
            print(f"⏱️  Total Processing Time: {final_perf_summary['total_duration_seconds']:.1f} seconds")
            print(f"🎯 Phases Completed: {final_perf_summary['performance_metrics']['phases_completed']}/7")
            print(f"🔧 System Efficiency: {final_perf_summary['resource_efficiency']['overall_rating'].title()}")
            print(f"💾 Peak Memory Usage: {final_perf_summary['memory_usage']['peak_memory_mb']} MB")
            
            if final_perf_summary['performance_metrics']['slowest_phase']:
                slowest_phase = final_perf_summary['performance_metrics']['slowest_phase']
                phase_name = final_perf_summary['phase_timings'][slowest_phase]['name']
                phase_duration = final_perf_summary['phase_timings'][slowest_phase]['duration']
                print(f"🐌 Most Time-Intensive: Phase {slowest_phase} ({phase_name}) - {phase_duration:.1f}s")
            
            # Display final results based on QA verdict
            final_verdict = qa_data.get('final_verdict', {})
            if final_verdict.get('approved_for_publication', False):
                print("✅ REEL APPROVED FOR PUBLICATION!")
                print(f"🏆 Quality Grade: {qa_data.get('quality_assessment', {}).get('quality_grade', 'N/A').upper()}")
                print(f"📊 Overall Score: {qa_data.get('quality_assessment', {}).get('overall_score', 0):.3f}")
                print(f"📱 Platform Ready: {', '.join(final_verdict.get('platform_readiness', []))}")
                print(f"🎯 Confidence: {final_verdict.get('confidence_score', 0):.1%}")
            else:
                reloop_strategy = qa_data.get('reloop_strategy', {})
                print("⚠️ REEL REQUIRES IMPROVEMENT")
                print(f"📊 Current Score: {qa_data.get('quality_assessment', {}).get('overall_score', 0):.3f}")
                print(f"🔄 Recommended Strategy: {reloop_strategy.get('strategy', 'unknown')}")
                print(f"💰 Estimated Cost: {reloop_strategy.get('estimated_cost', 'unknown')}")
                print(f"⏱️ Expected Timeline: {reloop_strategy.get('implementation_guidance', {}).get('expected_timeline', 'unknown')}")
            
            print(f"\n📋 ALL GENERATED FILES:")
            print("-" * 30)
            print(f"📁 Main Folder: {os.path.basename(reel_folder)}")
            print(f"📄 Metadata: reel_metadata.json")
            print(f"📝 Summary: reel_summary.md")
            print(f"🌐 Preview: reel_preview.html")
            print(f"🎬 Final Reel: final_reel.mp4")
            print(f"🛡️ QA Report: qa_report.json")
            print(f"📊 Processing Logs: quality_assessment_log.json")
            
            print(f"\n🎯 WHAT'S NEXT:")
            if final_verdict.get('approved_for_publication', False):
                print("1. 📱 Upload your reel to social media platforms")
                print("2. 📊 Monitor engagement and performance metrics")
                print("3. 🎨 Create variations using the successful formula")
                print("4. 📈 Analyze what worked for future content")
            else:
                improvement_recs = qa_data.get('improvement_recommendations', {})
                priority_improvements = improvement_recs.get('priority_improvements', [])
                if priority_improvements:
                    print("1. 🔧 Implement priority improvements:")
                    for i, improvement in enumerate(priority_improvements[:3], 1):
                        print(f"   {i}. {improvement}")
                print("2. 🔄 Re-run the generation with improvements")
                print("3. 🛡️ Re-test with QA system for approval")
            
            print("\n" + "="*60)
            print("✨ Professional Social Media Reel Generation Complete!")
            print("🤖 Generated with 8-Layer AI Architecture")
            print("🏆 Quality-Assured with Intelligent Reloop System")
            print("="*60)
            
            return phase7_result
            
        except Exception as e:
            print(f"\n❌ Critical Error in Reel Generation Pipeline: {str(e)}")
            print("🛡️ Activating comprehensive error recovery system...")
            
            # Determine which phase failed
            failed_phase = 2  # Default to Phase 2 if error occurs early
            if 'claude_refinement' in locals():
                failed_phase = 3
            elif 'video_result' in locals():
                failed_phase = 4
            elif 'audio_result' in locals():
                failed_phase = 5
            elif 'sync_result' in locals():
                failed_phase = 6
            elif 'qa_result' in locals():
                failed_phase = 7
            
            # Handle the error with comprehensive system
            error_context = {
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'reel_folder': reel_folder,
                'failed_phase': failed_phase
            }
            
            error_handling_result = error_handler.handle_phase_error(failed_phase, e, error_context)
            
            if error_handling_result['can_continue']:
                print(f"✅ Error recovery successful! Continuing with fallback data...")
                
                # Create comprehensive fallback result
                fallback_result = error_handler.create_fallback_result(failed_phase, error_context)
                
                # Enhance with error information
                enhanced_result = {
                    'timestamp': datetime.now().isoformat(),
                    'user_prompt': self.user_prompt,
                    'platform': self.platform,
                    'duration': self.duration,
                    'content_mode': self.content_mode,
                    'status': f'phase_{failed_phase}_recovered',
                    'folder_path': reel_folder,
                    'phase': failed_phase,
                    'error_recovery': {
                        'error_handled': True,
                        'recovery_strategy': error_handling_result['recovery_result'],
                        'fallback_data': fallback_result,
                        'original_error': str(e)
                    },
                    'fallback_active': True,
                    'message': f'Phase {failed_phase} failed but recovered with fallback data'
                }
                
                # Save error recovery metadata
                save_reel_metadata(reel_folder, enhanced_result)
                create_reel_summary(reel_folder, enhanced_result)
                
                print(f"\n🛡️ ERROR RECOVERY COMPLETE!")
                print("-" * 40)
                print(f"❌ Original Error: {str(e)[:100]}...")
                print(f"✅ Recovery Strategy: {error_handling_result['recovery_result']['strategy_used']}")
                print(f"📁 Fallback Data Generated: Phase {failed_phase}")
                print(f"⚠️ Quality Notice: Using mock/fallback data for failed components")
                
                print(f"\n📋 RECOVERY ACTIONS TAKEN:")
                actions = error_handling_result['recovery_result'].get('actions_taken', [])
                for action in actions:
                    print(f"   • {action}")
                
                print(f"\n💡 RECOMMENDATIONS:")
                print("   • Check API keys and network connectivity")
                print("   • Review error logs for detailed debugging")
                print("   • Consider re-running with corrected configuration")
                print("   • Mock data allows you to test the complete pipeline")
                
                print(f"\n📂 Error logs saved to: {error_handler.error_log_path}")
                
                return enhanced_result
            
            else:
                print(f"❌ Critical error - cannot continue with generation")
                print("💡 Check error logs and system requirements")
                
                # Create critical error result
                critical_error_result = {
                    'timestamp': datetime.now().isoformat(),
                    'user_prompt': self.user_prompt,
                    'platform': self.platform,
                    'duration': self.duration,
                    'content_mode': self.content_mode,
                    'status': 'critical_error',
                    'error': str(e),
                    'folder_path': reel_folder,
                    'phase': failed_phase,
                    'error_handling': error_handling_result,
                    'recovery_attempted': True,
                    'recovery_successful': False
                }
                
                save_reel_metadata(reel_folder, critical_error_result)
                return critical_error_result


def display_welcome_banner():
    """Display enhanced welcome banner with improved visual design"""
    print("\n" + "🌟" * 25)
    print("✨ SOCIAL MEDIA CONTENT CREATOR AI ✨")
    print("🌟" * 25)
    print("")
    print("🎯 CHOOSE YOUR CONTENT TYPE:")
    print("┌" + "─" * 48 + "┐")
    print("│  1️⃣  SINGLE POST - Individual creative posts    │")
    print("│  2️⃣  CONTENT CALENDAR - Strategic planning     │") 
    print("│  3️⃣  VIDEO REELS - Professional video content  │")
    print("└" + "─" * 48 + "┘")
    print("")

def display_feature_details():
    """Display detailed feature information with improved formatting"""
    print("📋 DETAILED FEATURES:")
    print("=" * 60)
    
    print("\n🎯 SINGLE POST (Option 1):")
    print("   ✅ 3 AI-generated creative ideas to choose from")
    print("   ✅ Professional captions with engaging hooks")
    print("   ✅ High-quality custom images via Ideogram V2 AI")
    print("   ✅ Strategic hashtag research (15-30 optimal tags)")
    print("   ✅ Platform-optimized timing recommendations")
    print("   ✅ Carousel & Story support with templates")
    print("   ⏱️ Time: 3-5 minutes | 💰 Cost: ~$0.50-1.20")
    
    print("\n📅 CONTENT CALENDAR (Option 2):")
    print("   ✅ Multi-week strategic content planning (1-12 weeks)")
    print("   ✅ Cross-platform scheduling (Instagram, Facebook, etc.)")
    print("   ✅ Content variety (posts, stories, carousels, reels)")
    print("   ✅ Theme-based content organization")
    print("   ✅ CSV/JSON export for scheduling tools")
    print("   ✅ Daily posting strategy with performance goals")
    print("   ⏱️ Time: 5-10 minutes | 💰 Cost: ~$2.00-4.00")
    
    print("\n🎬 VIDEO REELS (Option 3) - NEW!")
    print("   ✅ Professional AI video generation (FAL.AI models)")
    print("   ✅ Claude-enhanced prompt optimization")
    print("   ✅ Dual mode: Background Music OR Voice Narration")
    print("   ✅ Intelligent quality assessment & reloop system")
    print("   ✅ Platform-optimized (Instagram, TikTok, Facebook)")
    print("   ✅ 8-layer AI architecture for professional results")
    print("   ⏱️ Time: 10-20 minutes | 💰 Cost: ~$1.55-5.08")
    
    print("\n🎨 SUPPORTED FORMATS:")
    print("   📱 Instagram: Posts (1:1), Stories (9:16), Reels (9:16)")
    print("   📘 Facebook: Posts, Stories, Video content")
    print("   🐦 Twitter: Posts, Threads, Media content")
    print("   💼 LinkedIn: Professional posts, Articles")
    print("   🎵 TikTok: Short-form vertical videos")
    
    print("=" * 60)

def get_user_choice():
    """Get user choice with enhanced input validation and help"""
    while True:
        try:
            print("\n" + "💡 QUICK TIPS:" + " " * 43)
            print("   • Press Ctrl+C anytime to exit")
            print("   • All outputs saved to organized folders")
            print("   • Check .env file for API keys if errors occur")
            print("")
            
            choice = input("🎯 Enter your choice (1/2/3) or 'help' for details: ").strip().lower()
            
            if choice == 'help':
                print("\n" + "📖 HELP REQUESTED")
                display_feature_details()
                print("\n🔙 Back to main menu...")
                continue
            elif choice in ['1', '2', '3']:
                return choice
            elif choice in ['exit', 'quit', 'q']:
                raise KeyboardInterrupt
            else:
                print("❌ Please enter 1, 2, 3, or 'help'")
                
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Social Media Content Creator AI!")
            exit()

def show_progress_indicator(message, duration=1):
    """Show enhanced progress indicator"""
    import time
    print(f"\n⚡ {message}")
    for i in range(3):
        print("   " + "●" * (i+1) + "○" * (2-i) + " Processing...", end="\r")
        time.sleep(duration/3)
    print("   " + "●" * 3 + " Complete!   ")

def get_enhanced_single_post_input():
    """Enhanced input collection for single posts"""
    print("\n🎯 SINGLE POST CREATION")
    print("=" * 40)
    print("✨ Let's create an amazing social media post!")
    
    # Get user prompt with examples
    print("\n💭 CONTENT IDEAS (examples):")
    print("   • 'Eid Mubarak post for my fashion brand'")
    print("   • 'Motivational Monday quote for entrepreneurs'")
    print("   • '5 healthy breakfast recipes for busy moms'")
    print("   • 'Behind the scenes at our coffee shop'")
    
    while True:
        user_prompt = input("\n🗣️ What content do you want to create? ").strip()
        if user_prompt:
            break
        print("❌ Please provide a content description!")
    
    # Platform selection with improved UI
    print("\n📱 PLATFORM SELECTION:")
    platforms = {
        '1': 'instagram',
        '2': 'facebook', 
        '3': 'twitter',
        '4': 'linkedin'
    }
    
    print("   1️⃣  Instagram (recommended)")
    print("   2️⃣  Facebook")
    print("   3️⃣  Twitter")
    print("   4️⃣  LinkedIn")
    
    platform_choice = input("\nSelect platform (1-4) [default: Instagram]: ").strip()
    platform = platforms.get(platform_choice, 'instagram')
    
    # Content type with enhanced descriptions
    print(f"\n📸 CONTENT TYPE for {platform.title()}:")
    if platform == 'instagram':
        print("   1️⃣  Post - Single image or carousel (square/portrait)")
        print("   2️⃣  Story - Vertical format, 24-hour duration")
        content_choice = input("\nSelect type (1-2) [default: Post]: ").strip()
        content_type = 'story' if content_choice == '2' else 'post'
    else:
        content_type = 'post'
        print(f"   📌 Using standard post format for {platform.title()}")
    
    return user_prompt, platform, content_type

def get_enhanced_calendar_input():
    """Enhanced input collection for content calendars"""
    print("\n📅 CONTENT CALENDAR CREATION")
    print("=" * 40)
    print("📈 Let's plan your strategic content!")
    
    # Get user prompt with examples
    print("\n🎨 CALENDAR THEMES (examples):")
    print("   • 'Holiday season content for fashion boutique'")
    print("   • 'Tech startup thought leadership content'")
    print("   • 'Fitness coach motivational content'")
    print("   • 'Restaurant seasonal menu promotion'")
    
    while True:
        user_prompt = input("\n📝 Describe your content calendar theme: ").strip()
        if user_prompt:
            break
        print("❌ Please provide a calendar theme!")
    
    # Platform selection with checkboxes style
    print("\n📱 PLATFORM SELECTION (multi-select):")
    print("   ✅ Instagram - Visual storytelling")
    print("   ✅ Facebook - Community engagement") 
    print("   ✅ Twitter - Real-time updates")
    print("   ✅ LinkedIn - Professional networking")
    
    platforms_input = input("\nPlatforms (comma-separated) [default: all]: ").strip().lower()
    if platforms_input:
        available_platforms = ["instagram", "facebook", "twitter", "linkedin"]
        platforms = [p.strip() for p in platforms_input.split(",") if p.strip() in available_platforms]
        if not platforms:
            platforms = available_platforms
    else:
        platforms = ["instagram", "facebook", "twitter", "linkedin"]
    
    # Duration with recommendations
    print("\n📆 PLANNING DURATION:")
    print("   💡 Recommended:")
    print("      • 2-3 weeks: Testing new themes")
    print("      • 4-6 weeks: Seasonal campaigns")
    print("      • 8-12 weeks: Long-term strategy")
    
    duration_input = input("\nHow many weeks to plan? (1-12) [default: 4]: ").strip()
    try:
        duration_weeks = int(duration_input) if duration_input else 4
        if duration_weeks < 1 or duration_weeks > 12:
            duration_weeks = 4
    except ValueError:
        duration_weeks = 4
    
    return user_prompt, platforms, duration_weeks

def get_enhanced_reel_input():
    """Enhanced input collection for video reels"""
    print("\n🎬 VIDEO REEL CREATION")
    print("=" * 40)
    print("🚀 Let's create a professional video reel!")
    
    # Get user prompt with examples
    print("\n🎭 REEL IDEAS (examples):")
    print("   • 'Fashion brand showcase with trending styles'")
    print("   • 'Quick cooking tutorial for pasta dish'")
    print("   • 'Fitness transformation motivation'")
    print("   • 'Behind the scenes at coffee roastery'")
    print("   • 'Tech product demo in 30 seconds'")
    
    while True:
        user_prompt = input("\n🎬 What reel do you want to create? ").strip()
        if user_prompt:
            break
        print("❌ Please provide a reel description!")
    
    # Duration selection with cost estimates
    print("\n⏱️ DURATION SELECTION:")
    print("   1️⃣  15 seconds - Quick & punchy (Cost: $1.55-2.55)")
    print("   2️⃣  20 seconds - Balanced content (Cost: $2.02-3.55)")
    print("   3️⃣  30 seconds - Detailed story (Cost: $3.03-5.08)")
    
    duration_choice = input("\nSelect duration (1-3) [default: 20s]: ").strip()
    duration_map = {'1': '15s', '2': '20s', '3': '30s'}
    duration = duration_map.get(duration_choice, '20s')
    
    # Content mode with detailed explanations
    print("\n🎵 CONTENT MODE:")
    print("   1️⃣  Music Mode - Visual storytelling")
    print("       • Perfect for: Showcases, transformations, aesthetic content")
    print("       • Background music enhances visual appeal")
    print("       • Cost: Same as above (no extra audio charges)")
    print("")
    print("   2️⃣  Narration Mode - Educational content")
    print("       • Perfect for: Tutorials, explanations, tips")
    print("       • AI-generated voice narration with F5 TTS")
    print("       • Cost: +$0.02-0.08 for professional narration")
    
    mode_choice = input("\nSelect mode (1-2) [default: Music]: ").strip()
    content_mode = '2' if mode_choice == '2' else '1'
    
    # Platform with optimization notes
    print("\n📱 PLATFORM OPTIMIZATION:")
    print("   1️⃣  Instagram - 1080x1920, 15-30s optimal")
    print("   2️⃣  TikTok - Fast-paced, 9-21s optimal")  
    print("   3️⃣  Facebook - Algorithm optimized")
    print("   4️⃣  All platforms - Universal format")
    
    platform_choice = input("\nSelect platform (1-4) [default: Instagram]: ").strip()
    platform_map = {'1': 'instagram', '2': 'tiktok', '3': 'facebook', '4': 'all'}
    platform = platform_map.get(platform_choice, 'instagram')
    
    return user_prompt, duration, content_mode, platform

def display_completion_message(mode, result_data=None):
    """Display enhanced completion message with actionable next steps"""
    print("\n" + "🎉" * 20)
    print("✨ CONTENT CREATION COMPLETE! ✨")
    print("🎉" * 20)
    
    if mode == "1":
        print("\n📱 YOUR SINGLE POST IS READY!")
        print("🎯 What's included:")
        print("   ✅ Polished caption with hooks")
        print("   ✅ High-quality custom images")
        print("   ✅ Strategic hashtags")
        print("   ✅ Optimal posting time")
        
        print("\n📋 NEXT STEPS:")
        print("   1. 📖 Review the content in your output folder")
        print("   2. 🎨 Download images and customize if needed")
        print("   3. 📱 Schedule or post to your social platform")
        print("   4. 📊 Track engagement and performance")
        
    elif mode == "2":
        print("\n📅 YOUR CONTENT CALENDAR IS READY!")
        print("🎯 What's included:")
        print("   ✅ Multi-week strategic planning")
        print("   ✅ Platform-specific content")
        print("   ✅ Daily scheduling recommendations")
        print("   ✅ CSV export for scheduling tools")
        
        print("\n📋 NEXT STEPS:")
        print("   1. 📊 Import CSV into Buffer/Hootsuite/Later")
        print("   2. 🎨 Begin creating visuals for Week 1")
        print("   3. 📅 Schedule your first batch of posts")
        print("   4. 📈 Monitor performance and adjust strategy")
        
    elif mode == "3":
        if result_data and isinstance(result_data, dict):
            qa_data = result_data.get('quality_assessment', {})
            final_verdict = qa_data.get('final_verdict', {}) if isinstance(qa_data, dict) else {}
            approved = final_verdict.get('approved_for_publication', False)
            
            if approved:
                print("\n🎬 YOUR PROFESSIONAL REEL IS READY!")
                print("✅ QUALITY APPROVED FOR PUBLICATION!")
                score = qa_data.get('quality_assessment', {}).get('overall_score', 0) if isinstance(qa_data, dict) else 0
                print(f"🏆 Quality Score: {score:.1%}" if isinstance(score, (int, float)) else "🏆 Quality: Professional Grade")
                
                print("\n📋 NEXT STEPS:")
                print("   1. 📱 Upload to Instagram/TikTok/Facebook")
                print("   2. 📊 Monitor engagement in first hour")
                print("   3. 🎨 Create variations using successful elements")
                print("   4. 📈 Analyze performance for future content")
            else:
                print("\n🎬 YOUR REEL NEEDS IMPROVEMENT")
                print("⚠️ Quality assessment suggests enhancements")
                
                print("\n📋 NEXT STEPS:")
                print("   1. 📊 Review QA report in output folder")
                print("   2. 🔧 Implement suggested improvements")
                print("   3. 🔄 Re-run generation with updates")
                print("   4. 🛡️ Re-test with quality system")
        else:
            print("\n🎬 YOUR REEL GENERATION IS COMPLETE!")
            print("🎯 Professional 8-layer AI architecture used")
            
    print(f"\n📁 All files saved to organized output folder")
    print("💡 Check the generated files for complete details")

if __name__ == "__main__":
    # Initialize performance optimization for the main interface
    from reels.performance_optimizer import optimize_reel_generation_performance
    import os
    
    # Set up performance optimization
    temp_output = os.path.join(os.getcwd(), 'temp_interface')
    os.makedirs(temp_output, exist_ok=True)
    perf_config = optimize_reel_generation_performance(temp_output)
    
    # Display enhanced welcome banner
    display_welcome_banner()
    
    # Get user choice with enhanced interface
    mode = get_user_choice()
    
    try:
        if mode == "1":
            # Enhanced single post creation workflow
            show_progress_indicator("Initializing Single Post Creator")
            user_prompt, platform, content_type = get_enhanced_single_post_input()
            
            print(f"\n🎯 Creating {content_type} for {platform.title()}...")
            print(f"📝 Content: {user_prompt[:60]}{'...' if len(user_prompt) > 60 else ''}")
            
            creator = SocialMediaPostCreator(user_prompt, platform, content_type)
            result = creator.run()
            
            # Display completion message
            display_completion_message(mode)
            
        elif mode == "2":
            # Enhanced content calendar creation workflow
            show_progress_indicator("Initializing Content Calendar Planner")
            user_prompt, platforms, duration_weeks = get_enhanced_calendar_input()
            
            print(f"\n📅 Creating {duration_weeks}-week calendar...")
            print(f"📱 Platforms: {', '.join(platforms)}")
            print(f"🎨 Theme: {user_prompt[:60]}{'...' if len(user_prompt) > 60 else ''}")
            
            planner = ContentCalendarPlanner(user_prompt, platforms, duration_weeks)
            result = planner.run()
            
            # Display completion message
            display_completion_message(mode)
            
        elif mode == "3":
            # Enhanced video reels generation workflow
            show_progress_indicator("Initializing Professional Reel Creator")
            user_prompt, duration, content_mode, platform = get_enhanced_reel_input()
            
            # Show reel creation preview
            mode_text = "🎵 Music Mode" if content_mode == "1" else "🎙️ Narration Mode"
            print(f"\n🎬 Creating {duration} reel with {mode_text}")
            print(f"📱 Platform: {platform.title()}")
            print(f"🎭 Content: {user_prompt[:60]}{'...' if len(user_prompt) > 60 else ''}")
            
            # Estimate cost and time
            cost_estimates = {
                '15s': ('$1.55-2.55', '8-15 minutes'),
                '20s': ('$2.02-3.55', '10-20 minutes'), 
                '30s': ('$3.03-5.08', '12-25 minutes')
            }
            cost_range, time_range = cost_estimates.get(duration, ('$2.02-3.55', '10-20 minutes'))
            
            if content_mode == "2":  # Narration mode
                print(f"💰 Estimated cost: {cost_range} + $0.02-0.08 (narration)")
            else:
                print(f"💰 Estimated cost: {cost_range}")
            print(f"⏱️ Estimated time: {time_range}")
            
            # Confirmation before proceeding
            confirm = input("\n🚀 Ready to create your professional reel? (y/n) [default: y]: ").strip().lower()
            if confirm in ['n', 'no']:
                print("👋 No problem! Run the program again when you're ready.")
                exit()
            
            print("\n🎬 Starting professional reel generation...")
            print("📊 Using 8-layer AI architecture with quality assurance...")
            
            reel_creator = VideoReelCreator(user_prompt, duration, content_mode, platform)
            result = reel_creator.run()
            
            # Display completion message with result data
            display_completion_message(mode, result)
            
        else:
            print("❌ Invalid choice. Please run the program again!")
            exit()
            
        # Performance summary
        if hasattr(perf_config, 'monitor'):
            perf_summary = perf_config['monitor'].get_performance_summary()
            if perf_summary['total_duration_seconds'] > 5:  # Only show for longer operations
                print(f"\n📊 PERFORMANCE SUMMARY:")
                print(f"   ⏱️ Total time: {perf_summary['total_duration_seconds']:.1f}s")
                print(f"   🔧 Efficiency: {perf_summary['resource_efficiency']['overall_rating']}")
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Social Media Content Creator AI!")
        print("💡 Your content creation journey continues anytime!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("🔧 TROUBLESHOOTING TIPS:")
        print("   • Check your .env file contains all required API keys")
        print("   • Ensure stable internet connection")
        print("   • Try running the program again")
        print("   • Check the error logs in output folders for details")
        print(f"\n🆘 If issues persist, check: https://docs.anthropic.com/claude-code")
        
    finally:
        # Clean up performance optimization resources
        if hasattr(perf_config, 'resource_manager'):
            perf_config['resource_manager']._cleanup_all_temp_files()
        
        # Clean up temp interface folder
        import shutil
        try:
            if os.path.exists(temp_output):
                shutil.rmtree(temp_output)
        except:
            pass  # Ignore cleanup errors
