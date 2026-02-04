/**
 * VR Studio - ComplicationAI
 * AI-powered Unity VR code generation for orthopedic surgical training
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const generateForm = document.getElementById('generateForm');
    const generateBtn = document.getElementById('generateBtn');
    const promptInput = document.getElementById('prompt');
    const procedureSelect = document.getElementById('procedureType');

    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const codeOutput = document.getElementById('codeOutput');
    const outputActions = document.getElementById('outputActions');
    const downloadPanel = document.getElementById('downloadPanel');

    const scriptsContainer = document.getElementById('scriptsContainer');
    const instructionsSection = document.getElementById('instructionsSection');
    const instructionsList = document.getElementById('instructionsList');
    const dependenciesSection = document.getElementById('dependenciesSection');
    const dependenciesList = document.getElementById('dependenciesList');

    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadProjectBtn = document.getElementById('downloadProjectBtn');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    // State
    let currentProjectId = null;
    let generatedScripts = [];

    // Quick action buttons
    document.querySelectorAll('.quick-btn[data-tool]').forEach(btn => {
        btn.addEventListener('click', function() {
            const tool = this.dataset.tool;
            const toolNames = {
                'scalpel': 'skalpell för att göra incisioner',
                'bone_saw': 'bensåg för bensnitt',
                'drill': 'kirurgisk borr för skruvhål'
            };
            promptInput.value = `Skapa ett VR-verktyg för en ${toolNames[tool] || tool}. Inkludera haptisk feedback och handspårning för Meta Quest.`;
            promptInput.focus();
        });
    });

    document.querySelectorAll('.quick-btn[data-procedure]').forEach(btn => {
        btn.addEventListener('click', function() {
            const procedure = this.dataset.procedure;
            procedureSelect.value = procedure;
            promptInput.value = 'Skapa en komplett VR-simulering för denna procedur med alla nödvändiga steg och verktyg.';
            promptInput.focus();
        });
    });

    // Form submission
    generateForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const prompt = promptInput.value.trim();
        if (!prompt) {
            showToast('Skriv en prompt först', 'warning');
            return;
        }

        const procedureType = procedureSelect.value || null;
        const complexity = document.querySelector('input[name="complexity"]:checked').value;

        // Show loading state
        setLoadingState(true);

        try {
            const response = await fetch('/vr-studio/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    procedure_type: procedureType,
                    complexity: complexity,
                    language: 'sv'
                })
            });

            const data = await response.json();

            if (data.success) {
                currentProjectId = data.project_id;
                generatedScripts = data.scripts || [];
                displayResults(data);
                showToast('Kod genererad!');
            } else {
                throw new Error(data.error || 'Okänt fel');
            }
        } catch (error) {
            console.error('Generation error:', error);
            showToast('Fel: ' + error.message, 'error');
            setLoadingState(false);
            emptyState.style.display = 'flex';
        }
    });

    // Display results
    function displayResults(data) {
        setLoadingState(false);
        emptyState.style.display = 'none';
        codeOutput.style.display = 'flex';
        outputActions.style.display = 'flex';

        // Clear previous content
        scriptsContainer.innerHTML = '';
        instructionsList.innerHTML = '';
        dependenciesList.innerHTML = '';

        // Display scripts
        if (data.scripts && data.scripts.length > 0) {
            data.scripts.forEach((script, index) => {
                const scriptBlock = createScriptBlock(script, index);
                scriptsContainer.appendChild(scriptBlock);
            });

            // Apply syntax highlighting
            document.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }

        // Display instructions
        if (data.setup_instructions && data.setup_instructions.length > 0) {
            instructionsSection.style.display = 'block';
            data.setup_instructions.forEach(instruction => {
                const li = document.createElement('li');
                li.textContent = instruction.replace(/^[\d\.\-\*\)]+\s*/, '');
                instructionsList.appendChild(li);
            });
        } else {
            instructionsSection.style.display = 'none';
        }

        // Display dependencies
        if (data.dependencies && data.dependencies.length > 0) {
            dependenciesSection.style.display = 'block';
            data.dependencies.forEach(dep => {
                const tag = document.createElement('span');
                tag.className = 'dependency-tag';
                tag.textContent = `${dep.package}: ${dep.version}`;
                dependenciesList.appendChild(tag);
            });
        } else {
            dependenciesSection.style.display = 'none';
        }

        // Show download panel
        downloadPanel.style.display = 'flex';
    }

    // Create script block
    function createScriptBlock(script, index) {
        const block = document.createElement('div');
        block.className = 'script-block';

        const header = document.createElement('div');
        header.className = 'script-header';
        header.innerHTML = `
            <span class="filename">
                <i class="fas fa-file-code"></i>
                ${script.filename}
            </span>
            <button class="copy-script-btn" title="Kopiera" data-index="${index}">
                <i class="fas fa-copy"></i>
            </button>
        `;

        const codeDiv = document.createElement('div');
        codeDiv.className = 'script-code';
        codeDiv.innerHTML = `<pre><code class="language-csharp">${escapeHtml(script.content)}</code></pre>`;

        block.appendChild(header);
        block.appendChild(codeDiv);

        // Add copy handler
        header.querySelector('.copy-script-btn').addEventListener('click', function() {
            copyToClipboard(script.content);
            showToast('Kopierad till urklipp!');
        });

        return block;
    }

    // Copy all scripts
    copyBtn.addEventListener('click', function() {
        if (generatedScripts.length > 0) {
            const allCode = generatedScripts.map(s =>
                `// ${s.filename}\n${s.content}`
            ).join('\n\n// ============================================\n\n');
            copyToClipboard(allCode);
            showToast('All kod kopierad!');
        }
    });

    // Download buttons
    downloadBtn.addEventListener('click', downloadProject);
    downloadProjectBtn.addEventListener('click', downloadProject);

    async function downloadProject() {
        if (!currentProjectId) {
            showToast('Ingen projekt att ladda ner', 'warning');
            return;
        }

        try {
            window.location.href = `/vr-studio/download/${currentProjectId}`;
            showToast('Laddar ner...');
        } catch (error) {
            showToast('Nedladdning misslyckades', 'error');
        }
    }

    // Helper functions
    function setLoadingState(loading) {
        if (loading) {
            loadingState.style.display = 'flex';
            emptyState.style.display = 'none';
            codeOutput.style.display = 'none';
            outputActions.style.display = 'none';
            downloadPanel.style.display = 'none';
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Genererar...';
        } else {
            loadingState.style.display = 'none';
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> <span>Generera VR-kod</span>';
        }
    }

    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    function showToast(message, type = 'success') {
        toastMessage.textContent = message;
        toast.querySelector('i').className = type === 'error'
            ? 'fas fa-exclamation-circle'
            : type === 'warning'
                ? 'fas fa-exclamation-triangle'
                : 'fas fa-check-circle';
        toast.querySelector('i').style.color = type === 'error'
            ? 'var(--danger)'
            : type === 'warning'
                ? 'var(--warning)'
                : 'var(--success)';
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
