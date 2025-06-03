#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

# Load environment variables
load_dotenv()

# Pydantic schema for study notes
class Note(BaseModel):
    """Individual study note with structured fields."""
    id: int = Field(..., ge=1, le=10, description="Unique note ID from 1 to 10")
    heading: str = Field(..., min_length=5, max_length=100, description="Concise note title")
    summary: str = Field(..., max_length=150, description="Brief explanation or definition")
    page_ref: Optional[int] = Field(None, description="Page number in source material if available")
    topic_area: str = Field(..., description="Subject area (e.g., Derivatives, Integrals, Limits)")
    difficulty: str = Field(..., description="Difficulty level: Basic, Intermediate, or Advanced")

class StudyNotesResponse(BaseModel):
    """Container for the complete set of study notes."""
    notes: List[Note] = Field(..., min_items=10, max_items=10, description="Exactly 10 study notes")
    total_count: int = Field(10, description="Total number of notes (must be 10)")
    subject: str = Field(..., description="Subject area covered by these notes")

def get_client():
    """Initialize OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        sys.exit(1)
    
    org_id = os.getenv("OPENAI_ORG")
    client_kwargs = {"api_key": api_key}
    if org_id:
        client_kwargs["organization"] = org_id
    
    return OpenAI(**client_kwargs)

def load_assistant_id():
    """Load assistant ID from .assistant file."""
    assistant_file = Path(".assistant")
    if not assistant_file.exists():
        print("❌ No assistant found. Please run: python scripts/00_bootstrap.py")
        sys.exit(1)
    return assistant_file.read_text().strip()

def generate_notes_with_assistant(client, assistant_id):
    """Generate notes using the assistant with file_search capabilities."""
    print("🔍 Generating notes using Assistant API with file_search...")
    
    try:
        # Create thread for note generation
        thread = client.beta.threads.create(
            messages=[{
                "role": "user", 
                "content": """Create exactly 10 unique study notes from the uploaded materials that will help prepare for an exam. 

Return the response as a JSON object with the following structure:
{
  "notes": [
    {
      "id": 1,
      "heading": "Mean Value Theorem",
      "summary": "Brief explanation here (max 150 chars)",
      "page_ref": null,
      "topic_area": "Calculus Theorems", 
      "difficulty": "Intermediate"
    }
  ],
  "total_count": 10,
  "subject": "Calculus"
}

Make sure:
- Each note has a unique ID from 1 to 10
- Summaries are concise but informative (max 150 characters)
- Cover different topic areas from the materials
- Include a mix of difficulty levels
- Use clear, exam-focused headings"""
            }]
        )
        
        # Run with JSON mode
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            response_format={"type": "json_object"},
            instructions="Always respond with valid JSON matching the requested schema. Focus on the most important exam topics."
        )
        
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id, limit=1)
            response_content = messages.data[0].content[0].text.value
            
            print("✅ Raw JSON response received")
            return response_content
        else:
            print(f"❌ Run failed with status: {run.status}")
            if run.last_error:
                print(f"   Error: {run.last_error}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating notes with assistant: {e}")
        return None

def generate_notes_with_chat_completion(client):
    """Generate notes using Chat Completions API in JSON mode."""
    print("💬 Generating notes using Chat Completions API...")
    
    system_prompt = """You are a study summarizer that creates concise exam revision notes.
Return exactly 10 unique notes that will help prepare for a calculus exam.
Respond *only* with valid JSON matching this exact schema:

{
  "notes": [
    {
      "id": 1,
      "heading": "Concept Name",
      "summary": "Brief explanation (max 150 chars)",
      "page_ref": null,
      "topic_area": "Subject Area",
      "difficulty": "Basic/Intermediate/Advanced"
    }
  ],
  "total_count": 10,
  "subject": "Calculus"
}"""

    user_prompt = """Create 10 revision notes covering key calculus concepts:
- Limits and continuity
- Derivatives and rules
- Integration techniques  
- Important theorems (Mean Value, Fundamental Theorem)
- Applications and problem-solving

Make each note exam-focused and concise."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error generating notes with chat completion: {e}")
        return None

def validate_and_parse_notes(json_content):
    """Validate JSON response against Pydantic schema."""
    if not json_content:
        return None
    
    try:
        # Parse JSON
        data = json.loads(json_content)
        print("✅ Valid JSON parsed successfully")
        
        # Validate with Pydantic
        study_notes = StudyNotesResponse(**data)
        print("✅ Pydantic schema validation successful!")
        
        return study_notes
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return None
    except ValidationError as e:
        print(f"❌ Pydantic validation failed:")
        for error in e.errors():
            print(f"   - {error['loc']}: {error['msg']}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during validation: {e}")
        return None

