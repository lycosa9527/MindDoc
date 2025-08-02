class DocumentUploader {
    constructor() {
        this.currentJobId = null;
        this.statusCheckInterval = null;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const uploadForm = document.getElementById('uploadForm');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadSpinner = document.getElementById('uploadSpinner');
        const uploadText = document.getElementById('uploadText');
        const uploadStatus = document.getElementById('uploadStatus');
        
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleUpload();
        });
        
        // Download button
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadDocument();
        });
        
        // Reset button
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetDocument();
        });
        
        // File input change
        document.getElementById('documentFile').addEventListener('change', (e) => {
            this.validateFile(e.target);
        });
    }
    
    validateFile(fileInput) {
        const file = fileInput.files[0];
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadStatus = document.getElementById('uploadStatus');
        
        if (file) {
            // Check file size (16MB limit)
            const maxSize = 16 * 1024 * 1024; // 16MB
            if (file.size > maxSize) {
                this.showError('File size exceeds 16MB limit');
                fileInput.value = '';
                uploadBtn.disabled = true;
                uploadStatus.textContent = 'File too large';
                return;
            }
            
            // Check file type
            if (!file.name.toLowerCase().endsWith('.docx')) {
                this.showError('Only .docx files are supported');
                fileInput.value = '';
                uploadBtn.disabled = true;
                uploadStatus.textContent = 'Invalid file type';
                return;
            }
            
            uploadBtn.disabled = false;
            uploadStatus.textContent = 'File ready for upload';
        } else {
            uploadBtn.disabled = true;
            uploadStatus.textContent = 'No file selected';
        }
    }
    
    async handleUpload() {
        const fileInput = document.getElementById('documentFile');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadSpinner = document.getElementById('uploadSpinner');
        const uploadText = document.getElementById('uploadText');
        const uploadStatus = document.getElementById('uploadStatus');
        
        if (!fileInput.files[0]) {
            this.showError('Please select a file to upload');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        try {
            // Show loading state
            uploadBtn.disabled = true;
            uploadSpinner.classList.remove('d-none');
            uploadText.textContent = 'Uploading...';
            uploadStatus.textContent = 'Uploading document...';
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentJobId = result.job_id;
                this.showProgress();
                this.startStatusChecking();
                this.showSuccess('Document uploaded successfully! Analysis in progress...');
                uploadStatus.textContent = 'Upload successful, analysis started';
            } else {
                throw new Error(result.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
            uploadStatus.textContent = 'Upload failed';
        } finally {
            uploadBtn.disabled = false;
            uploadSpinner.classList.add('d-none');
            uploadText.textContent = 'Upload & Analyze';
        }
    }
    
    showProgress() {
        document.getElementById('progressSection').classList.remove('d-none');
        document.getElementById('downloadSection').classList.add('d-none');
    }
    
    hideProgress() {
        document.getElementById('progressSection').classList.add('d-none');
        document.getElementById('downloadSection').classList.remove('d-none');
    }
    
    showLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.remove('d-none');
    }
    
    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.add('d-none');
    }
    
    startStatusChecking() {
        this.statusCheckInterval = setInterval(async () => {
            await this.checkStatus();
        }, 2000);
    }
    
    stopStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
            this.statusCheckInterval = null;
        }
    }
    
    async checkStatus() {
        if (!this.currentJobId) return;
        
        try {
            const response = await fetch(`/status/${this.currentJobId}`);
            const status = await response.json();
            
            this.updateProgress(status);
            
            if (status.status === 'completed') {
                this.stopStatusChecking();
                await this.loadResults();
            } else if (status.status === 'failed') {
                this.stopStatusChecking();
                this.showError(`Analysis failed: ${status.message}`);
            }
            
        } catch (error) {
            console.error('Status check error:', error);
        }
    }
    
    updateProgress(status) {
        const progressBar = document.getElementById('progressBar');
        const progressMessage = document.getElementById('progressMessage');
        const progressDetails = document.getElementById('progressDetails');
        
        let progress = 0;
        let message = status.message || 'Processing...';
        
        switch (status.status) {
            case 'processing':
                progress = 50;
                break;
            case 'completed':
                progress = 100;
                message = 'Analysis completed!';
                break;
            case 'failed':
                progress = 0;
                message = 'Analysis failed';
                break;
            default:
                progress = 25;
        }
        
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressMessage.textContent = message;
        progressDetails.textContent = `Status: ${status.status}`;
    }
    
    async loadResults() {
        try {
            this.showLoadingOverlay();
            
            const response = await fetch(`/analysis/${this.currentJobId}`);
            const results = await response.json();
            
            if (response.ok) {
                window.documentViewer.renderDocument(results, this.currentJobId);
                this.hideProgress();
                this.showSuccess('Document analysis completed! You can now edit the document.');
            } else {
                throw new Error(results.error || 'Failed to load results');
            }
            
        } catch (error) {
            console.error('Error loading results:', error);
            this.showError(`Failed to load results: ${error.message}`);
        } finally {
            this.hideLoadingOverlay();
        }
    }
    
    downloadDocument() {
        if (!this.currentJobId) {
            this.showError('No document to download');
            return;
        }
        
        // Create a simple text version for download
        const documentData = window.documentViewer.currentDocument;
        if (!documentData) {
            this.showError('No document data available');
            return;
        }
        
        let content = '';
        documentData.paragraph_analyses.forEach((paragraph, index) => {
            content += `Paragraph ${index + 1}:\n`;
            content += `${paragraph.text}\n\n`;
            if (paragraph.comments && paragraph.comments.length > 0) {
                content += `Suggestions:\n`;
                paragraph.comments.forEach(comment => {
                    content += `- ${comment}\n`;
                });
                content += '\n';
            }
        });
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `minddoc_analysis_${this.currentJobId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showSuccess('Document downloaded successfully!');
    }
    
    resetDocument() {
        if (!this.currentJobId) {
            this.showError('No document to reset');
            return;
        }
        
        if (confirm('Are you sure you want to reset all changes? This will reload the original document.')) {
            this.loadResults();
            this.showSuccess('Document reset to original state');
        }
    }
    
    showSuccess(message) {
        const toast = new bootstrap.Toast(document.getElementById('saveToast'));
        document.querySelector('#saveToast .toast-body').textContent = message;
        toast.show();
    }
    
    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2" aria-hidden="true"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        errorContainer.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
}

// Initialize uploader
window.documentUploader = new DocumentUploader(); 