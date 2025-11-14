"""
Test Discord Webhook Integration
"""

import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


async def test_discord_notification():
    """Test sending a message to Discord"""

    webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')

    if not webhook_url or 'YOUR_WEBHOOK' in webhook_url:
        print("❌ Discord Webhook URL chưa được cấu hình!")
        print("\nVui lòng:")
        print("1. Tạo webhook trong Discord Server Settings → Integrations → Webhooks")
        print("2. Copy webhook URL")
        print("3. Thay thế giá trị DISCORD_WEBHOOK_URL trong file .env")
        return False

    print(f"🔍 Testing Discord webhook...")
    print(f"📡 Webhook URL: {webhook_url[:50]}...")

    # Test message with beautiful embed format
    embed = {
        "embeds": [{
            "author": {
                "name": "Roma Security Cyber Agent System",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/6195/6195699.png"
            },
            "title": "🟢 DISCORD INTEGRATION TEST - SUCCESS",
            "description": "**Connection Test** has been successfully completed",
            "color": 0x00FF00,  # Green
            "fields": [
                {
                    "name": "📡 Connection Status",
                    "value": "`✅ Connected`",
                    "inline": True
                },
                {
                    "name": "🤖 System",
                    "value": "`Roma Security Agent`",
                    "inline": True
                },
                {
                    "name": "⏰ Test Time",
                    "value": f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                    "inline": True
                },
                {
                    "name": "✨ Status",
                    "value": "Hệ thống thông báo Discord đang hoạt động bình thường!\n\n🎯 Format mới với embed fields đẹp hơn\n📊 Hiển thị thông tin rõ ràng và có tổ chức\n🎨 Màu sắc theo mức độ nghiêm trọng",
                    "inline": False
                }
            ],
            "footer": {
                "text": "⚡ Powered by Roma AI Security • Real-time Threat Detection",
                "icon_url": "https://cdn-icons-png.flaticon.com/512/2092/2092665.png"
            },
            "timestamp": datetime.now().isoformat(),
            "thumbnail": {
                "url": "https://cdn-icons-png.flaticon.com/512/190/190411.png"
            }
        }]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=embed) as response:
                if response.status in [200, 204]:
                    print("✅ Test message sent successfully!")
                    print("\n📱 Kiểm tra Discord channel của bạn để xem tin nhắn test")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to send: {response.status}")
                    print(f"Error: {error_text}")
                    return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_severity_alerts():
    """Test different severity levels"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')

    if not webhook_url or 'YOUR_WEBHOOK' in webhook_url:
        return

    print("\n🎨 Testing severity levels...")

    severities = [
        ('low', 'Low Priority', 0x00FF00, '🟢'),
        ('medium', 'Medium Priority', 0xFFFF00, '🟡'),
        ('high', 'High Priority', 0xFF9900, '🟠'),
        ('critical', 'Critical Priority', 0xFF0000, '🔴')
    ]

    for severity, title, color, emoji in severities:
        embed = {
            "embeds": [{
                "author": {
                    "name": "Roma Security Cyber Agent System",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/6195/6195699.png"
                },
                "title": f"{emoji} SECURITY ALERT - {title.upper()}",
                "description": f"Test alert for **{severity}** severity level",
                "color": color,
                "fields": [
                    {
                        "name": "🎯 Source IP",
                        "value": "`192.168.1.100`",
                        "inline": True
                    },
                    {
                        "name": "🎯 Target IP",
                        "value": "`192.168.1.1`",
                        "inline": True
                    },
                    {
                        "name": "📡 Protocol",
                        "value": "`TCP`",
                        "inline": True
                    },
                    {
                        "name": "🤖 AI Analysis",
                        "value": f"This is a test {severity} severity alert. The system has detected potential security concerns that require attention.",
                        "inline": False
                    },
                    {
                        "name": "📈 Confidence Score",
                        "value": "`85%`",
                        "inline": True
                    },
                    {
                        "name": "⏰ Detection Time",
                        "value": f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "⚡ Powered by Roma AI Security • Real-time Threat Detection",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/2092/2092665.png"
                },
                "timestamp": datetime.now().isoformat(),
                "thumbnail": {
                    "url": "https://cdn-icons-png.flaticon.com/512/3064/3064197.png"
                }
            }]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=embed) as response:
                    if response.status in [200, 204]:
                        print(f"  ✓ {emoji} {severity.capitalize()} alert sent")
                    else:
                        print(f"  ✗ {severity.capitalize()} failed")
        except Exception as e:
            print(f"  ✗ Error sending {severity}: {e}")

        # Wait a bit between messages
        await asyncio.sleep(1)

    print("\n✅ Severity test completed!")


async def main():
    print("=" * 60)
    print("🧪 DISCORD WEBHOOK TEST - ROMA SECURITY SYSTEM")
    print("=" * 60)

    # Test basic connection
    success = await test_discord_notification()

    if success:
        print("\n" + "=" * 60)
        choice = input("\n💡 Bạn có muốn test các mức độ nghiêm trọng khác nhau? (y/n): ")
        if choice.lower() == 'y':
            await test_severity_alerts()

    print("\n" + "=" * 60)
    print("✨ Test hoàn tất!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
