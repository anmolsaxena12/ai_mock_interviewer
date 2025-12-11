const BasePage = require('./base.page');
const path = require('path');

/**
 * Upload Documents Page Object
 */
class UploadPage extends BasePage {
    /**
     * Define page selectors
     */
    get resumeFileInput() {
        return $('input[name="resume"]');
    }

    get jobDescriptionTextarea() {
        return $('textarea[name="job_description_text"]');
    }

    get submitButton() {
        return $('button[type="submit"], input[type="submit"]');
    }

    get successMessage() {
        return $('.alert-success');
    }

    get errorMessage() {
        return $('.alert-danger');
    }

    get warningMessage() {
        return $('.alert-warning');
    }

    get atsScore() {
        return $('*[class*="ats"]');
    }

    get startInterviewButton() {
        return $('a[href*="start_interview"]');
    }

    /**
     * Open the upload documents page
     */
    async open() {
        await super.open('/upload_documents');
        await this.waitForPageLoad();
    }

    /**
     * Upload a resume file
     * @param {string} filePath - Path to the resume file
     */
    async uploadResume(filePath) {
        const absolutePath = path.resolve(filePath);
        await this.resumeFileInput.waitForExist();
        
        // For file inputs, we need to use a different approach
        const remoteFilePath = await browser.uploadFile(absolutePath);
        await this.resumeFileInput.setValue(remoteFilePath);
    }

    /**
     * Set job description text
     * @param {string} text - Job description text
     */
    async setJobDescription(text) {
        await this.setValue(this.jobDescriptionTextarea, text);
    }

    /**
     * Submit the upload form
     */
    async submit() {
        await this.clickElement(this.submitButton);
        await browser.pause(1000); // Wait for processing
    }

    /**
     * Upload documents with both resume and JD
     * @param {string} resumePath - Path to resume file
     * @param {string} jobDescription - Job description text
     */
    async uploadDocuments(resumePath, jobDescription) {
        await this.uploadResume(resumePath);
        await this.setJobDescription(jobDescription);
        await this.submit();
    }

    /**
     * Check if upload was successful
     * @returns {Promise<boolean>} True if successful
     */
    async isUploadSuccessful() {
        return await this.isDisplayed(this.successMessage);
    }

    /**
     * Check if there's an error
     * @returns {Promise<boolean>} True if error exists
     */
    async hasError() {
        return await this.isDisplayed(this.errorMessage);
    }

    /**
     * Get error message text
     * @returns {Promise<string>} The error message
     */
    async getErrorMessage() {
        if (await this.hasError()) {
            return await this.getText(this.errorMessage);
        }
        return '';
    }

    /**
     * Navigate to start interview
     */
    async startInterview() {
        await this.clickElement(this.startInterviewButton);
    }
}

module.exports = new UploadPage();

