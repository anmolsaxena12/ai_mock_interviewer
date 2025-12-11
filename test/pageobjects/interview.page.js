const BasePage = require('./base.page');

/**
 * Interview Page Object
 */
class InterviewPage extends BasePage {
    /**
     * Define page selectors
     */
    get questionText() {
        return $('*[class*="question"]');
    }

    get answerTextarea() {
        return $('textarea[name="user_answer"]');
    }

    get submitButton() {
        return $('button[type="submit"]');
    }

    get feedbackSection() {
        return $('*[class*="feedback"]');
    }

    get interviewHistory() {
        return $$('*[class*="history"] > *');
    }

    get endInterviewButton() {
        return $('a[href*="end_interview"]');
    }

    get currentStage() {
        return $('*[class*="stage"]');
    }

    /**
     * Open the interview page
     */
    async open() {
        await super.open('/start_interview');
        await this.waitForPageLoad();
    }

    /**
     * Get the current question
     * @returns {Promise<string>} The question text
     */
    async getCurrentQuestion() {
        await this.waitForElement(this.questionText);
        return await this.getText(this.questionText);
    }

    /**
     * Submit an answer
     * @param {string} answer - The answer text
     */
    async submitAnswer(answer) {
        await this.setValue(this.answerTextarea, answer);
        await this.clickElement(this.submitButton);
        await browser.pause(1000); // Wait for processing
    }

    /**
     * Check if feedback is displayed
     * @returns {Promise<boolean>} True if feedback is shown
     */
    async isFeedbackDisplayed() {
        return await this.isDisplayed(this.feedbackSection);
    }

    /**
     * Get feedback text
     * @returns {Promise<string>} The feedback text
     */
    async getFeedback() {
        if (await this.isFeedbackDisplayed()) {
            return await this.getText(this.feedbackSection);
        }
        return '';
    }

    /**
     * Get the number of questions in history
     * @returns {Promise<number>} Number of historical questions
     */
    async getHistoryCount() {
        const elements = await this.interviewHistory;
        return elements.length;
    }

    /**
     * End the interview
     */
    async endInterview() {
        await this.clickElement(this.endInterviewButton);
    }

    /**
     * Complete interview flow with multiple Q&A
     * @param {Array<string>} answers - Array of answers to submit
     */
    async completeInterview(answers) {
        for (const answer of answers) {
            await this.submitAnswer(answer);
            await browser.pause(1000);
        }
    }
}

module.exports = new InterviewPage();

