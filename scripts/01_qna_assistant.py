#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_client():
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
    assistant_file = Path(".assistant")
    if not assistant_file.exists():
        print("❌ No assistant found. Please run: python scripts/00_bootstrap.py")
        sys.exit(1)
    return assistant_file.read_text().strip()

def create_thread(client):
    try:
        thread = client.beta.threads.create()
        print(f"💬 Created new conversation thread: {thread.id}")
        return thread
    except Exception as e:
        print(f"❌ Error creating thread: {e}")
        sys.exit(1)

def ask_question(client, assistant_id, thread_id, question):
    print(f"\n❓ Question: {question}")
    print("🤔 Thinking...")
    
    try:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question
        )
        
        stream = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            stream=True
        )
        
        print("\n📝 Answer:")
        accumulated_text = ""
        
        for event in stream:
            if event.event == "thread.message.delta":
                if hasattr(event.data.delta, 'content'):
                    for content in event.data.delta.content:
                        if content.type == "text":
                            text_value = content.text.value
                            print(text_value, end="", flush=True)
                            accumulated_text += text_value
        
        print("\n")
        
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
        latest_message = messages.data[0]
        
        citations = extract_citations(latest_message)
        if citations:
            print("\n📚 Sources:")
            for i, citation in enumerate(citations, 1):
                print(f"   {i}. {citation}")
        else:
            print("\n📚 No specific sources cited in this response.")
            
        return accumulated_text, citations
        
    except Exception as e:
        print(f"❌ Error asking question: {e}")
        return None, []

def extract_citations(message):
    citations = []
    
    for content in message.content:
        if content.type == "text":
            for annotation in content.text.annotations:
                if annotation.type == "file_citation":
                    file_citation = annotation.file_citation
                    citations.append(f"File ID: {file_citation.file_id}")
                elif annotation.type == "file_path":
                    file_path = annotation.file_path
                    citations.append(f"File: {file_path.file_id}")
    
    return citations

def suggest_questions():
    return [
        "Explain the difference between a definite and an indefinite integral in one paragraph.",
        "Give me the statement of the Mean Value Theorem.",
        "What are the common derivative rules?",
        "How do you solve optimization problems using calculus?",
        "What is the Fundamental Theorem of Calculus?",
        "Explain the concept of limits and continuity.",
        "What are related rates problems and how do you solve them?",
        "What are the different integration techniques?",
    ]

def interactive_chat(client, assistant_id, thread_id):
    print("\n🎓 Welcome to the Study Q&A Assistant!")
    print("Type 'quit' to exit, 'suggestions' for test questions, or ask any study-related question.\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Happy studying!")
                break
            elif user_input.lower() in ['suggestions', 'suggest', 'help']:
                print("\n💡 Suggested test questions:")
                for i, question in enumerate(suggest_questions(), 1):
                    print(f"   {i}. {question}")
                print()
                continue
            elif not user_input:
                continue
            
            answer, citations = ask_question(client, assistant_id, thread_id, user_input)
            
            if answer:
                conversation_history.append({
                    "question": user_input,
                    "answer": answer,
                    "citations": citations
                })
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy studying!")
            break
        except Exception as e:
            print(f"\n❌ Error during chat: {e}")
            continue
    
    return conversation_history

def batch_test_questions(client, assistant_id, thread_id):
    print("\n🧪 Running batch test with suggested questions...")
    
    test_questions = suggest_questions()
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(test_questions)}")
        
        answer, citations = ask_question(client, assistant_id, thread_id, question)
        
        if answer:
            results.append({
                "question": question,
                "answer": answer,
                "citations": citations,
                "has_citations": len(citations) > 0
            })
        
        print("-" * 60)
    
    print(f"\n📊 Test Summary:")
    print(f"   Total questions: {len(test_questions)}")
    print(f"   Successful responses: {len(results)}")
    
    cited_responses = sum(1 for r in results if r["has_citations"])
    print(f"   Responses with citations: {cited_responses}/{len(results)}")
    
    if cited_responses == 0:
        print("⚠️  Warning: No responses included citations. Check if study materials are properly uploaded.")
    
    return results

def main():
    print("🚀 Study Q&A Assistant")
    print("=" * 50)
    
    client = get_client()
    assistant_id = load_assistant_id()
    
    print(f"✅ Using assistant: {assistant_id}")
    
    thread = create_thread(client)
    
    print("\nChoose mode:")
    print("1. Interactive chat")
    print("2. Batch test questions")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            conversation_history = interactive_chat(client, assistant_id, thread.id)
        elif choice == "2":
            conversation_history = batch_test_questions(client, assistant_id, thread.id)
        else:
            print("Invalid choice. Starting interactive chat...")
            conversation_history = interactive_chat(client, assistant_id, thread.id)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    
    print(f"\n📝 Session completed with {len(conversation_history)} interactions.")

if __name__ == "__main__":
    main() 