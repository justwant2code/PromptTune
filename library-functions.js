// Prompt Library Functions

// Load prompt library from API
async function loadPromptLibrary() {
    const libraryLoading = document.getElementById('libraryLoading');
    const promptGrid = document.getElementById('promptGrid');
    
    libraryLoading.classList.add('show');
    
    try {
        const response = await fetch(`${API_BASE}/prompts`);
        const data = await response.json();
        
        if (response.ok) {
            allPrompts = data.prompts || [];
            filteredPrompts = [...allPrompts];
            renderPrompts();
        } else {
            throw new Error(data.error || 'Failed to load prompts');
        }
    } catch (error) {
        console.log('Using sample prompts:', error.message);
        // Use sample prompts if API fails
        allPrompts = getSamplePrompts();
        filteredPrompts = [...allPrompts];
        renderPrompts();
    } finally {
        libraryLoading.classList.remove('show');
    }
}

// Get sample prompts for demo
function getSamplePrompts() {
    return [
        {
            id: 'prompt_001',
            title: 'Content Creation Assistant',
            prompt: 'Act as an expert content creator. Write engaging, SEO-optimized content about [TOPIC]. Include: 1) Compelling headline, 2) Introduction hook, 3) Key points with examples, 4) Call-to-action. Target audience: [AUDIENCE]. Tone: [TONE].',
            category: 'Marketing',
            description: 'Professional content creation prompt with structure and SEO optimization',
            tags: ['content', 'seo', 'marketing', 'writing'],
            created_at: new Date().toISOString(),
            usage_count: 45
        },
        {
            id: 'prompt_002',
            title: 'Code Review Expert',
            prompt: 'Act as a senior software engineer. Review the following code for: 1) Best practices, 2) Security vulnerabilities, 3) Performance optimizations, 4) Code readability. Provide specific suggestions with examples. Code language: [LANGUAGE].',
            category: 'Development',
            description: 'Comprehensive code review prompt for software quality assurance',
            tags: ['code', 'review', 'security', 'performance'],
            created_at: new Date().toISOString(),
            usage_count: 32
        },
        {
            id: 'prompt_003',
            title: 'Data Analysis Specialist',
            prompt: 'Act as a data scientist. Analyze the provided dataset and: 1) Identify key patterns and trends, 2) Provide statistical insights, 3) Suggest actionable recommendations, 4) Create visualization suggestions. Focus on: [BUSINESS_OBJECTIVE].',
            category: 'Analytics',
            description: 'Professional data analysis prompt with statistical insights',
            tags: ['data', 'analysis', 'statistics', 'insights'],
            created_at: new Date().toISOString(),
            usage_count: 28
        },
        {
            id: 'prompt_004',
            title: 'Email Marketing Campaign',
            prompt: 'Create a compelling email marketing campaign for [PRODUCT/SERVICE]. Include: 1) Subject line (A/B test options), 2) Personalized greeting, 3) Value proposition, 4) Social proof, 5) Clear CTA, 6) Mobile-optimized format. Target: [AUDIENCE]. Goal: [CONVERSION_GOAL].',
            category: 'Marketing',
            description: 'Complete email marketing campaign with conversion optimization',
            tags: ['email', 'marketing', 'conversion', 'campaign'],
            created_at: new Date().toISOString(),
            usage_count: 67
        },
        {
            id: 'prompt_005',
            title: 'Business Strategy Consultant',
            prompt: 'Act as a senior business consultant. Analyze [BUSINESS_SITUATION] and provide: 1) SWOT analysis, 2) Market opportunities, 3) Risk assessment, 4) Strategic recommendations, 5) Implementation roadmap. Consider: industry trends, competitive landscape, and resource constraints.',
            category: 'Business',
            description: 'Strategic business analysis with actionable recommendations',
            tags: ['strategy', 'business', 'analysis', 'consulting'],
            created_at: new Date().toISOString(),
            usage_count: 19
        },
        {
            id: 'prompt_006',
            title: 'Social Media Content Creator',
            prompt: 'Create engaging social media content for [PLATFORM] about [TOPIC]. Include: 1) Hook (first 3 seconds), 2) Value-driven content, 3) Visual suggestions, 4) Hashtag strategy, 5) Engagement questions. Style: [BRAND_VOICE]. Audience: [TARGET_DEMOGRAPHIC].',
            category: 'Content',
            description: 'Platform-specific social media content with engagement optimization',
            tags: ['social', 'content', 'engagement', 'branding'],
            created_at: new Date().toISOString(),
            usage_count: 54
        }
    ];
}

