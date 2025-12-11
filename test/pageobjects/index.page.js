const BasePage = require('./base.page');

/**
 * Index/Home Page Object
 */
class IndexPage extends BasePage {
    /**
     * Define page selectors
     */
    get heading() {
        return $('h1');
    }

    get llmTestResponse() {
        return $('.card-text');
    }

    get uploadButton() {
        return $('a[href*="upload"]');
    }

    /**
     * Open the index page
     */
    async open() {
        await super.open('/');
        await this.waitForPageLoad();
    }

    /**
     * Check if LLM test was successful
     * @returns {Promise<boolean>} True if LLM test succeeded
     */
    async isLLMTestSuccessful() {
        const text = await this.getText(this.llmTestResponse);
        return text.includes('Successful') || text.includes('successful');
    }

    /**
     * Navigate to upload page
     */
    async goToUpload() {
        await this.clickElement(this.uploadButton);
    }

    /**
     * Get page heading text
     * @returns {Promise<string>} The heading text
     */
    async getHeading() {
        return await this.getText(this.heading);
    }
}

module.exports = new IndexPage();

