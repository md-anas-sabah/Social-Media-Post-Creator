from crewai import Agent
from textwrap import dedent
try:
    from langchain_community.llms import OpenAI, Ollama
except ImportError:
    from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI
from crewai.tools import BaseTool
from typing import Any, Type
from pydantic import BaseModel, Field
import openai
import requests
import os
from datetime import datetime
import json
import uuid


class ImageGeneratorArgs(BaseModel):
    prompt: str = Field(description="The prompt for image generation")

class ImageGeneratorTool(BaseTool):
    name: str = "generate_image"
    description: str = "Generate an image using DALL-E based on the provided prompt."
    args_schema: Type[BaseModel] = ImageGeneratorArgs
    output_folder: str = None

    def __init__(self, output_folder=None):
        super().__init__()
        self.output_folder = output_folder

    def _run(self, prompt: str) -> str:
        try:
            client = openai.OpenAI()
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download and save the image locally
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Create unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"generated_image_{timestamp}_{unique_id}.png"
                
                # Use the specific output folder if provided, otherwise use default
                if self.output_folder:
                    local_path = os.path.join(self.output_folder, filename)
                else:
                    # Fallback to default generated_images folder
                    current_dir = os.getcwd()
                    images_dir = os.path.join(current_dir, "generated_images")
                    os.makedirs(images_dir, exist_ok=True)
                    local_path = os.path.join(images_dir, filename)
                
                with open(local_path, 'wb') as f:
                    f.write(image_response.content)
                
                return json.dumps({
                    "image_url": image_url,
                    "local_path": local_path,
                    "filename": filename,
                    "prompt": prompt
                })
            else:
                return json.dumps({
                    "image_url": image_url,
                    "local_path": "Failed to download",
                    "filename": "Failed to download",
                    "prompt": prompt,
                    "error": f"Failed to download image: {image_response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "image_url": "Error",
                "local_path": "Error",
                "filename": "Error", 
                "prompt": prompt,
                "error": f"Error generating image: {str(e)}"
            })


class CarouselImageGeneratorArgs(BaseModel):
    prompts: list = Field(description="List of prompts for carousel image generation")
    
class CarouselImageGeneratorTool(BaseTool):
    name: str = "generate_carousel_images"
    description: str = "Generate multiple images for carousel posts using DALL-E based on a list of prompts."
    args_schema: Type[BaseModel] = CarouselImageGeneratorArgs
    output_folder: str = None

    def __init__(self, output_folder=None):
        super().__init__()
        self.output_folder = output_folder

    def _run(self, prompts: list) -> str:
        try:
            client = openai.OpenAI()
            carousel_images = []
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    
                    image_url = response.data[0].url
                    
                    # Download and save the image locally
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Create unique filename with carousel index
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_id = str(uuid.uuid4())[:8]
                        filename = f"carousel_slide_{i}_{timestamp}_{unique_id}.png"
                        
                        # Use the specific output folder if provided, otherwise use default
                        if self.output_folder:
                            local_path = os.path.join(self.output_folder, filename)
                        else:
                            # Fallback to default generated_images folder
                            current_dir = os.getcwd()
                            images_dir = os.path.join(current_dir, "generated_images")
                            os.makedirs(images_dir, exist_ok=True)
                            local_path = os.path.join(images_dir, filename)
                        
                        with open(local_path, 'wb') as f:
                            f.write(image_response.content)
                        
                        carousel_images.append({
                            "slide_number": i,
                            "image_url": image_url,
                            "local_path": local_path,
                            "filename": filename,
                            "prompt": prompt
                        })
                    else:
                        carousel_images.append({
                            "slide_number": i,
                            "image_url": image_url,
                            "local_path": "Failed to download",
                            "filename": "Failed to download",
                            "prompt": prompt,
                            "error": f"Failed to download image: {image_response.status_code}"
                        })
                        
                except Exception as e:
                    carousel_images.append({
                        "slide_number": i,
                        "image_url": "Error",
                        "local_path": "Error",
                        "filename": "Error",
                        "prompt": prompt,
                        "error": f"Error generating image {i}: {str(e)}"
                    })
            
            return json.dumps({
                "carousel_images": carousel_images,
                "total_images": len(carousel_images),
                "successful_images": len([img for img in carousel_images if "error" not in img])
            })
                
        except Exception as e:
            return json.dumps({
                "carousel_images": [],
                "total_images": 0,
                "successful_images": 0,
                "error": f"Error generating carousel images: {str(e)}"
            })