// Render prompts in the grid
function renderPrompts() {
    const promptGrid = document.getElementById('promptGrid');
    
    if (filteredPrompts.length === 0) {
        promptGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">
                <h3>No prompts found</h3>
                <p>Try adjusting your search or add a new prompt to get started.</p>
            </div>
        `;
        return;
    }
    
    promptGrid.innerHTML = filteredPrompts.map(prompt => `
        <div class="prompt-card">
            <h4>${prompt.title}</h4>
            <div class="description">${prompt.description}</div>
            <div class="prompt-text">${prompt.prompt}</div>
            <div class="tags">
                <span class="tag">${prompt.category}</span>
                ${prompt.tags ? prompt.tags.map(tag => `<span class="tag">${tag}</span>`).join('') : ''}
            </div>
            <div class="actions">
                <button class="btn btn-small" onclick="usePrompt('${prompt.id}')">
                    🚀 Use Prompt
                </button>
                <button class="btn btn-secondary btn-small" onclick="editPrompt('${prompt.id}')">
                    ✏️ Edit
                </button>
                <button class="btn btn-danger btn-small" onclick="deletePrompt('${prompt.id}')">
                    🗑️ Delete
                </button>
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #666;">
                Used ${prompt.usage_count || 0} times
            </div>
        </div>
    `).join('');
}

// Filter prompts based on search and category
function filterPrompts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    
    filteredPrompts = allPrompts.filter(prompt => {
        const matchesSearch = !searchTerm || 
            prompt.title.toLowerCase().includes(searchTerm) ||
            prompt.description.toLowerCase().includes(searchTerm) ||
            prompt.prompt.toLowerCase().includes(searchTerm) ||
            (prompt.tags && prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm)));
        
        const matchesCategory = !categoryFilter || prompt.category === categoryFilter;
        
        return matchesSearch && matchesCategory;
    });
    
    renderPrompts();
}

// Use a prompt (copy to optimize tab)
function usePrompt(promptId) {
    const prompt = allPrompts.find(p => p.id === promptId);
    if (prompt) {
        document.getElementById('promptInput').value = prompt.prompt;
        showTab('optimize');
        
        // Update usage count (in real app, this would be sent to API)
        prompt.usage_count = (prompt.usage_count || 0) + 1;
        
        // Show success message
        setTimeout(() => {
            alert('Prompt loaded! You can now optimize it or use it as-is.');
        }, 500);
    }
}

// Edit a prompt
function editPrompt(promptId) {
    const prompt = allPrompts.find(p => p.id === promptId);
    if (prompt) {
        document.getElementById('promptName').value = prompt.title;
        document.getElementById('promptDescription').value = prompt.description;
        document.getElementById('promptText').value = prompt.prompt;
        document.getElementById('promptCategory').value = prompt.category;
        document.getElementById('promptTags').value = prompt.tags ? prompt.tags.join(', ') : '';
        document.getElementById('modalTitle').textContent = 'Edit Prompt';
        document.getElementById('promptModal').style.display = 'block';
        
        // Store the ID for updating
        document.getElementById('promptForm').dataset.editId = promptId;
    }
}

// Delete a prompt
function deletePrompt(promptId) {
    if (confirm('Are you sure you want to delete this prompt?')) {
        allPrompts = allPrompts.filter(p => p.id !== promptId);
        filteredPrompts = filteredPrompts.filter(p => p.id !== promptId);
        renderPrompts();
        
        // In a real app, this would call the API to delete
        console.log('Prompt deleted:', promptId);
    }
}

// Show add prompt modal
function showAddPromptModal() {
    document.getElementById('promptName').value = '';
    document.getElementById('promptDescription').value = '';
    document.getElementById('promptText').value = '';
    document.getElementById('promptCategory').value = '';
    document.getElementById('promptTags').value = '';
    document.getElementById('modalTitle').textContent = 'Add New Prompt';
    document.getElementById('promptForm').removeAttribute('data-edit-id');
    document.getElementById('promptModal').style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('promptModal').style.display = 'none';
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('promptForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            title: document.getElementById('promptName').value,
            description: document.getElementById('promptDescription').value,
            prompt: document.getElementById('promptText').value,
            category: document.getElementById('promptCategory').value,
            tags: document.getElementById('promptTags').value.split(',').map(tag => tag.trim()).filter(tag => tag)
        };
        
        const editId = this.dataset.editId;
        
        if (editId) {
            // Update existing prompt
            const promptIndex = allPrompts.findIndex(p => p.id === editId);
            if (promptIndex !== -1) {
                allPrompts[promptIndex] = {
                    ...allPrompts[promptIndex],
                    ...formData
                };
            }
        } else {
            // Add new prompt
            const newPrompt = {
                id: 'prompt_' + Date.now(),
                ...formData,
                created_at: new Date().toISOString(),
                usage_count: 0
            };
            allPrompts.unshift(newPrompt);
        }
        
        // Update filtered prompts and re-render
        filterPrompts();
        closeModal();
        
        // Show success message
        alert(editId ? 'Prompt updated successfully!' : 'Prompt added successfully!');
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('promptModal');
        if (e.target === modal) {
            closeModal();
        }
    });
});
