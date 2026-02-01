"""
Auto-update Cloudflare Tunnel URL
Monitors the Cloudflare tunnel and automatically updates VOICE_GATEWAY_URL
"""
import os
import re
import time
import subprocess
import requests
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv, set_key

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_cloudflare_url_from_logs():
    """Extract Cloudflare URL from Docker logs"""
    try:
        result = subprocess.run(
            ['docker', 'logs', 'relayx-cloudflare-tunnel'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        logs = result.stdout + result.stderr
        
        # Look for trycloudflare.com URL
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', logs)
        if match:
            return match.group(0)
        
        return None
    except Exception as e:
        logger.error(f"Failed to get Cloudflare URL from logs: {e}")
        return None

def get_current_env_url():
    """Get current VOICE_GATEWAY_URL from .env"""
    return os.getenv("VOICE_GATEWAY_URL", "")

def update_env_file(new_url):
    """Update VOICE_GATEWAY_URL in .env file"""
    try:
        set_key(env_path, "VOICE_GATEWAY_URL", new_url)
        logger.info(f"✅ Updated .env: VOICE_GATEWAY_URL={new_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to update .env: {e}")
        return False

def restart_services():
    """Restart backend and voice gateway services"""
    try:
        # Restart backend
        subprocess.run(
            ['docker', 'restart', 'relayx-backend'],
            check=True,
            timeout=30
        )
        logger.info("✅ Restarted backend service")
        
        # Restart voice gateway
        subprocess.run(
            ['docker', 'restart', 'relayx-voice-gateway'],
            check=True,
            timeout=30
        )
        logger.info("✅ Restarted voice gateway service")
        
        return True
    except Exception as e:
        logger.error(f"Failed to restart services: {e}")
        return False

def monitor_and_update(check_interval=30):
    """
    Monitor Cloudflare tunnel URL and auto-update when it changes
    
    Args:
        check_interval: Seconds between checks (default 30)
    """
    logger.info("🔄 Starting Cloudflare URL auto-update monitor...")
    logger.info(f"⏰ Check interval: {check_interval} seconds")
    
    last_url = get_current_env_url()
    logger.info(f"Current URL: {last_url}")
    
    while True:
        try:
            # Get current Cloudflare URL
            current_url = get_cloudflare_url_from_logs()
            
            if not current_url:
                logger.warning("⚠️ Could not detect Cloudflare URL, retrying...")
                time.sleep(check_interval)
                continue
            
            # Check if URL changed
            if current_url != last_url:
                logger.info(f"🔄 URL changed!")
                logger.info(f"   Old: {last_url}")
                logger.info(f"   New: {current_url}")
                
                # Update .env file
                if update_env_file(current_url):
                    # Restart services to pick up new URL
                    if restart_services():
                        logger.info("✅ Services updated with new Cloudflare URL")
                        last_url = current_url
                    else:
                        logger.error("❌ Failed to restart services")
                else:
                    logger.error("❌ Failed to update .env file")
            else:
                logger.debug(f"✓ URL unchanged: {current_url}")
            
            # Wait before next check
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logger.info("\n👋 Stopping monitor...")
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            time.sleep(check_interval)

if __name__ == "__main__":
    # Monitor every 30 seconds
    monitor_and_update(check_interval=30)
