

import logging
import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import json
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseA2AAgent
from utils.config import Config
from utils.a2a_client import A2ATask, TaskState

logger = logging.getLogger(__name__)


# Pydantic models for data validation
class AnalysisRequest(BaseModel):

    query: str = Field(..., description="The query to analyze")
    analysis_type: str = Field(default="general", description="Type of analysis to perform")
    depth: str = Field(default="standard", description="Depth of analysis: basic, standard, detailed")


class AnalysisResult(BaseModel):

    summary: str = Field(..., description="Summary of the analysis")
    key_points: List[str] = Field(default_factory=list, description="Key points from analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on analysis")
    confidence_score: float = Field(default=0.8, description="Confidence in the analysis")
    timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")


class DataInsight(BaseModel):
   
    insight: str = Field(..., description="The insight discovered")
    significance: str = Field(..., description="Why this insight is significant")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting the insight")


class AnalyticsAgent(BaseA2AAgent):
  
    
    def __init__(self, port: Optional[int] = None):
        
        if port is None:
            port = Config.ANALYTICS_AGENT_PORT
        
        super().__init__(
            name="AnalyticsAgent", 
            description="AI agent specialized in data analysis, insights generation, and reporting using structured analytics",
            port=port
        )
        
        # Validate configuration
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required for Analytics Agent")
        
        # Initialize OpenAI client
        try:
            self.client = OpenAI(
                api_key=Config.OPENAI_API_KEY,
                timeout=30.0
            )
        except Exception as e:
            logger.warning(f"Ошибка создания OpenAI клиента: {e}. Используем базовую конфигурацию.")
            # Fallback к более простой инициализации
            import openai
            openai.api_key = Config.OPENAI_API_KEY
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        logger.info("Analytics Agent initialized with OpenAI")
    
    def process_task(self, task: A2ATask) -> A2ATask:
       
        try:
            # Extract user query
            user_input = self.extract_text_from_message(task.message)
            
            if not user_input:
                return self.create_error_response(
                    "Не удалось извлечь текст из сообщения",
                    task
                )
            
            logger.info(f"Processing analytics query: {user_input}")
            
            # Parse request
            analysis_request = self._parse_analysis_request(user_input)
            
            # Perform analysis
            response = self._perform_analysis(analysis_request)
            
            # Create response
            return self.create_text_response(response, task)
            
        except Exception as e:
            logger.error(f"Error processing analytics task: {e}")
            return self.create_error_response(str(e), task)
    
    def _parse_analysis_request(self, user_input: str) -> AnalysisRequest:
        """Parse user input into analysis request."""
        # Determine analysis type
        analysis_type = "general"
        depth = "standard"
        
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["отчет", "report", "создай отчет"]):
            analysis_type = "report"
        elif any(word in input_lower for word in ["инсайт", "insight", "закономерность"]):
            analysis_type = "insights"
        elif any(word in input_lower for word in ["анализ данных", "data analysis"]):
            analysis_type = "data_analysis"
        
        if any(word in input_lower for word in ["детальн", "подробн", "глубок"]):
            depth = "detailed"
        elif any(word in input_lower for word in ["кратк", "базов", "простой"]):
            depth = "basic"
        
        return AnalysisRequest(
            query=user_input,
            analysis_type=analysis_type,
            depth=depth
        )
    
    def _perform_analysis(self, request: AnalysisRequest) -> str:
        """Perform analysis based on request type."""
        try:
            if request.analysis_type == "report":
                return self._generate_report(request)
            elif request.analysis_type == "insights":
                return self._extract_insights(request)
            elif request.analysis_type == "data_analysis":
                return self._analyze_data(request)
            else:
                return self._general_analysis(request)
                
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return f"Произошла ошибка при выполнении анализа: {str(e)}"
    
    def _analyze_data(self, request: AnalysisRequest) -> str:
      
        try:
            prompt = f"""
            Ты - эксперт по анализу данных. Проведи анализ следующего запроса: {request.query}
            
            Глубина анализа: {request.depth}
            
            Предоставь структурированный анализ в JSON формате со следующими полями:
            - summary: краткое резюме
            - key_points: список ключевых моментов (массив строк)
            - recommendations: рекомендации (массив строк)
            - confidence_score: оценка достоверности (число от 0 до 1)
            
            Ответь ТОЛЬКО JSON без дополнительного текста.
            """
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты - аналитик данных. Всегда отвечай в JSON формате."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            try:
                result_json = json.loads(response.choices[0].message.content)
                result = AnalysisResult(**result_json)
            except (json.JSONDecodeError, ValueError):
                # Fallback to simple parsing
                content = response.choices[0].message.content
                result = AnalysisResult(
                    summary=content[:200] + "..." if len(content) > 200 else content,
                    key_points=[content[:100] + "..."],
                    recommendations=["Анализ выполнен успешно"],
                    confidence_score=0.7
                )
            
            # Format the result nicely
            formatted_result = f"""
## 📊 Результаты анализа данных

### Краткое резюме:
{result.summary}

### Ключевые моменты:
"""
            for i, point in enumerate(result.key_points, 1):
                formatted_result += f"{i}. {point}\n"
            
            if result.recommendations:
                formatted_result += "\n### Рекомендации:\n"
                for i, rec in enumerate(result.recommendations, 1):
                    formatted_result += f"{i}. {rec}\n"
            
            formatted_result += f"\n### Уровень достоверности: {result.confidence_score:.1%}"
            formatted_result += f"\n### Время анализа: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return f"Ошибка при анализе данных: {str(e)}"
    
    def _generate_report(self, request: AnalysisRequest) -> str:
      
        try:
            prompt = f"""
            Создай профессиональный аналитический отчет на основе следующего запроса:
            {request.query}
            
            Отчет должен включать:
            - Исполнительное резюме
            - Детальный анализ
            - Выводы и рекомендации
            - Следующие шаги
            
            Глубина анализа: {request.depth}
            """
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты - специалист по созданию аналитических отчетов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            report = response.choices[0].message.content
            return f"## 📋 Аналитический отчет\n\n{report}"
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Ошибка при создании отчета: {str(e)}"
    
    def _extract_insights(self, request: AnalysisRequest) -> str:
      
        try:
            prompt = f"""
            Извлеки ключевые инсайты из следующего запроса: {request.query}
            
            Найди:
            - Скрытые закономерности
            - Важные тенденции  
            - Неожиданные выводы
            - Практически применимые находки
            
            Представь результат в виде списка инсайтов, где каждый инсайт содержит:
            1. Описание инсайта
            2. Его значимость
            3. Обоснование
            """
            
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты - аналитик по извлечению инсайтов из данных."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            insights_text = response.choices[0].message.content
            
            return f"## 💡 Ключевые инсайты\n\n{insights_text}"
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return f"Ошибка при извлечении инсайтов: {str(e)}"
    
    def _general_analysis(self, request: AnalysisRequest) -> str:
  
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты - универсальный аналитик. Проводи тщательный анализ запросов."},
                    {"role": "user", "content": f"Проведи общий анализ следующего запроса: {request.query}"}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content
            
            return f"""
## 🔍 Общий анализ

{analysis}
"""
        except Exception as e:
            logger.error(f"Error in general analysis: {e}")
            return f"Ошибка при общем анализе: {str(e)}"
    
    def get_capabilities(self) -> Dict[str, Any]:
      
        return {
            "analysis_types": [
                "data_analysis",
                "report_generation",
                "insight_extraction",
                "general_analysis"
            ],
            "depth_levels": ["basic", "standard", "detailed"],
            "output_formats": ["structured", "report", "insights"],
            "framework": "OpenAI Direct",
            "model": Config.OPENAI_MODEL
        }


def main():

    try:
        # Validate configuration
        Config.validate()
        
        # Create and run agent
        agent = AnalyticsAgent()
        agent.run(debug=True)
        
    except KeyboardInterrupt:
        logger.info("Analytics Agent stopped by user")
    except Exception as e:
        logger.error(f"Failed to start Analytics Agent: {e}")
        raise


if __name__ == "__main__":
    main() 