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
        print(f"\n🎬 Creating {self.duration}s {self.content_mode} reel for: '{self.user_prompt}'")
        print(f"📱 Platform: {self.platform}")
        print(f"🎵 Mode: {self.content_mode}")
        print("=" * 50)
        
        # Create output folder
        reel_folder, timestamp = create_unique_reel_folder(self.user_prompt, self.platform)
        print(f"\n📁 Created output folder: {os.path.basename(reel_folder)}")
        
        # PHASE 2: Content Planning Agent Implementation
        print("\n🧠 PHASE 2: Content Planning & Storyboard Generation")
        print("-" * 50)
        
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
            print("\n🔍 PHASE 3: Claude Prompt Refinement")
            print("-" * 50)
            
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
            print("\n🎬 PHASE 4: Video Generation")
            print("-" * 50)
            
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
            print("🚀 Next: Phase 6 - Video-Audio Synchronization")
            print("="*60)
            
            return phase5_result
            
        except Exception as e:
            print(f"\n❌ Error in Phase 2: {str(e)}")
            print("💡 Make sure all API keys are configured correctly")
            
            # Fallback result
            error_result = {
                'timestamp': datetime.now().isoformat(),
                'user_prompt': self.user_prompt,
                'platform': self.platform,
                'duration': self.duration,
                'content_mode': self.content_mode,
                'status': 'phase_2_error',
                'error': str(e),
                'folder_path': reel_folder,
                'phase': 2
            }
            
            save_reel_metadata(reel_folder, error_result)
            return error_result


if __name__ == "__main__":
    print("🎨 Welcome to Social Media Content Creator AI!")
    print("=" * 50)
    print("💡 Choose what you want to create:")
    print("   🎯 SINGLE POST: Create individual social media posts")
    print("   📅 CONTENT CALENDAR: Plan and organize your content strategy")
    print("   🎬 REELS GENERATION: Create professional video reels")
    print("")
    print("🎯 SINGLE POST FEATURES:")
    print("   • 3 creative ideas for you to choose from")
    print("   • A polished caption")
    print("   • Premium-quality visuals (single, carousel, or stories)")
    print("   • Strategic hashtags")
    print("   • Optimal posting times")
    print("")
    print("📅 CONTENT CALENDAR FEATURES:")
    print("   • Multi-week content planning")
    print("   • Platform-specific scheduling")
    print("   • Content type variety (posts, stories, carousels)")
    print("   • Strategic theme alignment")
    print("   • Organized output files")
    print("")
    print("🎬 REELS GENERATION FEATURES:")
    print("   • AI-powered video generation")
    print("   • Professional narration or background music")
    print("   • Claude-enhanced prompt optimization")
    print("   • Quality assessment and reloop system")
    print("   • Platform-optimized output (Instagram, TikTok, etc.)")
    print("")
    print("🎠 SUPPORTED FORMATS:")
    print("   • Carousel posts for lists (e.g., '5 ways to...', '10 tips for...')")
    print("   • Story templates with 9:16 vertical format (1080×1920px)")
    print("   • Story series for multi-part content")
    print("=" * 50)
    
    try:
        # Choose mode
        mode = input("\n🎯 What would you like to create?\n   (1) Single Post\n   (2) Content Calendar\n   (3) Video Reels\n   Enter 1, 2, or 3: ").strip()
        
        if mode == "1":
            # Single post creation workflow
            user_prompt = input("\n🗣️  What kind of social media content do you want to create?\n   (e.g., 'Eid Mubarak post for my fashion brand'): ").strip()
            
            if not user_prompt:
                print("❌ Please provide a prompt!")
                exit()
            
            platform = input("\n📱 Which platform? (instagram/facebook/twitter/linkedin) [default: instagram]: ").strip().lower()
            if not platform or platform not in ["instagram", "facebook", "twitter", "linkedin"]:
                platform = "instagram"
            
            content_type = input("\n📸 Content type? (post/story) [default: post]: ").strip().lower()
            if not content_type or content_type not in ["post", "story"]:
                content_type = "post"
            
            creator = SocialMediaPostCreator(user_prompt, platform, content_type)
            result = creator.run()
            
        elif mode == "2":
            # Content calendar creation workflow
            user_prompt = input("\n📅 What kind of content calendar do you want to create?\n   (e.g., 'Fashion brand content for holiday season', 'Tech startup social media strategy'): ").strip()
            
            if not user_prompt:
                print("❌ Please provide a prompt!")
                exit()
            
            # Platform selection
            print("\n📱 Select platforms (separate with commas):")
            print("   Available: instagram, facebook, twitter, linkedin")
            platforms_input = input("   Platforms [default: instagram,facebook,twitter,linkedin]: ").strip().lower()
            
            if platforms_input:
                platforms = [p.strip() for p in platforms_input.split(",") if p.strip() in ["instagram", "facebook", "twitter", "linkedin"]]
                if not platforms:
                    platforms = ["instagram", "facebook", "twitter", "linkedin"]
            else:
                platforms = ["instagram", "facebook", "twitter", "linkedin"]
            
            # Duration selection
            duration_input = input("\n📆 How many weeks? [default: 4]: ").strip()
            try:
                duration_weeks = int(duration_input) if duration_input else 4
                if duration_weeks < 1 or duration_weeks > 12:
                    duration_weeks = 4
            except ValueError:
                duration_weeks = 4
            
            planner = ContentCalendarPlanner(user_prompt, platforms, duration_weeks)
            result = planner.run()
            
        elif mode == "3":
            # NEW: Video reels generation workflow
            user_prompt = input("\n🎬 What kind of reel do you want to create?\n   (e.g., 'Fashion brand showcase', 'Cooking tutorial', 'Fitness motivation'): ").strip()
            
            if not user_prompt:
                print("❌ Please provide a prompt!")
                exit()
            
            duration = input("\n⏱️ Duration? (15s/20s/30s) [default: 20s]: ").strip() or "20s"
            
            content_mode = input("\n🎵 Content mode?\n   (1) Music Mode - Visual storytelling with background music\n   (2) Narration Mode - Educational with voice explanation\n   Enter 1 or 2 [default: 1]: ").strip() or "1"
            
            platform = input("\n📱 Primary platform? (instagram/tiktok/facebook/all) [default: instagram]: ").strip() or "instagram"
            
            reel_creator = VideoReelCreator(user_prompt, duration, content_mode, platform)
            result = reel_creator.run()
            
        else:
            print("❌ Please enter 1, 2, or 3!")
            exit()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Come back anytime to create amazing social media content!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("💡 Make sure you have set your OPENAI_API_KEY in the .env file!")
