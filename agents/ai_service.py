"""
AI Service - Support multiple AI providers (OpenAI, Gemini)
"""

from typing import Dict, Any, Optional
from loguru import logger
import google.generativeai as genai
from openai import AsyncOpenAI
import json
import os

from config.settings import settings


class AIService:
    """Universal AI service supporting multiple providers"""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()

        if self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use model from environment variable or settings
            model_name = os.environ.get('GEMINI_MODEL', settings.AI_MODEL)
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"🤖 Using Google Gemini: {model_name}")
        elif self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("🤖 Using OpenAI GPT")
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    async def test_connection(self) -> bool:
        """Test AI connection"""
        try:
            if self.provider == "gemini":
                if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "":
                    logger.warning("⚠️  Gemini API key not configured")
                    return False

                # Test with simple prompt
                response = self.model.generate_content("Hello")
                logger.debug(f"✓ Gemini connection successful: {response.text[:50]}")
                return True

            elif self.provider == "openai":
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "":
                    logger.warning("⚠️  OpenAI API key not configured")
                    return False

                response = await self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=10
                )
                logger.debug("✓ OpenAI connection successful")
                return True

        except Exception as e:
            logger.warning(f"⚠️  AI connection failed: {e}")
            return False

    async def analyze_threat(self, incident: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
        """Analyze security threat using AI"""
        try:
            # Build analysis prompt
            prompt = f"""Analyze this security incident and respond in JSON format:

Incident Type: {incident.get('type', 'unknown')}
Source IP: {incident.get('source_ip', 'N/A')}
Destination IP: {incident.get('dest_ip', 'N/A')}
Protocol: {incident.get('protocol', 'N/A')}
Timestamp: {incident.get('timestamp', 'N/A')}
Details: {json.dumps(incident.get('details', {}))}

Respond ONLY with valid JSON in this exact format:
{{
  "severity": "low|medium|high|critical",
  "threat_type": "specific threat classification",
  "immediate_actions": ["action1", "action2"],
  "explanation": "clear explanation of the threat",
  "mitigation": "long-term prevention strategy",
  "confidence": 0.0-1.0
}}"""

            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()

                # Clean markdown code blocks if present
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                elif result_text.startswith("```"):
                    result_text = result_text.replace("```", "").strip()

                result = json.loads(result_text)

            elif self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.AI_TEMPERATURE,
                    max_tokens=settings.AI_MAX_TOKENS
                )
                result = json.loads(response.choices[0].message.content)

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Return fallback analysis
            return {
                "severity": "medium",
                "threat_type": incident.get('type', 'unknown'),
                "immediate_actions": ["Monitor the situation", "Log the incident"],
                "explanation": f"AI analysis failed. Manual review required for {incident.get('type')} from {incident.get('source_ip')}",
                "mitigation": "Review security policies and implement monitoring",
                "confidence": 0.5
            }
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using AI"""
        try:
            if self.provider == "gemini":
                # Combine system prompt with user prompt for Gemini
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.model.generate_content(full_prompt)
                return response.text

            elif self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise

    async def generate_report(self, incidents: list, timeframe: str) -> str:
        """Generate security report"""
        try:
            prompt = f"""Generate a comprehensive security report for the last {timeframe}.

Total Incidents: {len(incidents)}
Incident Summary:
{json.dumps(incidents[:10], indent=2)}

Create a professional security report with:
1. Executive Summary
2. Key Findings
3. Threat Analysis
4. Recommendations
5. Action Items"""

            if self.provider == "gemini":
                response = self.model.generate_content(prompt)
                return response.text

            elif self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=settings.AI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"# Security Report - {timeframe}\n\nReport generation failed: {str(e)}\n\nTotal incidents: {len(incidents)}"


# Global AI service instance
ai_service = AIService()
