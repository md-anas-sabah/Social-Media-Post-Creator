import os
import json
import re
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from decouple import config
from datetime import datetime

from textwrap import dedent
from agents import SocialMediaAgents
from tasks import SocialMediaTasks

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")
if config("OPENAI_ORGANIZATION_ID", default=""):
    os.environ["OPENAI_ORGANIZATION"] = config("OPENAI_ORGANIZATION_ID")


class SocialMediaPostCreator:
    def __init__(self, user_prompt, platform="instagram"):
        self.user_prompt = user_prompt
        self.platform = platform
    
    def create_unique_output_folder(self):
        """Create a unique folder for this post's outputs"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a descriptive folder name from the prompt
        prompt_slug = re.sub(r'[^\w\s-]', '', self.user_prompt.lower())
        prompt_slug = re.sub(r'[\s]+', '_', prompt_slug)[:30]  # Limit length
        
        folder_name = f"{self.platform}_{prompt_slug}_{timestamp}"
        post_folder = os.path.join(os.getcwd(), "output", folder_name)
        os.makedirs(post_folder, exist_ok=True)
        
        return post_folder, timestamp

    def save_json_output(self, data, post_folder, timestamp):
        """Save the output as JSON file"""
        filename = f"{self.platform}_post_{timestamp}.json"
        filepath = os.path.join(post_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath

    def save_markdown_output(self, data, post_folder, timestamp):
        """Generate and save Markdown file"""
        filename = f"{self.platform}_post_{timestamp}.md"
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
        markdown_content = f"""# {self.platform.title()} Post

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
            if image_data.get('carousel_images'):
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
            else:
                # Handle single image
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
        print(f"\n🎯 Creating social media post for: '{self.user_prompt}'")
        print(f"📱 Platform: {self.platform}")
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
        
        # Create remaining tasks with the caption
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
        print("\n" + "="*60)
        print("🎉 YOUR COMPLETE SOCIAL MEDIA POST IS READY!")
        print("="*60)
        
        print(f"\n📝 CAPTION:")
        print("-" * 30)
        print(complete_result["caption"])
        
        print(f"\n📸 IMAGES:")
        print("-" * 30)
        if complete_result["image"].get("carousel_images"):
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
            if complete_result["image"].get("carousel_images"):
                carousel_images = complete_result["image"]["carousel_images"]
                successful_images = [img for img in carousel_images if "error" not in img]
                print(f"🎠 Carousel Images ({len(successful_images)} slides):")
                for img in successful_images:
                    print(f"   📄 {img['filename']}")
            elif complete_result["image"].get("filename"):
                print(f"🖼️  Image: {complete_result['image']['filename']}")
                
            print(f"👁️  Open the HTML file in your browser to see the {self.platform.title()} UI preview!")
        else:
            print("❌ HTML preview generation failed")
        
        print(f"\n📂 Complete folder path: {post_folder}")
        print("\n" + "="*60)
        print("✨ Everything organized in one folder! Check the HTML preview for platform-specific UI!")
        print("="*60)
        
        return complete_result


if __name__ == "__main__":
    print("🎨 Welcome to Social Media Post Creator AI!")
    print("=" * 50)
    print("💡 Just tell me what kind of post you want, and I'll create:")
    print("   • 3 creative ideas for you to choose from")
    print("   • A polished caption")
    print("   • Premium-quality images (single or carousel)")
    print("   • Strategic hashtags")
    print("   • Optimal posting times")
    print("")
    print("🎠 NEW: Automatically creates carousel posts for lists!")
    print("   (e.g., '5 ways to...', '10 tips for...', step-by-step guides)")
    print("=" * 50)
    
    try:
        user_prompt = input("\n🗣️  What kind of social media post do you want to create?\n   (e.g., 'Eid Mubarak post for my fashion brand'): ").strip()
        
        if not user_prompt:
            print("❌ Please provide a prompt!")
            exit()
        
        platform = input("\n📱 Which platform? (instagram/facebook/twitter/linkedin) [default: instagram]: ").strip().lower()
        if not platform or platform not in ["instagram", "facebook", "twitter", "linkedin"]:
            platform = "instagram"
        
        creator = SocialMediaPostCreator(user_prompt, platform)
        result = creator.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Come back anytime to create amazing social media posts!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("💡 Make sure you have set your OPENAI_API_KEY in the .env file!")
