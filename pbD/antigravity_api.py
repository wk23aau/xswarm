"""
Antigravity API - Python Client
================================
Works for: StartCascade, StreamCascadeReactiveUpdates, LogEvent
Blocked: SendUserCascadeMessage (use bridge for this)

Usage:
    from antigravity_api import AntigravityAPI
    api = AntigravityAPI(port=63920, csrf_token='...', oauth_token='...')
    cascade_id = api.start_cascade()
    chunks = api.stream_updates(cascade_id, duration=5)
"""

import struct
import requests
import threading
import re
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def encode_varint(n):
    result = b''
    while n > 127:
        result += bytes([(n & 0x7F) | 0x80])
        n >>= 7
    result += bytes([n])
    return result


def encode_string(field, value):
    data = value.encode('utf-8')
    return bytes([field << 3 | 2]) + encode_varint(len(data)) + data


def encode_submsg(field, content):
    return bytes([field << 3 | 2]) + encode_varint(len(content)) + content


def encode_bool(field, value):
    return bytes([field << 3 | 0, 1 if value else 0])


def connect_envelope(proto_data, flags=0):
    return bytes([flags]) + struct.pack('>I', len(proto_data)) + proto_data


class AntigravityAPI:
    def __init__(self, port, csrf_token, oauth_token):
        self.port = port
        self.csrf_token = csrf_token
        self.oauth_token = oauth_token
        self.base_url = f'https://127.0.0.1:{port}'
        self.session = requests.Session()
        
        self.base_headers = {
            'Connect-Protocol-Version': '1',
            'x-codeium-csrf-token': csrf_token,
            'Origin': 'vscode-file://vscode-app',
        }
    
    def _build_auth(self):
        auth = encode_string(1, 'antigravity')
        auth += encode_string(3, self.oauth_token)
        auth += encode_string(4, 'en')
        auth += encode_string(5, '1.14.2b')
        auth += encode_string(6, 'antigravity')
        return auth
    
    def start_cascade(self):
        """Start a new cascade. Returns cascade ID."""
        url = f'{self.base_url}/exa.language_server_pb.LanguageServerService/StartCascade'
        
        proto = encode_submsg(1, self._build_auth())
        proto += encode_bool(4, True)
        
        headers = {**self.base_headers, 'Content-Type': 'application/proto'}
        
        r = self.session.post(url, headers=headers, data=proto, verify=False, timeout=30)
        
        if r.status_code == 200:
            text = r.content.decode('latin-1')
            match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', text)
            if match:
                return match.group(0)
        return None
    
    def stream_updates(self, cascade_id, channel='chat-client-trajectories', duration=10):
        """Stream updates from a cascade. Returns list of data chunks."""
        url = f'{self.base_url}/exa.language_server_pb.LanguageServerService/StreamCascadeReactiveUpdates'
        
        proto = encode_bool(1, True)
        proto += encode_string(2, cascade_id)
        proto += encode_string(3, channel)
        
        payload = connect_envelope(proto)
        
        headers = {**self.base_headers, 'Content-Type': 'application/connect+proto'}
        
        chunks = []
        
        def stream():
            try:
                r = self.session.post(
                    url, headers=headers, data=payload,
                    verify=False, timeout=duration + 5, stream=True
                )
                if r.status_code == 200:
                    for chunk in r.iter_content(chunk_size=None):
                        if chunk:
                            chunks.append(chunk)
            except:
                pass
        
        thread = threading.Thread(target=stream, daemon=True)
        thread.start()
        thread.join(timeout=duration)
        
        return chunks
    
    def log_event(self, event_type, mode='editor'):
        """Log a UI event."""
        url = f'{self.base_url}/exa.extension_server_pb.ExtensionServerService/LogEvent'
        
        proto = b'\x08A\x12\x1e\n\x04type\x12\x16' + event_type.encode()[:22]
        proto += b'\x12\x0e\n\x04mode\x12\x06' + mode.encode()[:6]
        
        headers = {**self.base_headers, 'Content-Type': 'application/proto'}
        
        r = self.session.post(url, headers=headers, data=proto, verify=False, timeout=10)
        return r.status_code == 200


# Default config - UPDATE THESE VALUES from Network tab!
DEFAULT_CONFIG = {
    'port': 63920,
    'csrf_token': 'YOUR_CSRF_TOKEN_HERE',  # Get from x-codeium-csrf-token header
    'oauth_token': 'YOUR_OAUTH_TOKEN_HERE',  # Get from protobuf body (ya29....)
}


def get_default_config():
    return DEFAULT_CONFIG.copy()


if __name__ == '__main__':
    print("Antigravity API Demo")
    print("=" * 40)
    
    api = AntigravityAPI(**get_default_config())
    
    print("\n1. StartCascade...")
    cascade_id = api.start_cascade()
    if cascade_id:
        print(f"   ✅ Cascade: {cascade_id}")
    else:
        print("   ❌ Failed (update tokens)")
        exit(1)
    
    print("\n2. StreamCascadeReactiveUpdates (3 sec)...")
    chunks = api.stream_updates(cascade_id, duration=3)
    print(f"   ✅ Received {len(chunks)} chunks")
    
    print("\n3. LogEvent...")
    if api.log_event('api-test'):
        print("   ✅ Logged")
    
    print("\n" + "=" * 40)
    print("For sending messages, use the bridge!")