class StoryImageGeneratorArgs(BaseModel):
    prompt: str = Field(description="The prompt for story image generation")

class StoryImageGeneratorTool(BaseTool):
    name: str = "generate_story_image"
    description: str = "Generate a single vertical story image (9:16 format) using DALL-E based on the provided prompt."
    args_schema: Type[BaseModel] = StoryImageGeneratorArgs
    output_folder: str = None

    def __init__(self, output_folder=None):
        super().__init__()
        self.output_folder = output_folder

    def _run(self, prompt: str) -> str:
        try:
            client = openai.OpenAI()
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # 9:16 aspect ratio (closest available size)
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download and save the image locally
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Create unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"story_image_{timestamp}_{unique_id}.png"
                
                # Use the specific output folder if provided, otherwise use default
                if self.output_folder:
                    local_path = os.path.join(self.output_folder, filename)
                else:
                    # Fallback to default generated_images folder
                    current_dir = os.getcwd()
                    images_dir = os.path.join(current_dir, "generated_images")
                    os.makedirs(images_dir, exist_ok=True)
                    local_path = os.path.join(images_dir, filename)
                
                with open(local_path, 'wb') as f:
                    f.write(image_response.content)
                
                return json.dumps({
                    "image_url": image_url,
                    "local_path": local_path,
                    "filename": filename,
                    "prompt": prompt,
                    "format": "story_single",
                    "dimensions": "1024x1792"
                })
            else:
                return json.dumps({
                    "image_url": image_url,
                    "local_path": "Failed to download",
                    "filename": "Failed to download",
                    "prompt": prompt,
                    "format": "story_single",
                    "error": f"Failed to download image: {image_response.status_code}"
                })
                
        except Exception as e:
            return json.dumps({
                "image_url": "Error",
                "local_path": "Error",
                "filename": "Error", 
                "prompt": prompt,
                "format": "story_single",
                "error": f"Error generating story image: {str(e)}"
            })


class StorySeriesGeneratorArgs(BaseModel):
    prompts: list = Field(description="List of prompts for story series generation")
    
class StorySeriesGeneratorTool(BaseTool):
    name: str = "generate_story_series"
    description: str = "Generate multiple vertical story images (9:16 format) for story series using DALL-E based on a list of prompts."
    args_schema: Type[BaseModel] = StorySeriesGeneratorArgs
    output_folder: str = None

    def __init__(self, output_folder=None):
        super().__init__()
        self.output_folder = output_folder

    def _run(self, prompts: list) -> str:
        try:
            client = openai.OpenAI()
            story_images = []
            
            for i, prompt in enumerate(prompts, 1):
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1792",  # 9:16 aspect ratio (closest available size)
                        quality="standard",
                        n=1,
                    )
                    
                    image_url = response.data[0].url
                    
                    # Download and save the image locally
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        # Create unique filename with story index
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_id = str(uuid.uuid4())[:8]
                        filename = f"story_{i}_{timestamp}_{unique_id}.png"
                        
                        # Use the specific output folder if provided, otherwise use default
                        if self.output_folder:
                            local_path = os.path.join(self.output_folder, filename)
                        else:
                            # Fallback to default generated_images folder
                            current_dir = os.getcwd()
                            images_dir = os.path.join(current_dir, "generated_images")
                            os.makedirs(images_dir, exist_ok=True)
                            local_path = os.path.join(images_dir, filename)
                        
                        with open(local_path, 'wb') as f:
                            f.write(image_response.content)
                        
                        story_images.append({
                            "story_number": i,
                            "image_url": image_url,
                            "local_path": local_path,
                            "filename": filename,
                            "prompt": prompt
                        })
                    else:
                        story_images.append({
                            "story_number": i,
                            "image_url": image_url,
                            "local_path": "Failed to download",
                            "filename": "Failed to download",
                            "prompt": prompt,
                            "error": f"Failed to download image: {image_response.status_code}"
                        })
                        
                except Exception as e:
                    story_images.append({
                        "story_number": i,
                        "image_url": "Error",
                        "local_path": "Error",
                        "filename": "Error",
                        "prompt": prompt,
                        "error": f"Error generating story image {i}: {str(e)}"
                    })
            
            return json.dumps({
                "story_images": story_images,
                "total_stories": len(story_images),
                "successful_stories": len([img for img in story_images if "error" not in img]),
                "format": "story_series",
                "dimensions": "1024x1792"
            })
                
        except Exception as e:
            return json.dumps({
                "story_images": [],
                "total_stories": 0,
                "successful_stories": 0,
                "format": "story_series",
                "error": f"Error generating story series: {str(e)}"
            })

