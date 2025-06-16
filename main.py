import os
import json
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
    
    def save_json_output(self, data, filename=None):
        """Save the output as JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"social_media_post_{timestamp}.json"
        
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath

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
            verbose=False,
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
        
        # Step 3: Generate the complete post
        print("\n🚀 STEP 2: Creating your complete social media post...")
        
        # Initialize all remaining agents
        copywriter = agents.copywriter_agent()
        creative = agents.creative_agent()
        hashtag_agent = agents.hashtag_agent()
        timing_agent = agents.timing_agent()
        
        # Create tasks for the selected idea
        copywriting_task = tasks.copywriting_task(copywriter, selected_option, self.user_prompt, self.platform)
        
        # Execute copywriting first
        copy_crew = Crew(
            agents=[copywriter],
            tasks=[copywriting_task],
            verbose=False,
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
            verbose=False,
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
                    if "image_url" in task_str:
                        try:
                            # Try to extract JSON from the task output
                            if task_str.startswith('{') and task_str.endswith('}'):
                                image_data = json.loads(task_str)
                            else:
                                # If it's not pure JSON, try to find JSON within the string
                                import re
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
        
        # Save JSON output
        json_filepath = self.save_json_output(complete_result)
        
        # Format and display final output
        print("\n" + "="*60)
        print("🎉 YOUR COMPLETE SOCIAL MEDIA POST IS READY!")
        print("="*60)
        
        print(f"\n📝 CAPTION:")
        print("-" * 30)
        print(complete_result["caption"])
        
        print(f"\n📸 IMAGE:")
        print("-" * 30)
        if complete_result["image"].get("local_path"):
            print(f"✅ Image saved to: {complete_result['image']['local_path']}")
            print(f"🌐 Original URL: {complete_result['image'].get('image_url', 'N/A')}")
            print(f"📝 Image prompt: {complete_result['image'].get('prompt', 'N/A')}")
        else:
            print("❌ Image generation failed or not available")
        
        print(f"\n🏷️ HASHTAGS & TIMING:")
        print("-" * 30)
        print(complete_result["hashtags_and_timing"])
        
        print(f"\n💾 JSON OUTPUT SAVED:")
        print("-" * 30)
        print(f"📄 File: {json_filepath}")
        
        print("\n" + "="*60)
        print("✨ Ready to post! Check the JSON file and image folder for all content.")
        print("="*60)
        
        return complete_result


if __name__ == "__main__":
    print("🎨 Welcome to Social Media Post Creator AI!")
    print("=" * 50)
    print("💡 Just tell me what kind of post you want, and I'll create:")
    print("   • 3 creative ideas for you to choose from")
    print("   • A polished caption")
    print("   • A custom generated image")
    print("   • Strategic hashtags")
    print("   • Optimal posting times")
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
