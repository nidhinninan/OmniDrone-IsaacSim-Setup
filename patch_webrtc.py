#!/usr/bin/env python3
"""
Patch Isaac Sim 4.1.0's WebRTC client to use STUN/TURN servers for NAT traversal.
This enables WebRTC streaming from Brev cloud instances to local browsers.

Usage:
  1. Get your public IP: curl -s ifconfig.me
  2. Edit the variables below (PUBLIC_IP and TURN_PASSWORD)
  3. Run: python3 patch_webrtc.py
"""

import shutil
from pathlib import Path

# ============ EDIT THESE VALUES ============
PUBLIC_IP = "54.158.162.11"              # Your Brev public IP
TURN_USERNAME = "webrtc"
TURN_PASSWORD = "omnidrone2026"          # Your coturn password
# ===========================================

# File to patch (auto-detected)
JS_FILE = Path("/home/ubuntu/OmniDrone/isaac-sim-4.1.0/extscache/omni.services.streamclient.webrtc-1.3.8/web/js/kit-player.js")

def main():
    # Validation
    if PUBLIC_IP == "YOUR_BREV_PUBLIC_IP" or TURN_PASSWORD == "YOUR_TURN_PASSWORD":
        print("❌ ERROR: Please edit the script and set PUBLIC_IP and TURN_PASSWORD!")
        print(f"\n📝 Edit: nano {Path(__file__)}")
        print(f"🌐 Get IP: curl -s ifconfig.me")
        return 1
    
    print(f"[1/5] Reading: {JS_FILE}")
    if not JS_FILE.exists():
        print(f"❌ ERROR: File not found: {JS_FILE}")
        return 1
    
    text = JS_FILE.read_text()
    
    # Check if already patched
    if "OV_ICE_CONFIG" in text:
        print("[2/5] ⚠️  Already patched! Skipping.")
        return 0
    
    # Backup original
    backup = JS_FILE.with_suffix('.js.backup')
    if not backup.exists():
        print(f"[2/5] Creating backup: {backup}")
        shutil.copy(JS_FILE, backup)
    else:
        print(f"[2/5] Using existing backup: {backup}")
    
    # Insert config constant near the top
    print("[3/5] Injecting OV_ICE_CONFIG constant...")
    insert_at = text.find('"use strict";')
    if insert_at != -1:
        insert_at = text.find("\n", insert_at) + 1
    else:
        insert_at = 0
    
    config_block = f"""const OV_ICE_CONFIG = {{
  iceServers: [
    {{ urls: "stun:stun.l.google.com:19302" }},
    {{ urls: "stun:stun1.l.google.com:19302" }},
    {{
      urls: "turn:{PUBLIC_IP}:3478",
      username: "{TURN_USERNAME}",
      credential: "{TURN_PASSWORD}"
    }}
  ]
}};
"""
    
    text = text[:insert_at] + config_block + text[insert_at:]
    
    # Replace all RTCPeerConnection() calls
    print("[4/5] Replacing new RTCPeerConnection() calls...")
    text = text.replace("new RTCPeerConnection()", "new RTCPeerConnection(OV_ICE_CONFIG)")
    
    # Write back
    JS_FILE.write_text(text)
    
    print(f"[5/5] ✅ Patch applied successfully!")
    print(f"\n📋 Summary:")
    print(f"   STUN: stun.l.google.com:19302")
    print(f"   TURN: {PUBLIC_IP}:3478 (user: {TURN_USERNAME})")
    print(f"\n🔄 To restore original: cp {backup} {JS_FILE}")
    return 0

if __name__ == "__main__":
    exit(main())
