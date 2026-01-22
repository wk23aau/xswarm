"""
Antigravity Bridge Server
=========================
Runs a local HTTP server that communicates with the DevTools bridge_client.js

Usage:
    python antigravity_bridge.py

    # In another terminal or script:
    from antigravity_bridge import AntigravityBridge
    bridge = AntigravityBridge()
    bridge.send("Hello!")
"""

import http.server
import json
import threading
import time
import requests


class BridgeHandler(http.server.BaseHTTPRequestHandler):
    command_queue = []
    result_queue = []
    
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def do_GET(self):
        if self.path == '/poll':
            cmd = None
            if BridgeHandler.command_queue:
                cmd = BridgeHandler.command_queue.pop(0)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'command': cmd}).encode())
    
    def do_POST(self):
        if self.path == '/result':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length)) if length else {}
            BridgeHandler.result_queue.append(data)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


class AntigravityBridge:
    def __init__(self, port=8765):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the bridge server."""
        self.server = http.server.HTTPServer(('127.0.0.1', self.port), BridgeHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"🌉 Bridge running on http://127.0.0.1:{self.port}")
        print("📋 Paste bridge_client.js in Antigravity DevTools")
    
    def stop(self):
        """Stop the bridge server."""
        if self.server:
            self.server.shutdown()
            print("Bridge stopped")
    
    def send(self, message, conversation_id=None, timeout=10):
        """Send a message through the bridge."""
        cmd = {'type': 'send', 'message': message}
        if conversation_id:
            cmd['conversationId'] = conversation_id
        
        BridgeHandler.command_queue.append(cmd)
        BridgeHandler.result_queue.clear()
        
        # Wait for result
        start = time.time()
        while time.time() - start < timeout:
            if BridgeHandler.result_queue:
                return BridgeHandler.result_queue.pop(0)
            time.sleep(0.1)
        
        return {'success': False, 'error': 'timeout'}
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()


if __name__ == '__main__':
    bridge = AntigravityBridge()
    bridge.start()
    
    print("\nBridge is ready!")
    print("Commands:")
    print("  bridge.send('message')  - Send a message")
    print("  bridge.stop()           - Stop the bridge")
    print("\nPress Ctrl+C to exit")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        bridge.stop()
