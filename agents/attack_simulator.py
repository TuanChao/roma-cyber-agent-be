"""
Attack Simulator Agent - Controlled attack simulation for testing
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from scapy.all import IP, TCP, UDP, ICMP, sr1, send, ARP
import asyncio
import socket
import ipaddress

from agents.base_agent import BaseAgent


class AttackSimulatorAgent(BaseAgent):
    """
    Simulates various attack scenarios for security testing
    - Port scanning
    - DDoS simulation (controlled)
    - Brute force attempts
    - Network reconnaissance

    WARNING: Only use on authorized networks!
    """

    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(name="AttackSimulator", agent_id=agent_id)
        self.simulations = []
        self.is_simulation_running = False
        self.allowed_targets = []  # Whitelist of targets

    async def start(self) -> None:
        """Start attack simulator agent"""
        logger.info("⚔️ Starting Attack Simulator Agent")

        try:
            self.is_running = True
            self.start_time = datetime.now()
            await self._set_status("ready")

            logger.success("✅ Attack Simulator ready for simulations")

        except Exception as e:
            logger.error(f"❌ Failed to start Attack Simulator: {e}")
            await self._set_status("error")
            self.metrics["errors"] += 1
            raise

    async def stop(self) -> None:
        """Stop attack simulator"""
        logger.info("🛑 Stopping Attack Simulator...")
        self.is_running = False
        self.is_simulation_running = False
        await self._set_status("stopped")
        logger.success("✅ Attack Simulator stopped")

    async def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process simulation request"""
        simulation_type = event.get("type")

        if simulation_type == "port_scan":
            return await self.simulate_port_scan(
                target=event.get("target"),
                ports=event.get("ports", [])
            )
        elif simulation_type == "ddos":
            return await self.simulate_ddos(
                target=event.get("target"),
                duration=event.get("duration", 10)
            )
        elif simulation_type == "ping_sweep":
            return await self.simulate_ping_sweep(
                network=event.get("network")
            )

        return {"error": "Unknown simulation type"}

    async def simulate_port_scan(
        self,
        target: str,
        ports: List[int] = None,
        scan_type: str = "syn"
    ) -> Dict[str, Any]:
        """
        Simulate port scanning attack

        Args:
            target: Target IP address
            ports: List of ports to scan (default: common ports)
            scan_type: Type of scan (syn, connect, udp)
        """
        logger.info(f"🔍 Starting port scan simulation on {target}")

        if not await self._validate_target(target):
            return {"error": "Target not in allowed list"}

        if ports is None:
            ports = [21, 22, 23, 25, 80, 443, 3389, 8080]

        self.is_simulation_running = True
        open_ports = []
        closed_ports = []

        try:
            for port in ports:
                if not self.is_simulation_running:
                    break

                result = await self._scan_port(target, port, scan_type)

                if result["open"]:
                    open_ports.append(port)
                    logger.debug(f"✓ Port {port} is OPEN on {target}")
                else:
                    closed_ports.append(port)

                await asyncio.sleep(0.1)  # Delay between scans

            simulation_result = {
                "simulation_id": f"sim_{datetime.now().timestamp()}",
                "type": "port_scan",
                "target": target,
                "scan_type": scan_type,
                "timestamp": datetime.now().isoformat(),
                "total_ports": len(ports),
                "open_ports": open_ports,
                "closed_ports": closed_ports,
                "status": "completed"
            }

            self.simulations.append(simulation_result)
            self.metrics["events_processed"] += 1

            logger.success(f"✅ Port scan completed: {len(open_ports)} open ports found")
            return simulation_result

        except Exception as e:
            logger.error(f"❌ Port scan error: {e}")
            self.metrics["errors"] += 1
            return {"error": str(e), "status": "failed"}
        finally:
            self.is_simulation_running = False

    async def _scan_port(
        self,
        target: str,
        port: int,
        scan_type: str
    ) -> Dict[str, Any]:
        """Scan a single port"""
        try:
            if scan_type == "syn":
                # SYN scan (stealthy)
                pkt = IP(dst=target)/TCP(dport=port, flags="S")
                resp = sr1(pkt, timeout=1, verbose=0)

                if resp and resp.haslayer(TCP):
                    if resp[TCP].flags == 0x12:  # SYN-ACK
                        # Send RST to close connection
                        send(IP(dst=target)/TCP(dport=port, flags="R"), verbose=0)
                        return {"open": True, "response": "SYN-ACK"}

                return {"open": False, "response": "closed"}

            elif scan_type == "connect":
                # Full TCP connect
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                sock.close()
                return {"open": result == 0, "response": "connected" if result == 0 else "refused"}

            elif scan_type == "udp":
                # UDP scan
                pkt = IP(dst=target)/UDP(dport=port)
                resp = sr1(pkt, timeout=1, verbose=0)
                return {"open": resp is None, "response": "open|filtered" if resp is None else "closed"}

        except Exception as e:
            logger.debug(f"Port scan error on {target}:{port} - {e}")
            return {"open": False, "error": str(e)}

    async def simulate_ddos(
        self,
        target: str,
        duration: int = 10,
        packet_rate: int = 100
    ) -> Dict[str, Any]:
        """
        Simulate DDoS attack (controlled, low volume)

        WARNING: Only use on authorized networks!
        """
        logger.warning(f"⚠️ Starting DDoS simulation on {target} for {duration}s")

        if not await self._validate_target(target):
            return {"error": "Target not in allowed list"}

        self.is_simulation_running = True
        packets_sent = 0
        start_time = datetime.now()

        try:
            while (datetime.now() - start_time).seconds < duration:
                if not self.is_simulation_running:
                    break

                # Send SYN flood packets
                for _ in range(packet_rate):
                    pkt = IP(dst=target)/TCP(dport=80, flags="S")
                    send(pkt, verbose=0)
                    packets_sent += 1

                await asyncio.sleep(1)

            simulation_result = {
                "simulation_id": f"sim_{datetime.now().timestamp()}",
                "type": "ddos",
                "target": target,
                "duration_seconds": duration,
                "packets_sent": packets_sent,
                "packet_rate": packet_rate,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }

            self.simulations.append(simulation_result)
            self.metrics["events_processed"] += 1

            logger.success(f"✅ DDoS simulation completed: {packets_sent} packets sent")
            return simulation_result

        except Exception as e:
            logger.error(f"❌ DDoS simulation error: {e}")
            self.metrics["errors"] += 1
            return {"error": str(e), "status": "failed"}
        finally:
            self.is_simulation_running = False

    async def simulate_ping_sweep(self, network: str) -> Dict[str, Any]:
        """
        Simulate network reconnaissance via ping sweep

        Args:
            network: Network CIDR (e.g., "192.168.1.0/24")
        """
        logger.info(f"🔍 Starting ping sweep on network {network}")

        try:
            net = ipaddress.ip_network(network, strict=False)
            alive_hosts = []
            dead_hosts = []

            for ip in list(net.hosts())[:50]:  # Limit to first 50 hosts
                if not self.is_simulation_running:
                    break

                # Send ICMP echo request
                pkt = IP(dst=str(ip))/ICMP()
                resp = sr1(pkt, timeout=1, verbose=0)

                if resp:
                    alive_hosts.append(str(ip))
                    logger.debug(f"✓ Host {ip} is alive")
                else:
                    dead_hosts.append(str(ip))

                await asyncio.sleep(0.1)

            simulation_result = {
                "simulation_id": f"sim_{datetime.now().timestamp()}",
                "type": "ping_sweep",
                "network": network,
                "alive_hosts": alive_hosts,
                "total_scanned": len(alive_hosts) + len(dead_hosts),
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }

            self.simulations.append(simulation_result)
            self.metrics["events_processed"] += 1

            logger.success(f"✅ Ping sweep completed: {len(alive_hosts)} hosts alive")
            return simulation_result

        except Exception as e:
            logger.error(f"❌ Ping sweep error: {e}")
            self.metrics["errors"] += 1
            return {"error": str(e), "status": "failed"}

    async def _validate_target(self, target: str) -> bool:
        """Validate if target is in allowed list"""
        # In production, check against whitelist
        # For now, allow local network only
        try:
            ip = ipaddress.ip_address(target)
            return ip.is_private or ip.is_loopback
        except:
            return False

    async def get_simulations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent simulations"""
        return self.simulations[-limit:] if self.simulations else []

    async def stop_simulation(self) -> Dict[str, Any]:
        """Stop current running simulation"""
        if self.is_simulation_running:
            self.is_simulation_running = False
            logger.warning("🛑 Simulation stopped by user")
            return {"status": "stopped", "message": "Simulation terminated"}
        return {"status": "no_simulation", "message": "No simulation running"}
