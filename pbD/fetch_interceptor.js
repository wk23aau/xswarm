// ANTIGRAVITY FETCH INTERCEPTOR
// ==============================
// Paste in DevTools Console to capture all API requests/responses
// Useful for debugging and finding tokens

(() => {
    const originalFetch = window._origFetch || window.fetch;
    window._origFetch = originalFetch;

    window.fetch = async function (...args) {
        const [url, options] = args;
        const urlStr = typeof url === 'string' ? url : url.url;

        // Log interesting requests
        if (urlStr.includes('127.0.0.1') && urlStr.includes('exa.')) {
            const endpoint = urlStr.split('/').pop();
            console.log('========================================');
            console.log('🔍 INTERCEPTED:', endpoint);
            console.log('========================================');
            console.log('URL:', urlStr);

            // Log headers
            if (options?.headers) {
                console.log('HEADERS:');
                const headers = options.headers instanceof Headers
                    ? Object.fromEntries(options.headers)
                    : options.headers;
                for (const [k, v] of Object.entries(headers)) {
                    console.log(`  ${k}: ${v}`);
                }
            }

            // Log body info
            if (options?.body) {
                if (options.body instanceof Uint8Array) {
                    console.log('BODY:', options.body.length, 'bytes');
                    console.log('HEX:', Array.from(options.body.slice(0, 50))
                        .map(b => b.toString(16).padStart(2, '0')).join(' '));
                }
            }

            // Store for analysis
            window.lastRequest = { url: urlStr, options };
        }

        // Call original fetch
        const response = await originalFetch.apply(this, args);

        // Log response for key endpoints
        if (urlStr.includes('SendUserCascadeMessage')) {
            console.log('RESPONSE:', response.status, response.statusText);
        }

        return response;
    };

    console.log('🎯 Fetch interceptor installed');
    console.log('   All API requests will be logged');
    console.log('   window.lastRequest = last captured request');
})();
