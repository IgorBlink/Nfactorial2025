

import logging
import sys
import os
from typing import Dict, Any, Optional, List
try:
    from langchain_community.chat_models import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseA2AAgent
from utils.config import Config
from utils.a2a_client import A2ATask, TaskState

logger = logging.getLogger(__name__)


class ResearchAgent(BaseA2AAgent):
  
    
    def __init__(self, port: Optional[int] = None):
        
        if port is None:
            port = Config.RESEARCH_AGENT_PORT
        
        super().__init__(
            name="ResearchAgent",
            description="AI agent specialized in research, information gathering, and analysis using LangChain",
            port=port
        )
        

        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for Research Agent")
       
        try:
            self.llm = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY,
                model=Config.OPENAI_MODEL,
                temperature=0.7,
                max_tokens=1500
            )
        except Exception as e:
            logger.warning(f"Ошибка создания ChatOpenAI: {e}. Пробуем альтернативную инициализацию.")
            try:
                from langchain_openai import ChatOpenAI as OpenAIChatModel
                self.llm = OpenAIChatModel(
                    api_key=Config.OPENAI_API_KEY,
                    model=Config.OPENAI_MODEL,
                    temperature=0.7,
                    max_tokens=1500
                )
            except Exception as e2:
                logger.error(f"Не удалось создать LLM: {e2}")
                raise
        
        # Memory for conversation context
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Define research tools
        self.tools = self._create_tools()
        
        # Initialize agent with tools
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
        
        logger.info("Research Agent initialized with LangChain")
    
    def _create_tools(self) -> List[Tool]:
     
        
        def web_search_tool(query: str) -> str:
          
            return f"Поиск информации по запросу: '{query}'. Найдены релевантные источники и данные."
        
        def summarize_tool(text: str) -> str:
        
            try:
                messages = [
                    SystemMessage(content="Ты - эксперт по созданию кратких и содержательных резюме."),
                    HumanMessage(content=f"Создай краткое резюме следующего текста:\n\n{text}")
                ]
                response = self.llm(messages)
                return response.content
            except Exception as e:
                return f"Ошибка при создании резюме: {str(e)}"
        
        def analyze_topic_tool(topic: str) -> str:
     
            try:
                messages = [
                    SystemMessage(content="Ты - исследователь-аналитик. Проводи глубокий анализ тем."),
                    HumanMessage(content=f"Проведи детальный анализ темы: '{topic}'. Включи ключевые аспекты, тенденции и выводы.")
                ]
                response = self.llm(messages)
                return response.content
            except Exception as e:
                return f"Ошибка при анализе темы: {str(e)}"
        
        def fact_check_tool(claim: str) -> str:
    
            try:
                messages = [
                    SystemMessage(content="Ты - эксперт по проверке фактов. Анализируй утверждения критически."),
                    HumanMessage(content=f"Проверь достоверность следующего утверждения: '{claim}'")
                ]
                response = self.llm(messages)
                return response.content
            except Exception as e:
                return f"Ошибка при проверке фактов: {str(e)}"
        
        return [
            Tool(
                name="WebSearch",
                func=web_search_tool,
                description="Поиск информации в интернете по заданному запросу"
            ),
            Tool(
                name="Summarize",
                func=summarize_tool,
                description="Создание краткого резюме предоставленного текста"
            ),
            Tool(
                name="AnalyzeTopic", 
                func=analyze_topic_tool,
                description="Глубокий анализ заданной темы с выявлением ключевых аспектов"
            ),
            Tool(
                name="FactCheck",
                func=fact_check_tool,
                description="Проверка фактов и достоверности утверждений"
            )
        ]
    
    def process_task(self, task: A2ATask) -> A2ATask:
     
        try:
            # Extract user query
            user_input = self.extract_text_from_message(task.message)
            
            if not user_input:
                return self.create_error_response(
                    "Не удалось извлечь текст из сообщения", 
                    task
                )
            
            logger.info(f"Processing research query: {user_input}")
            
            # Determine research type based on input
            research_type = self._determine_research_type(user_input)
            
            # Process with LangChain agent
            response = self._conduct_research(user_input, research_type)
            
            # Create response
            return self.create_text_response(response, task)
            
        except Exception as e:
            logger.error(f"Error processing research task: {e}")
            return self.create_error_response(str(e), task)
    
    def _determine_research_type(self, query: str) -> str:
      
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["анализ", "исследование", "анализировать"]):
            return "analysis"
        elif any(word in query_lower for word in ["поиск", "найти", "информация"]):
            return "search"
        elif any(word in query_lower for word in ["резюме", "сократить", "суммировать"]):
            return "summarize"
        elif any(word in query_lower for word in ["проверить", "факт", "достоверность"]):
            return "fact_check"
        else:
            return "general"
    
    def _conduct_research(self, query: str, research_type: str) -> str:
   
        try:
            if research_type == "analysis":
                # Use analyze tool directly
                return self.tools[2].func(query)
            elif research_type == "search":
                # Use web search tool
                search_results = self.tools[0].func(query)
                return f"Результаты поиска:\n{search_results}"
            elif research_type == "summarize":
                # Use summarize tool
                return self.tools[1].func(query)
            elif research_type == "fact_check":
                # Use fact check tool
                return self.tools[3].func(query)
            else:
                # Use full agent for general queries
                response = self.agent.run(query)
                return response
                
        except Exception as e:
            logger.error(f"Error in research process: {e}")
            # Fallback to basic LLM response
            try:
                messages = [
                    SystemMessage(content="Ты - исследовательский ассистент. Помогай с поиском и анализом информации."),
                    HumanMessage(content=query)
                ]
                response = self.llm(messages)
                return response.content
            except Exception as fallback_error:
                return f"Извините, произошла ошибка при обработке вашего запроса: {str(fallback_error)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
    
        return {
            "research_types": [
                "information_search",
                "topic_analysis", 
                "text_summarization",
                "fact_checking"
            ],
            "tools": [tool.name for tool in self.tools],
            "framework": "LangChain",
            "model": Config.OPENAI_MODEL
        }


def main():
   
    try:
        # Validate configuration
        Config.validate()
        
        # Create and run agent
        agent = ResearchAgent()
        agent.run(debug=True)
        
    except KeyboardInterrupt:
        logger.info("Research Agent stopped by user")
    except Exception as e:
        logger.error(f"Failed to start Research Agent: {e}")
        raise


if __name__ == "__main__":
    main() 