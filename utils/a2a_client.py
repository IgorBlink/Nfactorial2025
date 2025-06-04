

import json
import uuid
import requests
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

from .config import Config

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class TaskState(Enum):

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(Enum):

    USER = "user"
    AGENT = "agent"


@dataclass
class A2AMessage:
    
    role: MessageRole
    parts: List[Dict[str, Any]]
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    @classmethod
    def create_text_message(cls, text: str, role: MessageRole = MessageRole.USER) -> 'A2AMessage':
       
        return cls(
            role=role,
            parts=[{"type": "text", "text": text}]
        )
    
    def to_dict(self) -> Dict[str, Any]:
       
        return {
            "role": self.role.value,
            "parts": self.parts,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id
        }


@dataclass
class A2ATask:
  
    id: str
    message: A2AMessage
    status: Dict[str, Any]
    messages: Optional[List[A2AMessage]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        if not self.messages:
            self.messages = []
    
    @classmethod
    def create(cls, message: A2AMessage, task_id: Optional[str] = None) -> 'A2ATask':
        
        if not task_id:
            task_id = str(uuid.uuid4())
        
        return cls(
            id=task_id,
            message=message,
            status={"state": TaskState.SUBMITTED.value}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            "id": self.id,
            "message": self.message.to_dict(),
            "status": self.status,
            "messages": [msg.to_dict() for msg in self.messages] if self.messages else [],
            "artifacts": self.artifacts or []
        }


class A2AClient:
    
    
    def __init__(self, base_url: str):
       
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = Config.A2A_TIMEOUT
    
    def get_agent_card(self) -> Dict[str, Any]:
       
        try:
            response = self.session.get(f"{self.base_url}/.well-known/agent.json")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get agent card from {self.base_url}: {e}")
            raise
    
    def send_task(self, task: A2ATask) -> A2ATask:
       
        url = f"{self.base_url}/tasks/send"
        
        try:
            response = self.session.post(
                url,
                json=task.to_dict(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            response_data = response.json()
            
            # Update task with response
            task.status = response_data.get("status", task.status)
            task.artifacts = response_data.get("artifacts", task.artifacts)
            
            # Update messages
            if "messages" in response_data:
                task.messages = []
                for msg_data in response_data["messages"]:
                    message = A2AMessage(
                        role=MessageRole(msg_data["role"]),
                        parts=msg_data["parts"],
                        message_id=msg_data.get("message_id"),
                        conversation_id=msg_data.get("conversation_id"),
                        parent_message_id=msg_data.get("parent_message_id")
                    )
                    task.messages.append(message)
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to send task to {url}: {e}")
            raise
    
    def ask(self, text: str, conversation_id: Optional[str] = None) -> str:
        
        message = A2AMessage.create_text_message(text)
        if conversation_id:
            message.conversation_id = conversation_id
        
        task = A2ATask.create(message)
        response_task = self.send_task(task)
        
    
        if response_task.messages:
            for message in reversed(response_task.messages):
                if message.role == MessageRole.AGENT:
                    for part in message.parts:
                        if part.get("type") == "text":
                            return part.get("text", "")
        
       
        if response_task.artifacts:
            for artifact in response_task.artifacts:
                if "parts" in artifact:
                    for part in artifact["parts"]:
                        if part.get("type") == "text":
                            return part.get("text", "")
        
        return "No response from agent"
    
    def ping(self) -> bool:
       
        try:
            self.get_agent_card()
            return True
        except:
            return False


class A2AAgentNetwork:
   
    
    def __init__(self, name: str = "Agent Network"):
       
        self.name = name
        self.agents: Dict[str, A2AClient] = {}
        self.agent_cards: Dict[str, Dict[str, Any]] = {}
    
    def add_agent(self, alias: str, url: str) -> None:
        
        client = A2AClient(url)
        
        try:
            card = client.get_agent_card()
            self.agents[alias] = client
            self.agent_cards[alias] = card
            logger.info(f"Added agent '{alias}': {card.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to add agent '{alias}' at {url}: {e}")
            raise
    
    def get_agent(self, alias: str) -> A2AClient:

        if alias not in self.agents:
            raise KeyError(f"Agent '{alias}' not found in network")
        return self.agents[alias]
    
    def list_agents(self) -> List[Dict[str, Any]]:
  
        return [
            {
                "alias": alias,
                "name": card.get("name", "Unknown"),
                "description": card.get("description", ""),
                "url": card.get("url", "")
            }
            for alias, card in self.agent_cards.items()
        ]
    
    def broadcast_task(self, task: A2ATask) -> Dict[str, A2ATask]:
        
        responses = {}
        
        for alias, client in self.agents.items():
            try:
                response = client.send_task(task)
                responses[alias] = response
            except Exception as e:
                logger.error(f"Failed to send task to agent '{alias}': {e}")
                # Create error response
                error_task = A2ATask.create(task.message)
                error_task.status = {"state": TaskState.FAILED.value, "error": str(e)}
                responses[alias] = error_task
        
        return responses
    
    def check_agents_health(self) -> Dict[str, bool]:
      
        health_status = {}
        
        for alias, client in self.agents.items():
            health_status[alias] = client.ping()
        
        return health_status 