def display_notes(study_notes):
    """Display notes in a formatted, readable way."""
    print(f"\n📚 {study_notes.subject} Study Notes")
    print("=" * 60)
    print(f"Total Notes: {study_notes.total_count}")
    print()
    
    # Group by topic area
    topics = {}
    for note in study_notes.notes:
        if note.topic_area not in topics:
            topics[note.topic_area] = []
        topics[note.topic_area].append(note)
    
    for topic, notes in topics.items():
        print(f"📖 {topic}")
        print("-" * len(topic))
        
        for note in notes:
            difficulty_emoji = {
                "Basic": "🟢",
                "Intermediate": "🟡", 
                "Advanced": "🔴"
            }.get(note.difficulty, "⚪")
            
            page_info = f" (p.{note.page_ref})" if note.page_ref else ""
            
            print(f"   {note.id:2d}. {note.heading}{page_info}")
            print(f"       {difficulty_emoji} {note.summary}")
        print()

def save_notes_to_file(study_notes, filename="exam_notes.json"):
    """Save notes to JSON file."""
    try:
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            # Convert to dict and format nicely
            json.dump(study_notes.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"💾 Notes saved to: {output_path.absolute()}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error saving notes: {e}")
        return None

def compare_generation_methods(client, assistant_id):
    """Compare assistant vs chat completion methods."""
    print("🔬 Comparing generation methods...")
    print("=" * 60)
    
    results = {}
    
    # Method 1: Assistant API
    print("\n1️⃣ Method 1: Assistant API with file_search")
    assistant_json = generate_notes_with_assistant(client, assistant_id)
    if assistant_json:
        assistant_notes = validate_and_parse_notes(assistant_json)
        results["assistant"] = assistant_notes
    
    # Method 2: Chat Completions
    print("\n2️⃣ Method 2: Chat Completions API")
    chat_json = generate_notes_with_chat_completion(client)
    if chat_json:
        chat_notes = validate_and_parse_notes(chat_json)
        results["chat"] = chat_notes
    
    # Display comparison
    print("\n📊 Comparison Results:")
    print("-" * 30)
    
    if "assistant" in results and results["assistant"]:
        print("✅ Assistant API: Success")
        print(f"   - Uses uploaded study materials")
        print(f"   - May include file citations")
        print(f"   - Generated {len(results['assistant'].notes)} notes")
    else:
        print("❌ Assistant API: Failed")
    
    if "chat" in results and results["chat"]:
        print("✅ Chat Completions: Success") 
        print(f"   - Uses model's training knowledge")
        print(f"   - No file access")
        print(f"   - Generated {len(results['chat'].notes)} notes")
    else:
        print("❌ Chat Completions: Failed")
    
    return results

def main():
    """Main function for note generation."""
    print("🚀 Study Notes Generator")
    print("=" * 50)
    
    # Initialize client
    client = get_client()
    
    # Choose generation method
    print("\nChoose generation method:")
    print("1. Assistant API (uses uploaded study materials)")
    print("2. Chat Completions API (uses model knowledge)")
    print("3. Compare both methods")
    
    try:
        choice = input("Enter choice (1, 2, or 3): ").strip()
        
        if choice in ["1", "3"]:
            assistant_id = load_assistant_id()
            print(f"✅ Using assistant: {assistant_id}")
        
        if choice == "1":
            # Assistant method only
            json_content = generate_notes_with_assistant(client, assistant_id)
            study_notes = validate_and_parse_notes(json_content)
            
            if study_notes:
                display_notes(study_notes)
                save_notes_to_file(study_notes)
            
        elif choice == "2":
            # Chat completions only
            json_content = generate_notes_with_chat_completion(client)
            study_notes = validate_and_parse_notes(json_content)
            
            if study_notes:
                display_notes(study_notes)
                save_notes_to_file(study_notes, "exam_notes_chat.json")
                
        elif choice == "3":
            # Compare both methods
            results = compare_generation_methods(client, assistant_id)
            
            for method, notes in results.items():
                if notes:
                    print(f"\n📋 {method.title()} Method Results:")
                    display_notes(notes)
                    save_notes_to_file(notes, f"exam_notes_{method}.json")
        else:
            print("Invalid choice. Using Assistant API...")
            assistant_id = load_assistant_id()
            json_content = generate_notes_with_assistant(client, assistant_id)
            study_notes = validate_and_parse_notes(json_content)
            
            if study_notes:
                display_notes(study_notes)
                save_notes_to_file(study_notes)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 