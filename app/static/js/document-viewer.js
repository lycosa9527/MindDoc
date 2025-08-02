class DocumentViewer {
    constructor() {
        this.currentDocument = null;
        this.autoSaveTimeout = null;
        this.currentJobId = null;
    }
    
    renderDocument(documentData, jobId) {
        this.currentJobId = jobId;
        this.currentDocument = documentData;
        
        const viewer = document.getElementById('documentViewer');
        let html = '<div class="document-content">';
        
        documentData.paragraph_analyses.forEach((paragraph, index) => {
            html += `
                <div class="paragraph-container" data-paragraph-id="${index}">
                    <div class="paragraph-header">
                        <span class="paragraph-number">Paragraph ${index + 1}</span>
                        <div class="paragraph-stats">
                            <span class="word-count">${paragraph.word_count} words</span>
                            <span class="readability-score">Readability: ${paragraph.readability?.toFixed(1) || 'N/A'}</span>
                        </div>
                    </div>
                    <div class="paragraph-content" 
                         contenteditable="true" 
                         data-original="${paragraph.text}"
                         role="textbox"
                         aria-label="Edit paragraph ${index + 1}">
                        ${paragraph.text}
                    </div>
                    <div class="paragraph-suggestions">
                        ${this.renderSuggestions(paragraph.comments)}
                    </div>
                    <div class="paragraph-actions">
                        <button class="btn btn-sm btn-outline-primary apply-suggestion" 
                                data-paragraph="${index}"
                                aria-label="Apply suggestions for paragraph ${index + 1}">
                            Apply Suggestions
                        </button>
                        <button class="btn btn-sm btn-outline-secondary revert-changes" 
                                data-paragraph="${index}"
                                aria-label="Revert changes for paragraph ${index + 1}">
                            Revert
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        viewer.innerHTML = html;
        this.setupEventListeners();
        this.updateDocumentStats();
    }
    
    renderSuggestions(comments) {
        if (!comments || comments.length === 0) {
            return '<div class="no-suggestions">No suggestions for this paragraph</div>';
        }
        
        return `
            <div class="suggestions-list">
                ${comments.map(comment => `
                    <div class="suggestion-item">
                        <i class="fas fa-lightbulb text-warning" aria-hidden="true"></i>
                        <span>${comment}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    setupEventListeners() {
        // Real-time content editing
        document.querySelectorAll('.paragraph-content').forEach(element => {
            element.addEventListener('input', (e) => {
                this.handleContentChange(e.target);
            });
            
            element.addEventListener('blur', (e) => {
                this.saveChanges(e.target);
            });
            
            // Keyboard navigation
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    element.blur();
                }
            });
        });
        
        // Apply suggestions
        document.querySelectorAll('.apply-suggestion').forEach(button => {
            button.addEventListener('click', (e) => {
                this.applySuggestions(e.target.dataset.paragraph);
            });
        });
        
        // Revert changes
        document.querySelectorAll('.revert-changes').forEach(button => {
            button.addEventListener('click', (e) => {
                this.revertChanges(e.target.dataset.paragraph);
            });
        });
    }
    
    handleContentChange(element) {
        const newText = element.textContent;
        
        // Mark as modified
        element.classList.add('modified');
        
        // Auto-save after delay
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveChanges(element);
        }, 2000);
    }
    
    async saveChanges(element) {
        const paragraphId = element.closest('.paragraph-container').dataset.paragraphId;
        const newText = element.textContent;
        
        try {
            const response = await fetch('/api/update-paragraph', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    paragraph_id: paragraphId,
                    new_text: newText,
                    job_id: this.currentJobId
                })
            });
            
            if (response.ok) {
                element.classList.remove('modified');
                this.showSaveIndicator(paragraphId);
                this.updateDocumentStats();
            } else {
                throw new Error('Failed to save changes');
            }
            
        } catch (error) {
            console.error('Error saving changes:', error);
            this.showError('Failed to save changes. Please try again.');
        }
    }
    
    showSaveIndicator(paragraphId) {
        const container = document.querySelector(`[data-paragraph-id="${paragraphId}"]`);
        const indicator = document.createElement('div');
        indicator.className = 'save-indicator';
        indicator.textContent = 'Saved';
        indicator.setAttribute('aria-live', 'polite');
        
        container.appendChild(indicator);
        
        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }
    
    updateDocumentStats() {
        if (!this.currentDocument) return;
        
        const totalParagraphs = this.currentDocument.paragraph_analyses.length;
        const totalWords = this.currentDocument.paragraph_analyses.reduce((sum, p) => sum + p.word_count, 0);
        const avgReadability = this.currentDocument.paragraph_analyses.reduce((sum, p) => sum + (p.readability || 0), 0) / totalParagraphs;
        
        document.getElementById('totalParagraphs').textContent = `${totalParagraphs} paragraphs`;
        document.getElementById('totalWords').textContent = `${totalWords} words`;
        document.getElementById('avgReadability').textContent = `${avgReadability.toFixed(1)} readability`;
        
        document.getElementById('documentStats').classList.remove('d-none');
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
    
    applySuggestions(paragraphId) {
        // Implementation for applying suggestions
        console.log('Applying suggestions for paragraph:', paragraphId);
        // TODO: Implement suggestion application logic
    }
    
    revertChanges(paragraphId) {
        const container = document.querySelector(`[data-paragraph-id="${paragraphId}"]`);
        const content = container.querySelector('.paragraph-content');
        const originalText = content.dataset.original;
        
        content.textContent = originalText;
        content.classList.remove('modified');
        
        this.saveChanges(content);
    }
}

// Initialize document viewer
window.documentViewer = new DocumentViewer(); 