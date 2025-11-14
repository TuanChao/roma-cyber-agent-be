"""
Network Monitor Agent - Real-time network traffic monitoring and analysis
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
import asyncio
from collections import defaultdict
import ipaddress

from agents.base_agent import BaseAgent


class NetworkMonitorAgent(BaseAgent):
    """
    Monitors network traffic and detects suspicious activities
    - Port scanning detection
    - DDoS attack identification
    - Unusual traffic patterns
    - Protocol analysis
    """

    def __init__(self, interface: str = "eth0", agent_id: Optional[str] = None, broadcast_callback=None):
        super().__init__(name="NetworkMonitor", agent_id=agent_id)
        self.interface = interface
        self.packet_count = 0
        self.alerts = []
        self.broadcast_callback = broadcast_callback  # Callback to broadcast alerts

        # Traffic tracking
        self.port_scan_tracker = defaultdict(set)  # IP -> set of ports
        self.traffic_stats = defaultdict(int)
        self.protocol_stats = defaultdict(int)

        # Thresholds
        self.PORT_SCAN_THRESHOLD = 10  # ports in timeframe
        self.DDOS_THRESHOLD = 1000  # packets per second
        self.PORT_SCAN_WINDOW = 60  # seconds

    async def start(self) -> None:
        """Start network monitoring"""
        logger.info(f"🔍 Starting Network Monitor on interface: {self.interface}")

        try:
            self.is_running = True
            self.start_time = datetime.now()
            await self._set_status("running")

            # Start packet capture in background
            asyncio.create_task(self._capture_packets())

            logger.success(f"✅ Network Monitor started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start Network Monitor: {e}")
            await self._set_status("error")
            self.metrics["errors"] += 1
            raise

    async def stop(self) -> None:
        """Stop network monitoring"""
        logger.info("🛑 Stopping Network Monitor...")
        self.is_running = False
        await self._set_status("stopped")
        logger.success("✅ Network Monitor stopped")

    async def _capture_packets(self) -> None:
        """Capture and analyze network packets"""
        try:
            # Run packet capture in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: sniff(
                    iface=self.interface,
                    prn=self._packet_callback,
                    store=False,
                    stop_filter=lambda x: not self.is_running
                )
            )
        except Exception as e:
            logger.error(f"❌ Packet capture error: {e}")
            self.metrics["errors"] += 1

    def _packet_callback(self, packet) -> None:
        """Process each captured packet"""
        try:
            if not self.is_running:
                return

            self.packet_count += 1
            self.metrics["events_processed"] += 1

            # Analyze packet
            analysis = self._analyze_packet(packet)

            if analysis.get("suspicious"):
                # Create alert
                alert = self._create_alert(analysis)
                self.alerts.append(alert)
                self.metrics["alerts_generated"] += 1

                # Log alert
                logger.warning(f"🚨 ALERT: {alert['type']} from {alert['source_ip']}")

                # Broadcast alert in real-time
                if self.broadcast_callback:
                    try:
                        asyncio.create_task(self.broadcast_callback(alert))
                    except Exception as e:
                        logger.error(f"Failed to broadcast alert: {e}")

        except Exception as e:
            logger.error(f"❌ Packet analysis error: {e}")
            self.metrics["errors"] += 1

    def _analyze_packet(self, packet) -> Dict[str, Any]:
        """Analyze a single packet for threats"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "suspicious": False,
            "threat_type": None,
            "severity": "low"
        }

        # Extract packet info
        if IP in packet:
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            analysis["source_ip"] = src_ip
            analysis["dest_ip"] = dst_ip

            # Protocol analysis
            if TCP in packet:
                analysis["protocol"] = "TCP"
                analysis["src_port"] = packet[TCP].sport
                analysis["dst_port"] = packet[TCP].dport

                # Port scan detection
                self.port_scan_tracker[src_ip].add(packet[TCP].dport)
                if len(self.port_scan_tracker[src_ip]) > self.PORT_SCAN_THRESHOLD:
                    analysis["suspicious"] = True
                    analysis["threat_type"] = "port_scan"
                    analysis["severity"] = "high"
                    analysis["ports_scanned"] = list(self.port_scan_tracker[src_ip])

            elif UDP in packet:
                analysis["protocol"] = "UDP"
                analysis["src_port"] = packet[UDP].sport
                analysis["dst_port"] = packet[UDP].dport

            elif ICMP in packet:
                analysis["protocol"] = "ICMP"
                # ICMP flood detection
                self.traffic_stats[f"icmp_{src_ip}"] += 1
                if self.traffic_stats[f"icmp_{src_ip}"] > 100:
                    analysis["suspicious"] = True
                    analysis["threat_type"] = "icmp_flood"
                    analysis["severity"] = "medium"

        elif ARP in packet:
            analysis["protocol"] = "ARP"
            # ARP spoofing detection could be added here

        # Update protocol stats
        self.protocol_stats[analysis.get("protocol", "unknown")] += 1

        return analysis

    def _create_alert(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a security alert from analysis"""
        return {
            "alert_id": f"alert_{datetime.now().timestamp()}",
            "timestamp": analysis["timestamp"],
            "type": analysis["threat_type"],
            "severity": analysis["severity"],
            "source_ip": analysis.get("source_ip"),
            "dest_ip": analysis.get("dest_ip"),
            "protocol": analysis.get("protocol"),
            "details": analysis,
            "agent": self.name,
            "status": "new"
        }

    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process external event (from other agents or API)"""
        # Can be used to correlate with other data sources
        return {"processed": True, "agent": self.name}

    async def get_statistics(self) -> Dict[str, Any]:
        """Get network monitoring statistics"""
        return {
            "total_packets": self.packet_count,
            "protocol_distribution": dict(self.protocol_stats),
            "active_ips": len(self.port_scan_tracker),
            "total_alerts": len(self.alerts),
            "recent_alerts": self.alerts[-10:] if self.alerts else []
        }

    async def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent security alerts"""
        return self.alerts[-limit:] if self.alerts else []

    async def clear_alerts(self) -> None:
        """Clear all alerts"""
        cleared_count = len(self.alerts)
        self.alerts.clear()
        logger.info(f"🗑️ Cleared {cleared_count} alerts")
