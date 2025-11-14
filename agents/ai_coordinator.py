"""
AI Response Coordinator - GPT-4 powered intelligent threat analysis and response
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
import asyncio

from agents.base_agent import BaseAgent
from agents.ai_service import ai_service
from config.settings import settings


class AIResponseCoordinator(BaseAgent):
    """
    AI-powered coordinator for threat analysis and automated response
    - Analyzes security incidents using GPT-4
    - Makes intelligent response decisions
    - Generates human-readable incident reports
    - Suggests mitigation strategies
    """

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(name="AICoordinator", agent_id=agent_id)

        # Use universal AI service
        self.ai_service = ai_service

        # Response history for learning
        self.incident_history = []
        self.response_actions = []

        # System prompt for AI
        self.system_prompt = """You are a cybersecurity AI agent specialized in threat analysis and incident response.

Your responsibilities:
1. Analyze security incidents and determine severity (low, medium, high, critical)
2. Suggest immediate response actions (block IP, isolate host, alert admin, etc.)
3. Provide clear explanations for non-technical stakeholders
4. Recommend long-term mitigation strategies
5. Learn from past incidents to improve future responses

When analyzing incidents, consider:
- Attack type and method
- Potential impact and risk
- Source and target information
- Pattern similarities with known threats
- Current system vulnerabilities

Respond in JSON format with:
{
  "severity": "low|medium|high|critical",
  "threat_type": "specific threat classification",
  "immediate_actions": ["action1", "action2"],
  "explanation": "clear explanation of the threat",
  "mitigation": "long-term prevention strategy",
  "confidence": 0.0-1.0
}"""

    async def start(self) -> None:
        """Start AI Response Coordinator"""
        logger.info("🤖 Starting AI Response Coordinator")

        try:
            # Test OpenAI connection
            await self._test_ai_connection()

            self.is_running = True
            self.start_time = datetime.now()
            await self._set_status("running")

            logger.success("✅ AI Response Coordinator started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start AI Coordinator: {e}")
            await self._set_status("error")
            self.metrics["errors"] += 1
            raise

    async def stop(self) -> None:
        """Stop AI coordinator"""
        logger.info("🛑 Stopping AI Response Coordinator...")
        self.is_running = False
        await self._set_status("stopped")
        logger.success("✅ AI Response Coordinator stopped")

    async def _test_ai_connection(self) -> None:
        """Test connection to AI provider"""
        success = await self.ai_service.test_connection()
        if success:
            logger.success(f"✅ AI Provider ({settings.AI_PROVIDER}) connected successfully")
        else:
            logger.warning("⚠️  AI features will be disabled")

    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process security incident with AI analysis"""
        return await self.analyze_incident(event)

    async def analyze_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security incident using GPT-4

        Args:
            incident: Incident data containing type, source, target, details

        Returns:
            AI analysis with severity, actions, and explanations
        """
        logger.info(f"🔍 Analyzing incident: {incident.get('type', 'unknown')}")

        try:
            # Use AI service for analysis
            analysis_result = await self.ai_service.analyze_threat(incident, self.system_prompt)

            # Enhance with metadata
            result = {
                "incident_id": incident.get("alert_id") or f"inc_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "original_incident": incident,
                "ai_analysis": analysis_result,
                "status": "analyzed"
            }

            # Store in history
            self.incident_history.append(result)
            self.metrics["events_processed"] += 1

            # Execute immediate actions if needed
            if analysis_result.get("severity") in ["high", "critical"]:
                await self._execute_actions(analysis_result["immediate_actions"], incident)

            logger.success(f"✅ Incident analyzed - Severity: {analysis_result.get('severity')}")
            return result

        except Exception as e:
            logger.error(f"❌ Incident analysis error: {e}")
            self.metrics["errors"] += 1
            return {
                "error": str(e),
                "status": "analysis_failed",
                "incident": incident
            }

    def _format_incident_context(self, incident: Dict[str, Any]) -> str:
        """Format incident data for AI analysis"""
        context = f"""
SECURITY INCIDENT ANALYSIS REQUEST

Incident Type: {incident.get('type', 'Unknown')}
Timestamp: {incident.get('timestamp', 'N/A')}
Source IP: {incident.get('source_ip', 'Unknown')}
Destination IP: {incident.get('dest_ip', 'Unknown')}
Protocol: {incident.get('protocol', 'Unknown')}

Details:
{self._format_details(incident.get('details', {}))}

Please analyze this security incident and provide:
1. Severity assessment
2. Threat classification
3. Immediate response actions
4. Clear explanation for security team
5. Long-term mitigation strategy
6. Confidence level in your analysis
"""
        return context.strip()

    def _format_details(self, details: Dict[str, Any]) -> str:
        """Format incident details"""
        lines = []
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                lines.append(f"- {key}: {str(value)[:100]}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines) if lines else "No additional details"

    async def _execute_actions(
        self,
        actions: List[str],
        incident: Dict[str, Any]
    ) -> None:
        """Execute immediate response actions"""
        logger.warning(f"⚡ Executing {len(actions)} immediate actions")

        for action in actions:
            try:
                action_lower = action.lower()

                if "block ip" in action_lower:
                    await self._block_ip(incident.get("source_ip"))
                elif "alert" in action_lower:
                    await self._send_alert(incident, action)
                elif "isolate" in action_lower:
                    await self._isolate_host(incident.get("source_ip"))
                elif "log" in action_lower:
                    await self._enhanced_logging(incident)

                self.response_actions.append({
                    "action": action,
                    "incident_id": incident.get("alert_id"),
                    "timestamp": datetime.now().isoformat(),
                    "status": "executed"
                })

                logger.info(f"✓ Action executed: {action}")

            except Exception as e:
                logger.error(f"❌ Failed to execute action '{action}': {e}")

    async def _block_ip(self, ip: str) -> None:
        """Block IP address (placeholder - integrate with firewall)"""
        logger.warning(f"🚫 BLOCKING IP: {ip}")
        # TODO: Integrate with actual firewall/iptables
        await asyncio.sleep(0.1)

    async def _send_alert(self, incident: Dict[str, Any], message: str) -> None:
        """Send alert to admins (placeholder)"""
        logger.warning(f"📧 ALERT: {message}")
        # TODO: Integrate with email/Slack/webhook
        await asyncio.sleep(0.1)

    async def _isolate_host(self, ip: str) -> None:
        """Isolate compromised host (placeholder)"""
        logger.warning(f"🔒 ISOLATING HOST: {ip}")
        # TODO: Integrate with network isolation
        await asyncio.sleep(0.1)

    async def _enhanced_logging(self, incident: Dict[str, Any]) -> None:
        """Enable enhanced logging for incident"""
        logger.info(f"📝 Enhanced logging enabled for {incident.get('type')}")
        await asyncio.sleep(0.1)

    async def generate_report(
        self,
        incident_ids: Optional[List[str]] = None,
        timeframe: str = "24h"
    ) -> str:
        """
        Generate human-readable incident report

        Args:
            incident_ids: Specific incidents to include (None = all recent)
            timeframe: Time range (24h, 7d, 30d)

        Returns:
            Formatted report text
        """
        logger.info(f"📊 Generating incident report for {timeframe}")

        try:
            # Get relevant incidents
            incidents = self._get_incidents_for_report(incident_ids, timeframe)

            if not incidents:
                return "No incidents to report in the specified timeframe."

            # Create report context
            report_context = self._format_report_context(incidents, timeframe)

            # Generate report with AI service
            system_prompt = "You are a cybersecurity analyst writing incident reports. Create clear, professional reports suitable for both technical and non-technical stakeholders."

            # Use AI service to generate report
            report = await self.ai_service.generate_text(
                prompt=f"Generate a comprehensive security incident report:\n\n{report_context}",
                system_prompt=system_prompt
            )

            logger.success("✅ Report generated successfully")
            return report

        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            return f"Error generating report: {str(e)}"

    def _get_incidents_for_report(
        self,
        incident_ids: Optional[List[str]],
        timeframe: str
    ) -> List[Dict[str, Any]]:
        """Get incidents for report"""
        if incident_ids:
            return [i for i in self.incident_history if i.get("incident_id") in incident_ids]

        # TODO: Filter by timeframe
        return self.incident_history[-10:]  # Last 10 for now

    def _format_report_context(
        self,
        incidents: List[Dict[str, Any]],
        timeframe: str
    ) -> str:
        """Format incidents for report generation"""
        context = f"INCIDENT REPORT - {timeframe.upper()}\n"
        context += f"Total Incidents: {len(incidents)}\n\n"

        for idx, inc in enumerate(incidents, 1):
            ai_analysis = inc.get("ai_analysis", {})
            context += f"{idx}. {inc.get('original_incident', {}).get('type', 'Unknown')}\n"
            context += f"   Severity: {ai_analysis.get('severity', 'Unknown')}\n"
            context += f"   Actions Taken: {', '.join(ai_analysis.get('immediate_actions', []))}\n\n"

        return context

    async def get_statistics(self) -> Dict[str, Any]:
        """Get AI coordinator statistics"""
        severity_counts = {}
        for inc in self.incident_history:
            severity = inc.get("ai_analysis", {}).get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_incidents_analyzed": len(self.incident_history),
            "actions_executed": len(self.response_actions),
            "severity_distribution": severity_counts,
            "recent_incidents": self.incident_history[-5:]
        }
