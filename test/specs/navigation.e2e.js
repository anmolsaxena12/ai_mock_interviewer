const IndexPage = require('../pageobjects/index.page');
const UploadPage = require('../pageobjects/upload.page');

describe('Navigation Tests', () => {
    it('should load the index page successfully', async () => {
        await IndexPage.open();
        
        const heading = await IndexPage.getHeading();
        expect(heading).toContain('Mock Interviewer' || 'AI Mock Interviewer');
    });

    it('should display LLM test status', async () => {
        await IndexPage.open();
        
        const llmStatus = await IndexPage.llmTestResponse;
        await expect(llmStatus).toBeDisplayed();
    });

    it('should navigate to upload page from index', async () => {
        await IndexPage.open();
        await IndexPage.goToUpload();
        
        // Verify we're on the upload page
        await browser.pause(500);
        const url = await browser.getUrl();
        expect(url).toContain('upload');
    });

    it('should have working navigation links', async () => {
        await IndexPage.open();
        
        // Check upload button exists
        const uploadBtn = await IndexPage.uploadButton;
        await expect(uploadBtn).toBeDisplayed();
    });

    it('should load page without errors', async () => {
        await IndexPage.open();
        
        // Check that no error messages are displayed
        const errorElements = await $$('.alert-danger');
        expect(errorElements.length).toBe(0);
    });
});