class TimingArgs(BaseModel):
    platform: str = Field(default="instagram", description="Social media platform")

class TimingTool(BaseTool):
    name: str = "get_optimal_posting_time"
    description: str = "Get optimal posting times for different social media platforms."
    args_schema: Type[BaseModel] = TimingArgs

    def _run(self, platform: str = "instagram") -> str:
        times = {
            "instagram": "6:00 PM - 9:00 PM (weekdays), 10:00 AM - 1:00 PM (weekends)",
            "facebook": "1:00 PM - 4:00 PM (weekdays), 12:00 PM - 2:00 PM (weekends)", 
            "twitter": "8:00 AM - 10:00 AM and 7:00 PM - 9:00 PM",
            "linkedin": "8:00 AM - 10:00 AM and 5:00 PM - 6:00 PM (Tuesday-Thursday)"
        }
        return times.get(platform.lower(), "6:00 PM - 9:00 PM (general recommendation)")


class SocialMediaAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)
        self.creative_llm = ChatOpenAI(model_name="gpt-4", temperature=0.9)

    def script_agent(self):
        return Agent(
            role="Social Media Content Strategist",
            backstory=dedent("""You are an expert social media strategist with 10+ years of experience 
                            creating viral content across all platforms. You understand what makes content 
                            engaging, shareable, and conversion-focused."""),
            goal=dedent("""Generate 3 creative and engaging social media post ideas based on user prompts. 
                       Each idea should have a clear hook, be platform-appropriate, and align with the 
                       brand's voice and objectives."""),
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )

    def copywriter_agent(self):
        return Agent(
            role="Expert Social Media Copywriter",
            backstory=dedent("""You are a master copywriter specializing in social media content. 
                            You know how to craft compelling captions that drive engagement, conversions, 
                            and brand awareness. You understand platform-specific best practices."""),
            goal=dedent("""Transform selected content ideas into polished, engaging social media captions 
                       that are optimized for the target platform and audience."""),
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT4,
        )

    def creative_agent(self, output_folder=None):
        return Agent(
            role="Visual Content Creator",
            backstory=dedent("""You are a creative visual artist and prompt engineer who specializes 
                            in creating stunning social media visuals. You understand color theory, 
                            composition, and what makes images perform well on social platforms. You excel 
                            at creating single images, cohesive carousel designs, and engaging vertical 
                            Story content optimized for mobile viewing."""),
            goal=dedent("""Generate detailed, creative prompts for AI image generation that will result 
                       in visually striking images perfectly suited for social media posts. For carousel 
                       posts, create consistent, premium-quality designs across multiple slides. For 
                       Story content, create mobile-optimized vertical visuals that work perfectly 
                       in the 9:16 format."""),
            tools=[ImageGeneratorTool(output_folder), CarouselImageGeneratorTool(output_folder), 
                   StoryImageGeneratorTool(output_folder), StorySeriesGeneratorTool(output_folder)],
            allow_delegation=False,
            verbose=True,
            llm=self.creative_llm,
        )

    def hashtag_agent(self):
        return Agent(
            role="Hashtag Research Specialist",
            backstory=dedent("""You are a social media growth expert who understands hashtag strategies, 
                            trending topics, and how to maximize reach and engagement through strategic 
                            hashtag usage."""),
            goal=dedent("""Research and provide relevant, trending hashtags that will maximize the reach 
                       and engagement of social media posts while staying relevant to the content."""),
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def timing_agent(self):
        return Agent(
            role="Social Media Timing Optimizer",
            backstory=dedent("""You are a data-driven social media analyst who understands audience 
                            behavior patterns, optimal posting times, and platform algorithms."""),
            goal=dedent("""Provide optimal posting times and platform-specific recommendations to 
                       maximize reach and engagement."""),
            tools=[TimingTool()],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )
