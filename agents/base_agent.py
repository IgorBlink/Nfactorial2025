

import json
import logging
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.a2a_client import A2AMessage, A2ATask, TaskState, MessageRole

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class BaseA2AAgent(ABC):
   
    
    def __init__(self, name: str, description: str, port: int, version: str = "1.0.0"):
        
        self.name = name
        self.description = description
        self.port = port
        self.version = version
        self.url = f"http://localhost:{port}"
        
        # Create Flask app
        self.app = Flask(f"{name}Agent")
        self.setup_routes()
        
        # Agent card
        self.agent_card = Config.get_agent_card_template(
            name=name,
            description=description,
            url=self.url,
            version=version
        )
        
        logger.info(f"Initialized {name} agent on port {port}")
    
    def setup_routes(self):
      
        
        @self.app.route("/.well-known/agent.json", methods=["GET"])
        def get_agent_card():

            return jsonify(self.agent_card)
        
        @self.app.route("/tasks/send", methods=["POST"])
        def handle_task():

            try:
                task_data = request.get_json()
                if not task_data:
                    return jsonify({"error": "No JSON data provided"}), 400
                
                # Parse task
                task = self.parse_task(task_data)
                
                # Process task
                response_task = self.process_task(task)
                
                # Return response
                return jsonify(response_task.to_dict())
                
            except Exception as e:
                logger.error(f"Error handling task: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
       
            return jsonify({
                "status": "healthy",
                "agent": self.name,
                "version": self.version
            })
    
    def parse_task(self, task_data: Dict[str, Any]) -> A2ATask:
       
        try:
            # Parse message
            msg_data = task_data.get("message", {})
            message = A2AMessage(
                role=MessageRole(msg_data.get("role", "user")),
                parts=msg_data.get("parts", []),
                message_id=msg_data.get("message_id"),
                conversation_id=msg_data.get("conversation_id"),
                parent_message_id=msg_data.get("parent_message_id")
            )
            
            # Create task
            task = A2ATask(
                id=task_data.get("id"),
                message=message,
                status=task_data.get("status", {"state": TaskState.SUBMITTED.value}),
                messages=task_data.get("messages", []),
                artifacts=task_data.get("artifacts", [])
            )
            
            return task
            
        except Exception as e:
            logger.error(f"Error parsing task: {e}")
            raise ValueError(f"Invalid task format: {e}")
    
    @abstractmethod
    def process_task(self, task: A2ATask) -> A2ATask:
        
        pass
    
    def extract_text_from_message(self, message: A2AMessage) -> str:
        
        text_parts = []
        for part in message.parts:
            if part.get("type") == "text" and "text" in part:
                text_parts.append(part["text"])
        
        return " ".join(text_parts).strip()
    
    def create_text_response(self, text: str, task: A2ATask) -> A2ATask:
       
        # Create agent response message
        response_message = A2AMessage.create_text_message(text, MessageRole.AGENT)
        response_message.conversation_id = task.message.conversation_id
        response_message.parent_message_id = task.message.message_id
        
        # Update task
        task.status = {"state": TaskState.COMPLETED.value}
        task.messages = [task.message, response_message]
        
        return task
    
    def create_error_response(self, error_message: str, task: A2ATask) -> A2ATask:
        
        task.status = {
            "state": TaskState.FAILED.value,
            "error": error_message
        }
        
        # Create error message
        error_msg = A2AMessage.create_text_message(
            f"Error: {error_message}", 
            MessageRole.AGENT
        )
        error_msg.conversation_id = task.message.conversation_id
        error_msg.parent_message_id = task.message.message_id
        
        task.messages = [task.message, error_msg]
        
        return task
    
    def run(self, host: str = "0.0.0.0", debug: bool = False):
       
        logger.info(f"Starting {self.name} agent server on {host}:{self.port}")
        logger.info(f"Agent card available at: {self.url}/.well-known/agent.json")
        logger.info(f"Task endpoint: {self.url}/tasks/send")
        
        try:
            self.app.run(host=host, port=self.port, debug=debug)
        except KeyboardInterrupt:
            logger.info(f"Shutting down {self.name} agent")
        except Exception as e:
            logger.error(f"Error running {self.name} agent: {e}")
            raise