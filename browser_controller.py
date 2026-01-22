"""
xswarm Browser Controller

Standalone browser automation with complete state tracking.
Provides AI agents with full browser context for decision-making.
"""

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from typing import Dict, List, Optional
import json
import time
from datetime import datetime

class BrowserState:
    """Complete browser state for AI context"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: Dict[str, Page] = {}  # page_id -> Page
        self.active_page_id: Optional[str] = None
        self.playwright = None
        
    def to_dict(self) -> dict:
        """Serialize browser state for AI"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_page": self.active_page_id,
            "pages": [
                {
                    "id": page_id,
                    "url": page.url,
                    "title": page.title(),
                    "is_active": page_id == self.active_page_id,
                    "viewport": page.viewport_size
                }
                for page_id, page in self.pages.items()
            ],
            "total_pages": len(self.pages)
        }

class BrowserController:
    """Browser automation controller for xswarm agents"""
    
    def __init__(self):
        self.state = BrowserState()
        
    def start(self, headless: bool = False):
        """Start browser"""
        self.state.playwright = sync_playwright().start()
        self.state.browser = self.state.playwright.chromium.launch(headless=headless)
        self.state.context = self.state.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        print("✅ Browser started")
        
    def new_tab(self, url: str = "about:blank") -> str:
        """Create new tab, return page_id"""
        page = self.state.context.new_page()
        page_id = f"page_{len(self.state.pages) + 1}"
        self.state.pages[page_id] = page
        self.state.active_page_id = page_id
        
        if url != "about:blank":
            page.goto(url)
        
        print(f"✅ New tab created: {page_id}")
        return page_id
    
    def switch_tab(self, page_id: str) -> bool:
        """Switch to specific tab"""
        if page_id in self.state.pages:
            self.state.active_page_id = page_id
            self.state.pages[page_id].bring_to_front()
            print(f"✅ Switched to tab: {page_id}")
            return True
        return False
    
    def close_tab(self, page_id: str) -> bool:
        """Close specific tab"""
        if page_id in self.state.pages:
            self.state.pages[page_id].close()
            del self.state.pages[page_id]
            
            # Switch to another tab if this was active
            if self.state.active_page_id == page_id:
                if self.state.pages:
                    self.state.active_page_id = list(self.state.pages.keys())[0]
                else:
                    self.state.active_page_id = None
            
            print(f"✅ Closed tab: {page_id}")
            return True
        return False
    
    def get_active_page(self) -> Optional[Page]:
        """Get currently active page"""
        if self.state.active_page_id:
            return self.state.pages.get(self.state.active_page_id)
        return None
    
    def execute_action(self, action: dict) -> dict:
        """
        Execute browser action suggested by AI.
        
        Action format:
        {
            "type": "click|type|scroll|navigate|wait|screenshot|new_tab|switch_tab|close_tab",
            "page_id": "optional - defaults to active",
            "x": 100,  # for click
            "y": 200,  # for click
            "text": "text to type",  # for type
            "url": "https://...",  # for navigate
            "scroll_y": 500,  # for scroll
            "selector": "optional CSS selector",
            "wait_ms": 1000  # for wait
        }
        
        Returns:
        {
            "status": "success|error",
            "message": "description",
            "new_state": {...}  # Updated browser state
        }
        """
        page = self.get_active_page()
        if not page and action["type"] not in ["new_tab"]:
            return {"status": "error", "message": "No active page"}
        
        try:
            action_type = action["type"]
            
            if action_type == "navigate":
                page.goto(action["url"])
                return {"status": "success", "message": f"Navigated to {action['url']}"}
            
            elif action_type == "click":
                if "selector" in action:
                    page.click(action["selector"])
                else:
                    page.mouse.click(action["x"], action["y"])
                return {"status": "success", "message": f"Clicked at ({action.get('x')}, {action.get('y')})"}
            
            elif action_type == "type":
                if "selector" in action:
                    page.fill(action["selector"], action["text"])
                else:
                    page.keyboard.type(action["text"])
                return {"status": "success", "message": f"Typed: {action['text'][:50]}..."}
            
            elif action_type == "scroll":
                page.evaluate(f"window.scrollBy(0, {action.get('scroll_y', 500)})")
                return {"status": "success", "message": f"Scrolled {action.get('scroll_y')} pixels"}
            
            elif action_type == "wait":
                time.sleep(action.get("wait_ms", 1000) / 1000)
                return {"status": "success", "message": f"Waited {action.get('wait_ms')}ms"}
            
            elif action_type == "screenshot":
                path = action.get("path", f"screenshot_{int(time.time())}.png")
                page.screenshot(path=path)
                return {"status": "success", "message": f"Screenshot saved: {path}", "path": path}
            
            elif action_type == "new_tab":
                page_id = self.new_tab(action.get("url", "about:blank"))
                return {"status": "success", "message": f"Created tab: {page_id}", "page_id": page_id}
            
            elif action_type == "switch_tab":
                if self.switch_tab(action["page_id"]):
                    return {"status": "success", "message": f"Switched to: {action['page_id']}"}
                return {"status": "error", "message": "Tab not found"}
            
            elif action_type == "close_tab":
                if self.close_tab(action.get("page_id", self.state.active_page_id)):
                    return {"status": "success", "message": "Tab closed"}
                return {"status": "error", "message": "Failed to close tab"}
            
            else:
                return {"status": "error", "message": f"Unknown action: {action_type}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_context_for_ai(self) -> dict:
        """
        Get complete browser context for AI decision-making.
        
        Returns comprehensive state including:
        - All tabs with URLs, titles
        - Active tab info
        - Current page screenshot
        - DOM snapshot
        """
        page = self.get_active_page()
        
        context = {
            "browser_state": self.state.to_dict(),
            "current_page": None
        }
        
        if page:
            context["current_page"] = {
                "url": page.url,
                "title": page.title(),
                "viewport": page.viewport_size,
                "html": page.content()[:5000],  # First 5KB of HTML
                "screenshot": None  # Will be filled if requested
            }
        
        return context
    
    def stop(self):
        """Stop browser"""
        if self.state.context:
            self.state.context.close()
        if self.state.browser:
            self.state.browser.close()
        if self.state.playwright:
            self.state.playwright.stop()
        print("✅ Browser stopped")


# Example usage
if __name__ == "__main__":
    controller = BrowserController()
    controller.start(headless=False)
    
    # Create tab
    controller.new_tab("https://example.com")
    
    # Get state for AI
    state = controller.get_context_for_ai()
    print(json.dumps(state, indent=2))
    
    # Execute AI-suggested actions
    result = controller.execute_action({
        "type": "click",
        "x": 100,
        "y": 200
    })
    print(result)
    
    controller.stop()
