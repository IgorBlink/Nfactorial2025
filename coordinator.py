"""Coordinator for multi-agent system using A2A protocol."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.config import Config
from utils.a2a_client import A2AAgentNetwork, A2AClient, A2AMessage, A2ATask, MessageRole

# Configure logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)


class MultiAgentCoordinator:
    """Coordinator for orchestrating multi-agent workflows via A2A protocol."""
    
    def __init__(self):
        """Initialize the coordinator."""
        self.network = A2AAgentNetwork("Multi-Agent Research System")
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize agents
        self._setup_agents()
        
        logger.info("Multi-Agent Coordinator initialized")
    
    def _setup_agents(self):
        """Setup agent network."""
        try:
            # Add research agent (LangChain)
            self.network.add_agent("research", Config.RESEARCH_AGENT_URL)
            logger.info("✅ Research Agent connected")
            
            # Add analytics agent (PydanticAI)  
            self.network.add_agent("analytics", Config.ANALYTICS_AGENT_URL)
            logger.info("✅ Analytics Agent connected")
            
        except Exception as e:
            logger.error(f"Failed to setup agents: {e}")
            raise
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check health of all agents in the system."""
        health_status = self.network.check_agents_health()
        
        system_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if all(health_status.values()) else "degraded",
            "agents": {}
        }
        
        for alias, is_healthy in health_status.items():
            agent_info = next(
                (agent for agent in self.network.list_agents() if agent["alias"] == alias),
                {"name": "Unknown", "description": ""}
            )
            
            system_status["agents"][alias] = {
                "name": agent_info["name"],
                "description": agent_info["description"],
                "status": "healthy" if is_healthy else "unhealthy"
            }
        
        return system_status
    
    def list_capabilities(self) -> Dict[str, Any]:
        """List capabilities of all agents."""
        capabilities = {
            "system_name": self.network.name,
            "agents": {}
        }
        
        for agent_info in self.network.list_agents():
            alias = agent_info["alias"]
            capabilities["agents"][alias] = {
                "name": agent_info["name"],
                "description": agent_info["description"],
                "framework": "LangChain" if alias == "research" else "PydanticAI"
            }
        
        return capabilities
    
    def process_research_task(self, topic: str, depth: str = "standard", 
                            conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a research task using both agents.
        
        Args:
            topic: Research topic
            depth: Depth of analysis (basic, standard, detailed)
            conversation_id: Optional conversation ID for context
            
        Returns:
            Comprehensive research results
        """
        if not conversation_id:
            conversation_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔬 Starting research task: {topic}")
        
        try:
            # Step 1: Gather information using Research Agent
            research_results = self._conduct_research(topic, conversation_id)
            
            # Step 2: Analyze findings using Analytics Agent  
            analysis_results = self._analyze_findings(research_results, depth, conversation_id)
            
            # Step 3: Combine results
            final_results = self._combine_results(topic, research_results, analysis_results, conversation_id)
            
            # Store conversation history
            self._store_conversation(conversation_id, final_results)
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error processing research task: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _conduct_research(self, topic: str, conversation_id: str) -> str:
        """Conduct research using Research Agent (LangChain)."""
        logger.info("📚 Conducting research phase...")
        
        research_agent = self.network.get_agent("research")
        
        research_query = f"""
        Проведи исследование по теме: "{topic}"
        
        Необходимо:
        1. Найти ключевую информацию по теме
        2. Проанализировать основные аспекты  
        3. Выявить важные факты и тенденции
        4. Подготовить материал для дальнейшего анализа
        """
        
        return research_agent.ask(research_query, conversation_id)
    
    def _analyze_findings(self, research_data: str, depth: str, conversation_id: str) -> str:
        """Analyze research findings using Analytics Agent (PydanticAI)."""
        logger.info("📊 Analyzing research findings...")
        
        analytics_agent = self.network.get_agent("analytics")
        
        analysis_query = f"""
        Проведи {depth} анализ данных следующих исследований:
        
        {research_data}
        
        Создай структурированный анализ с:
        - Ключевыми инсайтами
        - Рекомендациями  
        - Выводами
        - Практическими применениями
        """
        
        return analytics_agent.ask(analysis_query, conversation_id)
    
    def _combine_results(self, topic: str, research_results: str, 
                        analysis_results: str, conversation_id: str) -> Dict[str, Any]:
        """Combine research and analysis results."""
        return {
            "success": True,
            "topic": topic,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "workflow": {
                "step_1_research": {
                    "agent": "ResearchAgent (LangChain)",
                    "description": "Information gathering and initial analysis",
                    "results": research_results
                },
                "step_2_analysis": {
                    "agent": "AnalyticsAgent (PydanticAI)", 
                    "description": "Deep analysis and insights extraction",
                    "results": analysis_results
                }
            },
            "final_summary": self._create_summary(topic, research_results, analysis_results)
        }
    
    def _create_summary(self, topic: str, research_results: str, analysis_results: str) -> str:
        """Create final summary of the research task."""
        return f"""
# 📋 Итоговый отчет: {topic}

## 🔬 Результаты исследования (LangChain)
{research_results}

---

## 📊 Аналитические выводы (PydanticAI)  
{analysis_results}

---

## ✅ Заключение
Исследование выполнено с использованием мультиагентной системы:
- **Исследовательский агент** (LangChain): сбор и первичный анализ информации
- **Аналитический агент** (PydanticAI): глубокий анализ и извлечение инсайтов

Оба агента взаимодействовали через стандартизированный A2A протокол, обеспечивая 
интеграцию различных AI фреймворков в единой системе.
"""
    
    def _store_conversation(self, conversation_id: str, results: Dict[str, Any]):
        """Store conversation history."""
        self.conversation_history[conversation_id] = results
        logger.info(f"💾 Stored conversation: {conversation_id}")
    
    def get_conversation_history(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history by ID."""
        return self.conversation_history.get(conversation_id)
    
    def list_conversations(self) -> List[str]:
        """List all conversation IDs."""
        return list(self.conversation_history.keys())
    
    async def process_complex_workflow(self, task_description: str) -> Dict[str, Any]:
        """Process a complex workflow involving multiple agent interactions."""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔄 Starting complex workflow: {workflow_id}")
        
        try:
            # Step 1: Break down the task using Research Agent
            research_agent = self.network.get_agent("research")
            task_breakdown = research_agent.ask(
                f"Разбей следующую задачу на подзадачи для исследования: {task_description}"
            )
            
            # Step 2: Analyze task complexity using Analytics Agent
            analytics_agent = self.network.get_agent("analytics")
            complexity_analysis = analytics_agent.ask(
                f"Проанализируй сложность и приоритеты следующих подзадач: {task_breakdown}"
            )
            
            # Step 3: Execute based on analysis
            execution_plan = research_agent.ask(
                f"Создай план выполнения на основе анализа: {complexity_analysis}"
            )
            
            # Step 4: Final report
            final_report = analytics_agent.ask(
                f"Создай итоговый отчет по выполнению задачи: {execution_plan}"
            )
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "steps": {
                    "task_breakdown": task_breakdown,
                    "complexity_analysis": complexity_analysis,
                    "execution_plan": execution_plan,
                    "final_report": final_report
                }
            }
            
        except Exception as e:
            logger.error(f"Error in complex workflow: {e}")
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """Main function to run the coordinator."""
    try:
        # Validate configuration
        Config.validate()
        
        # Create coordinator
        coordinator = MultiAgentCoordinator()
        
        # Check system health
        health = coordinator.check_system_health()
        print("🏥 System Health Check:")
        print(f"Overall Status: {health['overall_status']}")
        for agent, status in health["agents"].items():
            status_emoji = "✅" if status["status"] == "healthy" else "❌"
            print(f"{status_emoji} {status['name']}: {status['status']}")
        
        # Show capabilities
        capabilities = coordinator.list_capabilities()
        print(f"\n🔧 System Capabilities:")
        for agent, info in capabilities["agents"].items():
            print(f"• {info['name']} ({info['framework']}): {info['description']}")
        
        # Interactive mode
        print(f"\n🤖 Multi-Agent System Ready!")
        print("Available commands:")
        print("- research <topic>: Start research task")
        print("- workflow <description>: Start complex workflow")
        print("- health: Check system health")
        print("- quit: Exit")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() == "quit":
                    break
                elif command.lower() == "health":
                    health = coordinator.check_system_health()
                    print(f"System Status: {health['overall_status']}")
                elif command.startswith("research "):
                    topic = command[9:]  # Remove "research "
                    print(f"🔬 Starting research on: {topic}")
                    results = coordinator.process_research_task(topic)
                    if results["success"]:
                        print(results["final_summary"])
                    else:
                        print(f"❌ Error: {results['error']}")
                elif command.startswith("workflow "):
                    task = command[9:]  # Remove "workflow "
                    print(f"🔄 Starting workflow: {task}")
                    results = asyncio.run(coordinator.process_complex_workflow(task))
                    if results["success"]:
                        print("✅ Workflow completed!")
                        print(results["steps"]["final_report"])
                    else:
                        print(f"❌ Error: {results['error']}")
                else:
                    print("❓ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
        
        print("👋 Goodbye!")
        
    except Exception as e:
        logger.error(f"Failed to start coordinator: {e}")
        print(f"❌ Failed to start: {e}")


if __name__ == "__main__":
    main() 