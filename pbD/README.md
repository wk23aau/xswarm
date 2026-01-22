# Antigravity API Research Findings

## Executive Summary

Reverse-engineered the Antigravity IDE's internal API. Found working endpoints for session management and streaming, but `SendUserCascadeMessage` is blocked for external clients due to HTTP/2 session binding.

---

## Working Endpoints ✅

| Endpoint | What it does | How to call |
|----------|-------------|-------------|
| `StartCascade` | Create new session | Python API works |
| `StreamCascadeReactiveUpdates` | Receive AI responses | Python API works |
| `LogEvent` | Log UI events | Python API works |
| `HandleCascadeUserInteraction` | Button clicks | Python API works |

---

## Blocked Endpoint ❌

| Endpoint | Issue |
|----------|-------|
| `SendUserCascadeMessage` | HTTP/2 session binding - only works from Antigravity's internal gRPC transport |

### Root Cause
Antigravity uses an internal gRPC-Web/Connect transport that maintains HTTP/2 connections. Even from within the same Electron process, new `fetch()` calls get `ERR_HTTP2_PROTOCOL_ERROR`.

---

## What We Discovered

### 1. API Details
- **Protocol**: Connect protocol (gRPC-Web variant)
- **Content-Type**: `application/proto` (unary) or `application/connect+proto` (streaming)
- **Auth**: OAuth token embedded in protobuf, CSRF token in header
- **Port**: Dynamic (found via HAR capture or network tab)

### 2. Headers Required
```
Connect-Protocol-Version: 1
Content-Type: application/proto
x-codeium-csrf-token: <csrf-token>
Origin: vscode-file://vscode-app
```

### 3. Protobuf Structure
Messages use standard protobuf encoding:
- Field 1: String (conversation ID or client name)
- Field 2: Submessage (message content)
- Field 3: Submessage (auth metadata)

---

## Available Solutions

### 1. Python API (Partial)
Works for: Creating sessions, receiving streams, logging events
Blocked for: Sending messages

### 2. UI Simulation Bridge
Works for: Everything (uses Antigravity's own transport)
Requires: DevTools script + Python bridge server

### 3. Stream Interception
Can capture AI responses by intercepting fetch in DevTools

---

## Files in This Package

| File | Purpose |
|------|---------|
| `antigravity_api.py` | Python API for working endpoints |
| `antigravity_bridge.py` | Python bridge server |
| `bridge_client.js` | DevTools script for UI automation |
| `stream_interceptor.js` | Capture AI responses |
| `fetch_interceptor.js` | Debug tool for request analysis |

---

## Usage

### Option 1: Python API (Limited)
```python
from antigravity_api import AntigravityAPI, get_default_config
api = AntigravityAPI(**get_default_config())

# Create session
cascade_id = api.start_cascade()

# Stream responses  
chunks = api.stream_updates(cascade_id, duration=5)
```

### Option 2: Full Bridge (Complete Access)
```bash
# Terminal 1
python antigravity_bridge.py

# DevTools Console
<paste bridge_client.js>

# Python
from antigravity_bridge import AntigravityBridge
bridge = AntigravityBridge()
bridge.send("Hello!")
```

---

## Key Learnings

1. **SendUserCascadeMessage is session-bound** - Can't be called from external HTTP clients
2. **UI simulation is reliable** - Using Antigravity's own UI bypasses all restrictions
3. **Stream interception works** - Can capture all AI responses
4. **Tokens refresh** - OAuth tokens expire; re-capture from network tab

---

## Future Work

- [ ] VS Code extension for proper integration
- [ ] Electron IPC injection for full control
- [ ] React fiber access for state manipulation
- [ ] WebSocket bridge as alternative
