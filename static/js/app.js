// Job Board Application JavaScript

class JobBoard {
    constructor() {
        this.jobs = [];
        this.filteredJobs = [];
        this.currentFilters = {
            search: '',
            location: '',
            employmentType: ''
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.loadJobs();
        this.updateStats();
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('job-search').addEventListener('input', (e) => {
            this.currentFilters.search = e.target.value;
            this.filterJobs();
        });

        // Location filter
        document.getElementById('location-filter').addEventListener('input', (e) => {
            this.currentFilters.location = e.target.value;
            this.filterJobs();
        });

        // Employment type filter
        document.getElementById('employment-type-filter').addEventListener('change', (e) => {
            this.currentFilters.employmentType = e.target.value;
            this.filterJobs();
        });

        // Clear filters
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });

        // Modal close
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal when clicking outside
        document.getElementById('job-modal').addEventListener('click', (e) => {
            if (e.target.id === 'job-modal') {
                this.closeModal();
            }
        });
    }

    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            const data = await response.json();
            
            if (data.success) {
                this.jobs = data.jobs;
                this.filteredJobs = [...this.jobs];
                this.renderJobs();
                this.updateJobCount(data.total);
            } else {
                this.showError('Failed to load jobs: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading jobs: ' + error.message);
        }
    }

    filterJobs() {
        this.filteredJobs = this.jobs.filter(job => {
            const matchesSearch = !this.currentFilters.search || 
                job.title.toLowerCase().includes(this.currentFilters.search.toLowerCase()) ||
                job.company.toLowerCase().includes(this.currentFilters.search.toLowerCase()) ||
                job.description.toLowerCase().includes(this.currentFilters.search.toLowerCase());

            const matchesLocation = !this.currentFilters.location ||
                job.location.toLowerCase().includes(this.currentFilters.location.toLowerCase()) ||
                job.city.toLowerCase().includes(this.currentFilters.location.toLowerCase()) ||
                job.state.toLowerCase().includes(this.currentFilters.location.toLowerCase());

            const matchesEmploymentType = !this.currentFilters.employmentType ||
                job.employment_type === this.currentFilters.employmentType;

            return matchesSearch && matchesLocation && matchesEmploymentType;
        });

        this.renderJobs();
    }

    clearFilters() {
        document.getElementById('job-search').value = '';
        document.getElementById('location-filter').value = '';
        document.getElementById('employment-type-filter').value = '';
        
        this.currentFilters = {
            search: '',
            location: '',
            employmentType: ''
        };
        
        this.filteredJobs = [...this.jobs];
        this.renderJobs();
    }

    renderJobs() {
        const jobsList = document.getElementById('jobs-list');
        
        if (this.filteredJobs.length === 0) {
            jobsList.innerHTML = `
                <div class="loading">
                    <i class="fas fa-search"></i>
                    <span>No jobs found matching your criteria</span>
                </div>
            `;
            return;
        }

        jobsList.innerHTML = this.filteredJobs.map(job => this.createJobHTML(job)).join('');
        
        // Add click event listeners to job items
        document.querySelectorAll('.job-item').forEach(item => {
            item.addEventListener('click', () => {
                const jobId = item.dataset.jobId;
                const job = this.jobs.find(j => j.id === jobId);
                if (job) {
                    this.showJobModal(job);
                }
            });
        });
    }

    createJobHTML(job) {
        const salary = this.formatSalary(job.salary_min, job.salary_max);
        const datePosted = this.formatDate(job.date_posted);
        
        return `
            <div class="job-item" data-job-id="${job.id}">
                <div class="job-header">
                    <div>
                        <div class="job-title">${this.escapeHtml(job.title)}</div>
                        <div class="job-company">${this.escapeHtml(job.company)}</div>
                    </div>
                    ${salary ? `<div class="job-salary">${salary}</div>` : ''}
                </div>
                
                <div class="job-meta">
                    <span><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(job.location)}</span>
                    <span><i class="fas fa-briefcase"></i> ${this.escapeHtml(job.employment_type || 'N/A')}</span>
                    <span><i class="fas fa-building"></i> ${this.escapeHtml(job.source)}</span>
                </div>
                
                <div class="job-description">
                    ${this.escapeHtml(job.description)}
                </div>
                
                <div class="job-footer">
                    <div class="job-tags">
                        ${job.seniority_level ? `<span class="tag">${this.escapeHtml(job.seniority_level)}</span>` : ''}
                        ${job.employment_type ? `<span class="tag">${this.escapeHtml(job.employment_type)}</span>` : ''}
                    </div>
                    <div class="job-date">${datePosted}</div>
                </div>
            </div>
        `;
    }

    showJobModal(job) {
        const modal = document.getElementById('job-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const applyLink = document.getElementById('apply-link');
        
        modalTitle.textContent = job.title;
        applyLink.href = job.url;
        
        const salary = this.formatSalary(job.salary_min, job.salary_max);
        const datePosted = this.formatDate(job.date_posted);
        
        modalBody.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h3 style="color: #667eea; margin-bottom: 0.5rem;">${this.escapeHtml(job.company)}</h3>
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.9rem; color: #64748b;">
                    <span><i class="fas fa-map-marker-alt"></i> ${this.escapeHtml(job.location)}</span>
                    <span><i class="fas fa-briefcase"></i> ${this.escapeHtml(job.employment_type || 'N/A')}</span>
                    <span><i class="fas fa-building"></i> ${this.escapeHtml(job.source)}</span>
                </div>
                ${salary ? `<div style="margin-bottom: 1rem;"><strong>Salary:</strong> ${salary}</div>` : ''}
                <div style="margin-bottom: 1.5rem;"><strong>Posted:</strong> ${datePosted}</div>
            </div>
            
            <div>
                <h4 style="margin-bottom: 1rem; color: #1e293b;">Job Description</h4>
                <div style="white-space: pre-wrap; line-height: 1.6;">${this.escapeHtml(job.description)}</div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    closeModal() {
        document.getElementById('job-modal').style.display = 'none';
    }

    formatSalary(min, max) {
        if (!min && !max) return null;
        if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
        if (min) return `$${min.toLocaleString()}+`;
        if (max) return `Up to $${max.toLocaleString()}`;
        return null;
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateJobCount(count) {
        document.getElementById('total-jobs').textContent = `${count} jobs available`;
    }

    async updateStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                const stats = data.stats;
                document.getElementById('update-time').textContent = new Date().toLocaleTimeString();
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    showError(message) {
        const jobsList = document.getElementById('jobs-list');
        jobsList.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                <span>${message}</span>
            </div>
        `;
    }

    // File Upload Methods
    setupFileUpload() {
        /**
         * Set up all file upload event listeners and interactions
         * 
         * TODO: Implement this method to:
         * 1. Get references to upload area, file input, and upload link elements
         * 2. Add click event listener to upload area to trigger file input
         * 3. Add click event listener to upload link to trigger file input
         * 4. Add change event listener to file input to handle file selection
         * 5. Add drag and drop event listeners (dragover, dragleave, drop)
         * 6. Prevent default behavior for drag events
         * 7. Add/remove 'dragover' CSS class for visual feedback
         */
        // TODO: Implement file upload setup
    }

    handleFileUpload(file) {
        /**
         * Handle the file upload process
         * 
         * @param {File} file - The selected file to upload
         * 
         * TODO: Implement this method to:
         * 1. Validate the file using validateFile()
         * 2. Show upload progress using showUploadProgress()
         * 3. Create FormData object and append the file
         * 4. Send POST request to '/api/upload-resume' endpoint
         * 5. Handle response - show success/error message
         * 6. Hide upload progress using hideUploadProgress()
         * 7. Handle errors with try/catch or .catch()
         */
        // TODO: Implement file upload handling
    }

    validateFile(file) {
        /**
         * Validate uploaded file for type and size
         * 
         * @param {File} file - The file to validate
         * @returns {boolean} - True if valid, false otherwise
         * 
         * TODO: Implement this method to:
         * 1. Check if file type is 'application/pdf'
         * 2. Check if file size is under 10MB (10 * 1024 * 1024 bytes)
         * 3. Show error message using showUploadStatus() if invalid
         * 4. Return true if valid, false if invalid
         */
        // TODO: Implement file validation
        return false;
    }

    showUploadProgress() {
        /**
         * Show upload progress bar and hide status messages
         * 
         * TODO: Implement this method to:
         * 1. Show the upload progress element
         * 2. Hide the upload status element
         * 3. Create a progress simulation (optional - for demo purposes)
         * 4. Update progress bar width and text
         * 5. Store interval ID for cleanup later
         */
        // TODO: Implement progress display
    }

    hideUploadProgress() {
        /**
         * Hide upload progress bar and clean up intervals
         * 
         * TODO: Implement this method to:
         * 1. Hide the upload progress element
         * 2. Clear any running intervals (progress simulation)
         * 3. Reset progress bar to 0%
         */
        // TODO: Implement progress hiding
    }

    showUploadStatus(type, message) {
        /**
         * Show upload status message (success, error, info)
         * 
         * @param {string} type - Status type: 'success', 'error', or 'info'
         * @param {string} message - Status message to display
         * 
         * TODO: Implement this method to:
         * 1. Get reference to upload status element
         * 2. Set CSS class based on type (upload-status success/error/info)
         * 3. Set the message text
         * 4. Show the status element
         * 5. Auto-hide success messages after 5 seconds
         */
        // TODO: Implement status display
    }
}

// Initialize the job board when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new JobBoard();
});
