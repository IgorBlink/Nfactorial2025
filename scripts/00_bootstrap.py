#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def get_client():
    """Initialize OpenAI client with API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("   Please copy .env.example to .env and add your API key.")
        sys.exit(1)
    
    org_id = os.getenv("OPENAI_ORG")
    client_kwargs = {"api_key": api_key}
    if org_id:
        client_kwargs["organization"] = org_id
    
    return OpenAI(**client_kwargs)

def load_assistant_id():
    """Load existing assistant ID from .assistant file if it exists."""
    assistant_file = Path(".assistant")
    if assistant_file.exists():
        return assistant_file.read_text().strip()
    return None

def save_assistant_id(assistant_id):
    """Save assistant ID to .assistant file for reuse."""
    assistant_file = Path(".assistant")
    assistant_file.write_text(assistant_id)
    print(f"💾 Assistant ID saved to {assistant_file}")

def create_or_update_assistant(client):
    """Create a new assistant or update existing one."""
    existing_id = load_assistant_id()
    
    assistant_config = {
        "name": "Study Q&A Assistant",
        "model": "gpt-4o-mini",
        "instructions": (
            "You are a helpful tutor. "
            "Use the knowledge in the attached files to answer questions. "
            "Cite sources where possible. "
            "Always provide clear explanations and examples when appropriate. "
            "If you're unsure about something, say so rather than guessing."
        ),
        "tools": [{"type": "file_search"}],
        "temperature": 0.7
    }
    
    try:
        if existing_id:
            try:
                assistant = client.beta.assistants.retrieve(existing_id)
                print(f"🔄 Found existing assistant: {existing_id}")
                assistant = client.beta.assistants.update(
                    assistant_id=existing_id,
                    **assistant_config
                )
                print("✅ Assistant updated successfully!")
            except Exception:
                print(f"🗑️ Previous assistant not found, creating new one...")
                assistant = client.beta.assistants.create(**assistant_config)
                save_assistant_id(assistant.id)
                print("✅ New assistant created successfully!")
        else:
            print("🆕 Creating new assistant...")
            assistant = client.beta.assistants.create(**assistant_config)
            save_assistant_id(assistant.id)
            print("✅ Assistant created successfully!")
        
        print(f"📋 Assistant Details:")
        print(f"   ID: {assistant.id}")
        print(f"   Name: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Tools: {[tool.type for tool in assistant.tools]}")
        
        return assistant
        
    except Exception as e:
        print(f"❌ Error creating/updating assistant: {e}")
        sys.exit(1)

def upload_study_materials(client):
    """Upload study materials to OpenAI for file_search."""
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return []
    
    uploaded_files = []
    supported_extensions = {'.md', '.txt', '.pdf', '.docx'}
    
    print("📚 Uploading study materials...")
    
    for file_path in data_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'rb') as file:
                    uploaded_file = client.files.create(
                        file=file,
                        purpose="assistants"
                    )
                    uploaded_files.append(uploaded_file)
                    print(f"   ✅ Uploaded: {file_path.name} (ID: {uploaded_file.id})")
            except Exception as e:
                print(f"   ❌ Failed to upload {file_path.name}: {e}")
    
    if not uploaded_files:
        print("⚠️  No study materials found to upload.")
        print(f"   Please add PDF, MD, TXT, or DOCX files to {data_dir}/")
    
    return uploaded_files

def create_vector_store_with_files(client, uploaded_files):
    if not uploaded_files:
        print("⚠️  No files to create vector store.")
        return None
    
    try:
        print("🗃️ Creating vector store...")
        
        vector_store = client.vector_stores.create(
            name="Study Materials Vector Store"
        )
        
        print(f"✅ Vector store created: {vector_store.id}")
        print(f"   Adding {len(uploaded_files)} files...")
        
        file_batch = client.vector_stores.file_batches.create_and_poll(
            vector_store_id=vector_store.id,
            file_ids=[file.id for file in uploaded_files]
        )
        
        print(f"✅ File batch status: {file_batch.status}")
        print(f"📊 Files processed: {file_batch.file_counts.completed}/{file_batch.file_counts.total}")
        
        return vector_store.id
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return None

def attach_vector_store_to_assistant(client, assistant_id, vector_store_id):
    if not vector_store_id:
        print("⚠️  No vector store to attach.")
        return False
    
    try:
        client.beta.assistants.update(
            assistant_id=assistant_id,
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        print(f"📎 Attached vector store to assistant")
        return True
        
    except Exception as e:
        print(f"❌ Error attaching vector store: {e}")
        return False

def main():
    """Main function to bootstrap the study assistant."""
    print("🚀 Study Q&A Assistant - Bootstrap")
    print("=" * 50)
    
    # Initialize client
    client = get_client()
    print("✅ OpenAI client initialized")
    
    # Create or update assistant
    assistant = create_or_update_assistant(client)
    
    # Upload study materials
    uploaded_files = upload_study_materials(client)
    
    if uploaded_files:
        vector_store_id = create_vector_store_with_files(client, uploaded_files)
        attach_success = attach_vector_store_to_assistant(client, assistant.id, vector_store_id)
        
        print("\n🎯 Next Steps:")
        if attach_success:
            print("   ✅ All files successfully attached to assistant!")
            print("   1. Run: python scripts/01_qna_assistant.py")
            print("   2. Ask questions about your study materials")
            print("   3. Generate revision notes with: python scripts/02_generate_notes.py")
        else:
            print("   ⚠️ Files uploaded but attachment failed")
            print("   1. Try running: python scripts/01_qna_assistant.py anyway")
            print("   2. Generate revision notes with: python scripts/02_generate_notes.py")
    else:
        print("\n🎯 Next Steps:")
        print("   1. Add study materials (PDF, MD, TXT, DOCX) to data/ directory")
        print("   2. Re-run this script to upload materials")
    
    print("\n💡 Tip: Use 'python scripts/99_cleanup.py' to clean up resources when done")

if __name__ == "__main__":
    main() 