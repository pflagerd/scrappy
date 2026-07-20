const puppeteer = require('puppeteer');
const express = require('express');
const fs = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'window-size.json');

function loadWindowSize() {
    try {
        if (fs.existsSync(configPath)) {
            return JSON.parse(fs.readFileSync(configPath, 'utf8'));
        }
    } catch (err) {
        console.error('Error loading config:', err);
    }
    return { width: 1920, height: 1080 };
}

(async () => {
    const app = express();
    app.use(express.static(__dirname));
    const server = app.listen(3000, () => {
        console.log('Server running on http://localhost:3000');
    });

    const windowSize = loadWindowSize();

    const browser = await puppeteer.launch({
        headless: false,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            `--window-size=${windowSize.width},${windowSize.height}`
        ],
        defaultViewport: null
    });

    const pages = await browser.pages();
    const page = pages[0];

    // Create browser-level CDP session for getting window bounds
    const client = await browser.target().createCDPSession();

    // Expose function to save window size
    await page.exposeFunction('saveWindowSize', async () => {
        try {
            const { windowId } = await client.send('Browser.getWindowForTarget', {
                targetId: page.target()._targetId
            });
            const { bounds } = await client.send('Browser.getWindowBounds', { windowId });

            fs.writeFileSync(configPath, JSON.stringify({
                width: bounds.width,
                height: bounds.height
            }, null, 2));
        } catch (err) {
            console.error('Error saving config:', err);
        }
    });

    // Inject resize listener
    await page.evaluateOnNewDocument(() => {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                window.saveWindowSize();
            }, 500); // Debounce for 500ms
        });
    });

    await page.goto('http://localhost:3000/index.html');

    browser.on('disconnected', () => {
        server.close();
    });
})();
