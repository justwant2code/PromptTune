// ===== MODERN DARK PROMPT TUNE APPLICATION =====
// Professional AI Prompt Engineering Platform
// Preserving all existing functionality with modern UI

class PromptTuneApp {
    constructor() {
        this.currentTab = 'optimize';
        this.prompts = [];
        this.analytics = {
            totalOptimizations: 0,
            savedPrompts: 0,
            avgLength: 0
        };
        this.isOptimizing = false;
        this.editingPromptId = null;
        
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
        this.setupSamplePrompts();
        this.updateAnalytics();
        this.renderPrompts();
        this.updateCharacterCount();
    }

    // ===== DATA MANAGEMENT =====
    loadData() {
        try {
            const savedPrompts = localStorage.getItem('promptTunePrompts');
            if (savedPrompts) {
                this.prompts = JSON.parse(savedPrompts);
            }
            
            const savedAnalytics = localStorage.getItem('promptTuneAnalytics');
            if (savedAnalytics) {
                this.analytics = JSON.parse(savedAnalytics);
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showToast('Error loading saved data', 'error');
        }
    }

    saveData() {
        try {
            localStorage.setItem('promptTunePrompts', JSON.stringify(this.prompts));
            localStorage.setItem('promptTuneAnalytics', JSON.stringify(this.analytics));
        } catch (error) {
            console.error('Error saving data:', error);
            this.showToast('Error saving data', 'error');
        }
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Optimize functionality
        const optimizeBtn = document.getElementById('optimizeBtn');
        const promptInput = document.getElementById('promptInput');
        const clearBtn = document.getElementById('clearInput');
        
        optimizeBtn.addEventListener('click', () => this.optimizePrompt());
        clearBtn.addEventListener('click', () => this.clearInput());
        
        promptInput.addEventListener('input', () => this.updateCharacterCount());
        promptInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.optimizePrompt();
            }
        });

        // Result actions
        document.getElementById('copyResult').addEventListener('click', () => this.copyResult());
        document.getElementById('saveToLibrary').addEventListener('click', () => this.saveResultToLibrary());

        // Library functionality
        document.getElementById('searchPrompts').addEventListener('input', (e) => {
            this.filterPrompts(e.target.value, document.getElementById('categoryFilter').value);
        });
        
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filterPrompts(document.getElementById('searchPrompts').value, e.target.value);
        });

        document.getElementById('addPromptBtn').addEventListener('click', () => this.openPromptModal());

        // Modal functionality
        document.getElementById('closeModal').addEventListener('click', () => this.closeModal());
        document.getElementById('cancelModal').addEventListener('click', () => this.closeModal());
        document.getElementById('promptForm').addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Close modal on overlay click
        document.getElementById('promptModal').addEventListener('click', (e) => {
            if (e.target.id === 'promptModal') {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    // ===== TAB MANAGEMENT =====
    switchTab(tabName) {
        // Update active tab button
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Update analytics when switching to analytics tab
        if (tabName === 'analytics') {
            this.updateAnalytics();
        }
    }

    // ===== PROMPT OPTIMIZATION =====
    async optimizePrompt() {
        const input = document.getElementById('promptInput').value.trim();
        
        if (!input) {
            this.showToast('Please enter a prompt to optimize', 'error');
            return;
        }

        if (this.isOptimizing) {
            return;
        }

        this.isOptimizing = true;
        this.showLoadingState();
        this.disableOptimizeButton();

        try {
            const response = await fetch('/api/optimize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: input })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.optimized_prompt) {
                this.displayResult(data.optimized_prompt);
                this.analytics.totalOptimizations++;
                this.saveData();
                this.showToast('Prompt optimized successfully!', 'success');
            } else {
                throw new Error('No optimized prompt received');
            }

        } catch (error) {
            console.error('Optimization error:', error);
            this.showToast('Failed to optimize prompt. Please try again.', 'error');
            this.showEmptyState();
        } finally {
            this.isOptimizing = false;
            this.enableOptimizeButton();
        }
    }

    showLoadingState() {
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('resultContent').classList.add('hidden');
        document.getElementById('loadingState').classList.remove('hidden');
        
        // Disable result actions
        document.getElementById('copyResult').disabled = true;
        document.getElementById('saveToLibrary').disabled = true;
    }

    displayResult(result) {
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('resultContent').classList.remove('hidden');
        
        const resultText = document.querySelector('.result-text');
        resultText.textContent = result;
        
        // Enable result actions
        document.getElementById('copyResult').disabled = false;
        document.getElementById('saveToLibrary').disabled = false;
    }

    showEmptyState() {
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('resultContent').classList.add('hidden');
        document.getElementById('emptyState').classList.remove('hidden');
        
        // Disable result actions
        document.getElementById('copyResult').disabled = true;
        document.getElementById('saveToLibrary').disabled = true;
    }

    disableOptimizeButton() {
        const btn = document.getElementById('optimizeBtn');
        btn.disabled = true;
        btn.innerHTML = `
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            Optimizing...
        `;
    }

    enableOptimizeButton() {
        const btn = document.getElementById('optimizeBtn');
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/>
            </svg>
            Optimize Prompt
        `;
    }

    clearInput() {
        document.getElementById('promptInput').value = '';
        this.updateCharacterCount();
        this.showEmptyState();
    }

    updateCharacterCount() {
        const input = document.getElementById('promptInput');
        const count = document.querySelector('.character-count');
        count.textContent = `${input.value.length} characters`;
    }

    // ===== RESULT ACTIONS =====
    async copyResult() {
        const resultText = document.querySelector('.result-text').textContent;
        
        try {
            await navigator.clipboard.writeText(resultText);
            this.showToast('Result copied to clipboard!', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            this.showToast('Failed to copy result', 'error');
        }
    }

    saveResultToLibrary() {
        const resultText = document.querySelector('.result-text').textContent;
        const originalPrompt = document.getElementById('promptInput').value;
        
        // Pre-fill modal with result
        this.openPromptModal();
        document.getElementById('promptText').value = resultText;
        document.getElementById('promptTitle').value = 'Optimized Prompt';
        
        // Focus on title for editing
        setTimeout(() => {
            document.getElementById('promptTitle').select();
        }, 100);
    }

    // ===== PROMPT LIBRARY MANAGEMENT =====
    setupSamplePrompts() {
        if (this.prompts.length === 0) {
            this.prompts = [
                {
                    id: this.generateId(),
                    title: "Content Creation Assistant",
                    category: "Content",
                    tags: ["writing", "content", "SEO"],
                    text: "You are a professional content creator. Help me write engaging, SEO-optimized content that resonates with my target audience. Focus on clear structure, compelling headlines, and actionable insights.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                },
                {
                    id: this.generateId(),
                    title: "Code Review Expert",
                    category: "Development",
                    tags: ["code", "review", "best-practices"],
                    text: "Act as a senior software engineer conducting a thorough code review. Analyze the code for security vulnerabilities, performance issues, maintainability, and adherence to best practices. Provide specific, actionable feedback.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                },
                {
                    id: this.generateId(),
                    title: "Data Analysis Specialist",
                    category: "Analytics",
                    tags: ["data", "analysis", "insights"],
                    text: "You are a data analyst with expertise in statistical analysis and business intelligence. Help me analyze this dataset, identify key trends, patterns, and provide actionable business recommendations based on the findings.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                },
                {
                    id: this.generateId(),
                    title: "Email Marketing Campaign",
                    category: "Marketing",
                    tags: ["email", "marketing", "conversion"],
                    text: "Create a compelling email marketing campaign that drives engagement and conversions. Include subject line variations, personalized content, clear call-to-actions, and A/B testing recommendations.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                },
                {
                    id: this.generateId(),
                    title: "Business Strategy Consultant",
                    category: "Business",
                    tags: ["strategy", "business", "planning"],
                    text: "Act as a strategic business consultant. Analyze the current market situation, identify opportunities and threats, and develop a comprehensive strategic plan with actionable steps and measurable goals.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                },
                {
                    id: this.generateId(),
                    title: "Social Media Content Creator",
                    category: "Marketing",
                    tags: ["social-media", "content", "engagement"],
                    text: "Create engaging social media content optimized for different platforms. Focus on trending topics, hashtag strategies, visual content ideas, and community engagement tactics that drive organic reach.",
                    createdAt: new Date().toISOString(),
                    usageCount: 0
                }
            ];
            this.saveData();
        }
    }

    renderPrompts(filteredPrompts = null) {
        const grid = document.getElementById('promptsGrid');
        const emptyState = document.getElementById('libraryEmptyState');
        const promptsToRender = filteredPrompts || this.prompts;

        if (promptsToRender.length === 0) {
            grid.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        grid.style.display = 'grid';
        emptyState.style.display = 'none';

        grid.innerHTML = promptsToRender.map(prompt => `
            <div class="prompt-card" data-id="${prompt.id}">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">${this.escapeHtml(prompt.title)}</h3>
                        <span class="card-category">${prompt.category}</span>
                    </div>
                    <div class="card-actions">
                        <button class="card-action-btn" onclick="app.editPrompt('${prompt.id}')" title="Edit">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="card-action-btn" onclick="app.deletePrompt('${prompt.id}')" title="Delete">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3,6 5,6 21,6"/>
                                <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p class="card-text">${this.escapeHtml(prompt.text)}</p>
                </div>
                <div class="card-footer">
                    <div class="card-tags">
                        ${prompt.tags.map(tag => `<span class="card-tag">${this.escapeHtml(tag)}</span>`).join('')}
                    </div>
                    <div class="card-meta">
                        <span>Used ${prompt.usageCount} times</span>
                    </div>
                </div>
                <button class="use-prompt-btn" onclick="app.usePrompt('${prompt.id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/>
                    </svg>
                    Use Prompt
                </button>
            </div>
        `).join('');
    }

    filterPrompts(searchTerm, category) {
        let filtered = this.prompts;

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            filtered = filtered.filter(prompt => 
                prompt.title.toLowerCase().includes(term) ||
                prompt.text.toLowerCase().includes(term) ||
                prompt.tags.some(tag => tag.toLowerCase().includes(term))
            );
        }

        if (category) {
            filtered = filtered.filter(prompt => prompt.category === category);
        }

        this.renderPrompts(filtered);
    }

    usePrompt(id) {
        const prompt = this.prompts.find(p => p.id === id);
        if (prompt) {
            // Switch to optimize tab
            this.switchTab('optimize');
            
            // Load prompt into input
            document.getElementById('promptInput').value = prompt.text;
            this.updateCharacterCount();
            
            // Update usage count
            prompt.usageCount++;
            this.saveData();
            this.renderPrompts();
            
            this.showToast(`Loaded "${prompt.title}" into optimizer`, 'success');
        }
    }

    // ===== MODAL MANAGEMENT =====
    openPromptModal(promptId = null) {
        this.editingPromptId = promptId;
        const modal = document.getElementById('promptModal');
        const form = document.getElementById('promptForm');
        const title = document.getElementById('modalTitle');

        if (promptId) {
            const prompt = this.prompts.find(p => p.id === promptId);
            if (prompt) {
                title.textContent = 'Edit Prompt';
                document.getElementById('promptTitle').value = prompt.title;
                document.getElementById('promptCategory').value = prompt.category;
                document.getElementById('promptTags').value = prompt.tags.join(', ');
                document.getElementById('promptText').value = prompt.text;
            }
        } else {
            title.textContent = 'Add New Prompt';
            form.reset();
        }

        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        setTimeout(() => {
            document.getElementById('promptTitle').focus();
        }, 100);
    }

    closeModal() {
        const modal = document.getElementById('promptModal');
        modal.classList.add('hidden');
        document.body.style.overflow = '';
        this.editingPromptId = null;
    }

    handleFormSubmit(e) {
        e.preventDefault();
        
        const title = document.getElementById('promptTitle').value.trim();
        const category = document.getElementById('promptCategory').value;
        const tags = document.getElementById('promptTags').value.split(',').map(tag => tag.trim()).filter(tag => tag);
        const text = document.getElementById('promptText').value.trim();

        if (!title || !category || !text) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        const promptData = {
            title,
            category,
            tags,
            text,
            usageCount: 0
        };

        if (this.editingPromptId) {
            // Edit existing prompt
            const promptIndex = this.prompts.findIndex(p => p.id === this.editingPromptId);
            if (promptIndex !== -1) {
                this.prompts[promptIndex] = {
                    ...this.prompts[promptIndex],
                    ...promptData
                };
                this.showToast('Prompt updated successfully!', 'success');
            }
        } else {
            // Add new prompt
            const newPrompt = {
                id: this.generateId(),
                ...promptData,
                createdAt: new Date().toISOString()
            };
            this.prompts.unshift(newPrompt);
            this.analytics.savedPrompts++;
            this.showToast('Prompt added successfully!', 'success');
        }

        this.saveData();
        this.renderPrompts();
        this.closeModal();
    }

    editPrompt(id) {
        this.openPromptModal(id);
    }

    deletePrompt(id) {
        if (confirm('Are you sure you want to delete this prompt?')) {
            this.prompts = this.prompts.filter(p => p.id !== id);
            this.analytics.savedPrompts = this.prompts.length;
            this.saveData();
            this.renderPrompts();
            this.showToast('Prompt deleted successfully', 'success');
        }
    }

    // ===== ANALYTICS =====
    updateAnalytics() {
        this.analytics.savedPrompts = this.prompts.length;
        
        if (this.prompts.length > 0) {
            const totalLength = this.prompts.reduce((sum, prompt) => sum + prompt.text.length, 0);
            this.analytics.avgLength = Math.round(totalLength / this.prompts.length);
        }

        document.getElementById('totalOptimizations').textContent = this.analytics.totalOptimizations;
        document.getElementById('savedPrompts').textContent = this.analytics.savedPrompts;
        document.getElementById('avgLength').textContent = this.analytics.avgLength;

        this.saveData();
    }

    // ===== TOAST NOTIFICATIONS =====
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const iconSvg = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="toast-icon">${iconSvg}</div>
            <div class="toast-content">
                <div class="toast-message">${this.escapeHtml(message)}</div>
            </div>
            <button class="toast-close">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.remove();
        });

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                <polyline points="20,6 9,17 4,12"/>
            </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>`
        };
        return icons[type] || icons.info;
    }

    // ===== UTILITY FUNCTIONS =====
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application
const app = new PromptTuneApp();

// Global error handling
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    app.showToast('An unexpected error occurred', 'error');
});

// Service worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
