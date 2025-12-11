/**
 * Base Page Object
 * Contains common methods used across all page objects
 */
class BasePage {
    /**
     * Open a page with the given path
     * @param {string} path - The path to navigate to
     */
    async open(path) {
        await browser.url(path);
    }

    /**
     * Wait for an element to be displayed
     * @param {WebdriverIO.Element} element - The element to wait for
     * @param {number} timeout - Optional timeout in milliseconds
     */
    async waitForElement(element, timeout = 10000) {
        await element.waitForDisplayed({ timeout });
    }

    /**
     * Click an element after waiting for it
     * @param {WebdriverIO.Element} element - The element to click
     */
    async clickElement(element) {
        await this.waitForElement(element);
        await element.click();
    }

    /**
     * Set value in an input field
     * @param {WebdriverIO.Element} element - The input element
     * @param {string} value - The value to set
     */
    async setValue(element, value) {
        await this.waitForElement(element);
        await element.setValue(value);
    }

    /**
     * Get text from an element
     * @param {WebdriverIO.Element} element - The element to get text from
     * @returns {Promise<string>} The element text
     */
    async getText(element) {
        await this.waitForElement(element);
        return await element.getText();
    }

    /**
     * Check if element is displayed
     * @param {WebdriverIO.Element} element - The element to check
     * @returns {Promise<boolean>} True if displayed
     */
    async isDisplayed(element) {
        try {
            return await element.isDisplayed();
        } catch (error) {
            return false;
        }
    }

    /**
     * Wait for page to load
     */
    async waitForPageLoad() {
        await browser.waitUntil(
            async () => await browser.execute(() => document.readyState === 'complete'),
            {
                timeout: 10000,
                timeoutMsg: 'Page did not load within 10 seconds'
            }
        );
    }
}

module.exports = BasePage;

