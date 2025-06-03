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
        return None
    return assistant_file.read_text().strip()

def confirm_cleanup():
    """Ask user to confirm cleanup operation."""
    print("⚠️  WARNING: This will permanently delete:")
    print("   - Your study assistant")
    print("   - All uploaded files")
    print("   - Vector stores")
    print("   - The .assistant file")
    print()
    
    response = input("Are you sure you want to continue? (type 'yes' to confirm): ")
    return response.lower() == 'yes'

def delete_assistant(client, assistant_id):
    """Delete the assistant."""
    if not assistant_id:
        print("ℹ️  No assistant to delete.")
        return True
    
    try:
        # Get assistant details first
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"🔍 Found assistant: {assistant.name} ({assistant_id})")
        
        # Delete the assistant
        client.beta.assistants.delete(assistant_id)
        print("✅ Assistant deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting assistant: {e}")
        return False

def list_and_delete_files(client, assistant_id=None):
    """List and delete uploaded files."""
    try:
        # Get list of files
        files = client.files.list()
        assistant_files = []
        
        print("🔍 Scanning for uploaded files...")
        
        for file in files.data:
            # Check if file is used for assistants
            if file.purpose == "assistants":
                assistant_files.append(file)
        
        if not assistant_files:
            print("ℹ️  No assistant files found to delete.")
            return True
        
        print(f"📄 Found {len(assistant_files)} assistant files:")
        for file in assistant_files:
            print(f"   - {file.filename} (ID: {file.id}, Size: {file.bytes} bytes)")
        
        # Delete files
        deleted_count = 0
        for file in assistant_files:
            try:
                client.files.delete(file.id)
                print(f"   ✅ Deleted: {file.filename}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Failed to delete {file.filename}: {e}")
        
        print(f"✅ Deleted {deleted_count}/{len(assistant_files)} files")
        return True
        
    except Exception as e:
        print(f"❌ Error managing files: {e}")
        return False

def list_and_delete_vector_stores(client):
    """List and delete vector stores."""
    try:
        # Get list of vector stores
        vector_stores = client.beta.vector_stores.list()
        
        if not vector_stores.data:
            print("ℹ️  No vector stores found to delete.")
            return True
        
        print(f"🗃️  Found {len(vector_stores.data)} vector stores:")
        for vs in vector_stores.data:
            print(f"   - {vs.name or 'Unnamed'} (ID: {vs.id})")
        
        # Delete vector stores
        deleted_count = 0
        for vs in vector_stores.data:
            try:
                client.beta.vector_stores.delete(vs.id)
                print(f"   ✅ Deleted: {vs.name or vs.id}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Failed to delete {vs.name or vs.id}: {e}")
        
        print(f"✅ Deleted {deleted_count}/{len(vector_stores.data)} vector stores")
        return True
        
    except Exception as e:
        print(f"❌ Error managing vector stores: {e}")
        return False

def cleanup_local_files():
    """Clean up local files."""
    files_to_remove = [
        Path(".assistant"),
        Path("exam_notes.json"),
        Path("exam_notes_chat.json"),
        Path("exam_notes_assistant.json")
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   ✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Failed to remove {file_path}: {e}")
    
    if removed_count > 0:
        print(f"✅ Cleaned up {removed_count} local files")
    else:
        print("ℹ️  No local files to clean up.")

def main():
    """Main cleanup function."""
    print("🧹 Study Assistant Cleanup")
    print("=" * 50)
    
    # Ask for confirmation
    if not confirm_cleanup():
        print("❌ Cleanup cancelled by user.")
        sys.exit(0)
    
    print("\n🚀 Starting cleanup process...")
    
    # Initialize client
    try:
        client = get_client()
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Load assistant ID
    assistant_id = load_assistant_id()
    
    success = True
    
    # 1. Delete assistant
    print("\n1️⃣ Deleting assistant...")
    if not delete_assistant(client, assistant_id):
        success = False
    
    # 2. Delete files
    print("\n2️⃣ Deleting uploaded files...")
    if not list_and_delete_files(client, assistant_id):
        success = False
    
    # 3. Delete vector stores
    print("\n3️⃣ Deleting vector stores...")
    if not list_and_delete_vector_stores(client):
        success = False
    
    # 4. Clean up local files
    print("\n4️⃣ Cleaning up local files...")
    cleanup_local_files()
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("✅ Cleanup completed successfully!")
        print("💡 You can now run scripts/00_bootstrap.py to start fresh.")
    else:
        print("⚠️  Cleanup completed with some errors.")
        print("💡 Check the error messages above and try again if needed.")

if __name__ == "__main__":
    main() 