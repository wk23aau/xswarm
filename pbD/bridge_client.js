// ANTIGRAVITY UI BRIDGE CLIENT
// =============================
// Paste this in Antigravity DevTools Console (chat.js frame)
// Works by simulating UI interaction - guaranteed to work!
//
// Commands:
//   window.send('message')  - Send a message
//   window.stopBridge()     - Stop polling

(() => {
    const BRIDGE_URL = 'http://127.0.0.1:8765';
    let active = true;

    // Send message via UI simulation
    async function sendMessage(text) {
        const input = document.querySelector('[contenteditable="true"][data-lexical-editor]');

        if (!input) {
            console.log('❌ Input not found');
            return { success: false, error: 'Input not found' };
        }

        // Clear and type
        input.focus();
        input.innerHTML = `<p class="text-sm">${text}</p>`;
        input.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText' }));

        // Wait for UI to update
        await new Promise(r => setTimeout(r, 100));

        // Find and click submit button
        const btn = document.querySelector('button:has(svg.lucide-arrow-right):not([disabled])');
        if (!btn) {
            console.log('❌ Submit button not found');
            return { success: false, error: 'No submit button' };
        }

        btn.click();
        console.log(`✅ Sent: "${text.slice(0, 50)}${text.length > 50 ? '...' : ''}"`);
        return { success: true };
    }

    // Poll for commands from Python bridge
    async function poll() {
        while (active) {
            try {
                const r = await fetch(`${BRIDGE_URL}/poll`, { signal: AbortSignal.timeout(5000) });
                const data = await r.json();

                if (data.command?.type === 'send') {
                    const result = await sendMessage(data.command.message);
                    await fetch(`${BRIDGE_URL}/result`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(result)
                    });
                }
            } catch (e) {
                // Bridge not running - continue polling
            }
            await new Promise(r => setTimeout(r, 500));
        }
    }

    // Export functions
    window.send = sendMessage;
    window.stopBridge = () => { active = false; console.log('Bridge stopped'); };

    // Start polling
    poll();

    console.log(`
╔════════════════════════════════════════════════════════════╗
║  🎮 ANTIGRAVITY UI BRIDGE                                  ║
╠════════════════════════════════════════════════════════════╣
║  Manual:  window.send('Hello!')                            ║
║  Python:  Run antigravity_bridge.py first                  ║
║  Stop:    window.stopBridge()                              ║
╚════════════════════════════════════════════════════════════╝
    `);
})();
