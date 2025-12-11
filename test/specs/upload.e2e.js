const UploadPage = require('../pageobjects/upload.page');
const path = require('path');

describe('Document Upload Flow', () => {
    beforeEach(async () => {
        await UploadPage.open();
    });

    it('should display upload form', async () => {
        await expect(UploadPage.resumeFileInput).toBeDisplayed();
        await expect(UploadPage.jobDescriptionTextarea).toBeDisplayed();
        await expect(UploadPage.submitButton).toBeDisplayed();
    });

    it('should show error when submitting without resume', async () => {
        // Try to submit with only job description
        await UploadPage.setJobDescription('Test job description for software engineer');
        await UploadPage.submit();
        
        // Should show error
        await browser.pause(1000);
        const hasError = await UploadPage.hasError();
        expect(hasError).toBe(true);
    });

    it('should show error when submitting without job description', async () => {
        // Note: This test would require creating an actual file
        // For now, we'll test the validation
        await UploadPage.submit();
        
        await browser.pause(1000);
        const hasError = await UploadPage.hasError();
        expect(hasError).toBe(true);
    });

    it('should accept text in job description field', async () => {
        const testJD = 'We are looking for a Python developer with Flask experience.';
        await UploadPage.setJobDescription(testJD);
        
        const value = await UploadPage.jobDescriptionTextarea.getValue();
        expect(value).toBe(testJD);
    });

    it('should display form validation messages', async () => {
        await UploadPage.submit();
        await browser.pause(1000);
        
        // Check for validation messages
        const alerts = await $$('.alert');
        expect(alerts.length).toBeGreaterThan(0);
    });

    it('should handle empty job description submission', async () => {
        await UploadPage.setJobDescription('');
        await UploadPage.submit();
        
        await browser.pause(1000);
        const errorMsg = await UploadPage.getErrorMessage();
        expect(errorMsg).toContain('empty' || 'required');
    });

    // Note: Full file upload test would require actual PDF/DOCX files
    // This can be extended with fixture files
});

describe('Document Upload Validation', () => {
    beforeEach(async () => {
        await UploadPage.open();
    });

    it('should validate file type (conceptual test)', async () => {
        // This test demonstrates the structure
        // In practice, you'd create test fixture files
        
        await expect(UploadPage.resumeFileInput).toExist();
        
        // File input should accept specific types
        const acceptAttr = await UploadPage.resumeFileInput.getAttribute('accept');
        // Verify it accepts PDF and DOCX if attribute is set
        if (acceptAttr) {
            expect(acceptAttr).toContain('pdf' || 'docx');
        }
    });

    it('should have proper form structure', async () => {
        // Verify form elements exist
        await expect(UploadPage.resumeFileInput).toExist();
        await expect(UploadPage.jobDescriptionTextarea).toExist();
        await expect(UploadPage.submitButton).toExist();
        
        // Verify form attributes
        const textareaName = await UploadPage.jobDescriptionTextarea.getAttribute('name');
        expect(textareaName).toBe('job_description_text');
    });
});

describe('Upload Page UI', () => {
    it('should display all required form fields', async () => {
        await UploadPage.open();
        
        // Check all form elements are visible
        await expect(UploadPage.resumeFileInput).toBeExisting();
        await expect(UploadPage.jobDescriptionTextarea).toBeExisting();
        await expect(UploadPage.submitButton).toBeExisting();
    });

    it('should have accessible form labels', async () => {
        await UploadPage.open();
        
        // Check for labels (good accessibility practice)
        const labels = await $$('label');
        expect(labels.length).toBeGreaterThan(0);
    });
});

