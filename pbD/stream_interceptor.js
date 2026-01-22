// ANTIGRAVITY STREAM INTERCEPTOR
// ===============================
// Captures AI responses from StreamCascadeReactiveUpdates
// Paste in DevTools BEFORE sending messages

(() => {
    const responseBuffer = [];
    const originalFetch = window._origFetch || window.fetch;
    window._origFetch = originalFetch;

    window.fetch = async function (...args) {
        const response = await originalFetch.apply(this, args);
        const url = typeof args[0] === 'string' ? args[0] : args[0].url;

        // Intercept streaming responses
        if (url.includes('StreamCascadeReactiveUpdates')) {
            console.log('📡 Streaming intercepted:', url.split('/').pop());

            const clone = response.clone();
            (async () => {
                try {
                    const reader = clone.body.getReader();
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        // Extract readable text from protobuf
                        const raw = new TextDecoder('latin1').decode(value);
                        const matches = raw.match(/[\x20-\x7E]{15,}/g) || [];

                        for (const text of matches) {
                            // Filter out tokens and IDs
                            if (!text.match(/^[A-Za-z0-9+/=_-]{30,}$/) &&
                                !text.match(/^[0-9a-f-]{36}$/)) {
                                console.log('📥', text.slice(0, 100));
                                responseBuffer.push({
                                    time: Date.now(),
                                    text: text
                                });
                            }
                        }
                    }
                } catch (e) {
                    // Stream ended
                }
            })();
        }

        return response;
    };

    // Export functions
    window.getResponses = () => responseBuffer.map(r => r.text).join('\n');
    window.getRawResponses = () => responseBuffer;
    window.clearResponses = () => { responseBuffer.length = 0; };

    console.log('📡 Stream interceptor ready');
    console.log('   getResponses()      - Get captured AI text');
    console.log('   getRawResponses()   - Get raw capture data');
    console.log('   clearResponses()    - Clear buffer');
})();
