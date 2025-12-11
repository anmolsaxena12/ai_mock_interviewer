const path = require('path');

exports.config = {
    runner: 'local',
    specs: [
        './test/specs/**/*.e2e.js'
    ],
    exclude: [],
    maxInstances: 10,
    
    capabilities: [{
        maxInstances: 5,
        browserName: 'chrome',
        acceptInsecureCerts: true,
        'goog:chromeOptions': {
            args: [
                '--headless',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        }
    }],
    
    logLevel: 'info',
    bail: 0,
    baseUrl: 'http://localhost:5000',
    waitforTimeout: 10000,
    connectionRetryTimeout: 120000,
    connectionRetryCount: 3,
    
    services: ['chromedriver'],
    
    framework: 'mocha',
    reporters: ['spec'],
    
    mochaOpts: {
        ui: 'bdd',
        timeout: 60000
    },
    
    before: function (capabilities, specs) {
        // Set up any global test configuration here
    },
    
    afterTest: async function(test, context, { error, result, duration, passed, retries }) {
        if (!passed) {
            await browser.takeScreenshot();
        }
    }
}

