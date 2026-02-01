"""
Cloudflare Tunnel URL Auto-Update Utility
Call this from voice_gateway.py on startup
"""
import os
import re
import subprocess
import time
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv, set_key

def get_cloudflare_url():
    """
    Get Cloudflare tunnel URL from multiple sources:
    1. Docker logs (if running in Docker)
    2. VOICE_GATEWAY_URL env var
    3. Return None if not found
    """
    
    # First try Docker logs
    try:
        result = subprocess.run(
            ['docker', 'logs', 'relayx-cloudflare-tunnel', '--tail', '100'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        logs = result.stdout + result.stderr
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', logs)
        
        if match:
            url = match.group(0)
            logger.info(f"✅ Found Cloudflare URL from Docker logs: {url}")
            return url
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        logger.debug("Docker not available or container not running")
    
    # Fall back to env var
    env_url = os.getenv("VOICE_GATEWAY_URL")
    if env_url and "trycloudflare.com" in env_url:
        logger.info(f"✅ Using VOICE_GATEWAY_URL from env: {env_url}")
        return env_url
    
    logger.warning("⚠️ No Cloudflare URL found")
    return None

def update_voice_gateway_url_in_env(new_url: str) -> bool:
    """
    Update VOICE_GATEWAY_URL in .env file
    
    Args:
        new_url: The new Cloudflare tunnel URL
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Find .env file (one level up from voice_gateway/)
        env_path = Path(__file__).parent.parent / '.env'
        
        if not env_path.exists():
            logger.error(f".env file not found at {env_path}")
            return False
        
        # Update the env file
        set_key(str(env_path), "VOICE_GATEWAY_URL", new_url)
        
        # Also update the current process environment
        os.environ["VOICE_GATEWAY_URL"] = new_url
        
        logger.info(f"✅ Updated VOICE_GATEWAY_URL: {new_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update VOICE_GATEWAY_URL: {e}")
        return False

def auto_detect_and_update_tunnel_url():
    """
    Auto-detect Cloudflare tunnel URL and update environment
    Call this on voice gateway startup
    """
    logger.info("🔍 Auto-detecting Cloudflare tunnel URL...")
    
    # Try to get current URL
    current_url = get_cloudflare_url()
    
    if current_url:
        # Update env file if needed
        env_url = os.getenv("VOICE_GATEWAY_URL")
        
        if env_url != current_url:
            logger.info(f"🔄 Updating tunnel URL: {env_url} → {current_url}")
            update_voice_gateway_url_in_env(current_url)
        else:
            logger.info("✓ Tunnel URL already up to date")
        
        return current_url
    else:
        logger.warning("⚠️ Could not auto-detect Cloudflare URL. Manual configuration may be required.")
        return None

if __name__ == "__main__":
    # Test the auto-detection
    load_dotenv()
    url = auto_detect_and_update_tunnel_url()
    if url:
        print(f"\n✅ Detected URL: {url}")
    else:
        print("\n❌ Could not detect Cloudflare URL")
