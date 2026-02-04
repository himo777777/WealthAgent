/**
 * VR Studio Wizard - Step-by-step VR project creation
 */

document.addEventListener('DOMContentLoaded', function() {
    // State
    let currentStep = 1;
    const totalSteps = 5;
    let selectedProcedure = null;
    let generatedProjectId = null;
    let currentCategory = 'anatomy_skeletal';

    // Elements
    const steps = document.querySelectorAll('.wizard-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressFill = document.getElementById('progressFill');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const procedureName = document.getElementById('procedureName');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    // Data from server
    const { procedures, assets, tutorials, packages } = window.VR_STUDIO_DATA || {};

    // Initialize
    init();

    function init() {
        setupProcedureCards();
        setupNavigation();
        setupCodeGeneration();
        updateProgress();
    }

    // =========================================================================
    // Navigation
    // =========================================================================

    function setupNavigation() {
        prevBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                goToStep(currentStep - 1);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (validateStep(currentStep)) {
                if (currentStep < totalSteps) {
                    goToStep(currentStep + 1);
                }
            }
        });
    }

    function goToStep(step) {
        // Hide current step
        steps.forEach(s => s.classList.remove('active'));
        progressSteps.forEach(s => s.classList.remove('active', 'completed'));

        // Show new step
        currentStep = step;
        document.querySelector(`.wizard-step[data-step="${step}"]`).classList.add('active');

        // Update progress
        for (let i = 1; i <= totalSteps; i++) {
            const progressStep = document.querySelector(`.progress-step[data-step="${i}"]`);
            if (i < step) {
                progressStep.classList.add('completed');
            } else if (i === step) {
                progressStep.classList.add('active');
            }
        }

        updateProgress();
        updateNavButtons();

        // Step-specific actions
        if (step === 2 && selectedProcedure) {
            loadAssetsForProcedure();
        }
        if (step === 4) {
            loadPackageList();
        }
        if (step === 5) {
            loadTutorials();
        }
    }

    function updateProgress() {
        const progress = (currentStep / totalSteps) * 100;
        progressFill.style.width = `${progress}%`;
    }

    function updateNavButtons() {
        prevBtn.disabled = currentStep === 1;

        if (currentStep === totalSteps) {
            nextBtn.innerHTML = '<i class="fas fa-check"></i> Klar';
            nextBtn.onclick = () => {
                showToast('Lycka till med din VR-simulering!');
                window.location.href = '/vr-studio/';
            };
        } else {
            nextBtn.innerHTML = 'Nästa <i class="fas fa-arrow-right"></i>';
        }
    }

    function validateStep(step) {
        if (step === 1 && !selectedProcedure) {
            showToast('Välj en procedur först', 'warning');
            return false;
        }
        if (step === 3 && !generatedProjectId) {
            showToast('Generera kod först', 'warning');
            return false;
        }
        return true;
    }

    // =========================================================================
    // Step 1: Procedure Selection
    // =========================================================================

    function setupProcedureCards() {
        const cards = document.querySelectorAll('.procedure-card');
        cards.forEach(card => {
            card.addEventListener('click', function() {
                // Deselect all
                cards.forEach(c => c.classList.remove('selected'));
                // Select this one
                this.classList.add('selected');
                selectedProcedure = this.dataset.procedure;

                // Update header
                const proc = procedures.find(p => p.key === selectedProcedure);
                if (proc) {
                    procedureName.textContent = proc.name_sv;
                }

                showToast(`${proc.name_sv} vald`);
            });
        });
    }

    // =========================================================================
    // Step 2: Assets
    // =========================================================================

    function loadAssetsForProcedure() {
        const assetCategories = document.getElementById('assetCategories');
        const assetList = document.getElementById('assetList');

        if (!assets || !assets[selectedProcedure]) {
            assetList.innerHTML = '<p>Inga assets tillgängliga för denna procedur.</p>';
            return;
        }

        const procedureAssets = assets[selectedProcedure];

        // Render categories
        const categories = Object.keys(procedureAssets);
        const categoryLabels = {
            'anatomy_skeletal': 'Anatomi',
            'surgical_tools': 'Verktyg',
            'implants': 'Implantat',
            'operating_room': 'Operationssal',
            'vr_hands': 'VR Händer'
        };

        assetCategories.innerHTML = categories.map(cat => `
            <button class="category-btn ${cat === currentCategory ? 'active' : ''}" data-category="${cat}">
                ${categoryLabels[cat] || cat}
            </button>
        `).join('');

        // Add click handlers
        assetCategories.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                assetCategories.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentCategory = this.dataset.category;
                renderAssets(procedureAssets[currentCategory]);
            });
        });

        // Render initial assets
        if (categories.includes(currentCategory)) {
            renderAssets(procedureAssets[currentCategory]);
        } else if (categories.length > 0) {
            currentCategory = categories[0];
            renderAssets(procedureAssets[currentCategory]);
        }
    }

    function renderAssets(assetArray) {
        const assetList = document.getElementById('assetList');

        if (!assetArray || assetArray.length === 0) {
            assetList.innerHTML = '<p>Inga assets i denna kategori.</p>';
            return;
        }

        assetList.innerHTML = assetArray.map(asset => `
            <div class="asset-card">
                <h5>${asset.name}</h5>
                <div class="asset-meta">
                    ${asset.source} | ${asset.format} | ${asset.quality} kvalitet
                </div>
                <div class="asset-tags">
                    ${(asset.tags || []).map(tag => `<span class="asset-tag">${tag}</span>`).join('')}
                </div>
                <a href="${asset.url}" target="_blank">
                    <i class="fas fa-external-link-alt"></i> Öppna
                </a>
            </div>
        `).join('');
    }

    // =========================================================================
    // Step 3: Code Generation
    // =========================================================================

    function setupCodeGeneration() {
        // Option buttons
        document.querySelectorAll('.option-buttons').forEach(group => {
            group.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    group.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                });
            });
        });

        // Generate button
        const generateBtn = document.getElementById('generateCodeBtn');
        if (generateBtn) {
            generateBtn.addEventListener('click', generateCode);
        }
    }

    async function generateCode() {
        const generateBtn = document.getElementById('generateCodeBtn');
        const codePreview = document.getElementById('codePreview');

        // Get options
        const interactionType = document.querySelector('.option-buttons [data-option].active')?.dataset.option || 'hand_tracking';
        const complexity = document.querySelectorAll('.option-buttons')[1]?.querySelector('.active')?.dataset.option || 'beginner';
        const customPrompt = document.getElementById('customPrompt')?.value || '';

        const options = {
            haptics: document.getElementById('optHaptics')?.checked || false,
            audio: document.getElementById('optAudio')?.checked || false,
            scoring: document.getElementById('optScoring')?.checked || false,
            multiplayer: document.getElementById('optMultiplayer')?.checked || false
        };

        // Build prompt
        let prompt = `Skapa en komplett VR-simulering för ${selectedProcedure} med följande specifikationer:
- Interaktion: ${interactionType === 'hand_tracking' ? 'Handspårning' : interactionType === 'controllers' ? 'Kontroller' : 'Båda'}
- Komplexitet: ${complexity}
${options.haptics ? '- Inkludera haptisk feedback' : ''}
${options.audio ? '- Inkludera ljudeffekter' : ''}
${options.scoring ? '- Inkludera poängsystem och prestationsmätning' : ''}
${options.multiplayer ? '- Förbered för flerspelarfunktionalitet' : ''}
${customPrompt ? '\nYtterligare instruktioner: ' + customPrompt : ''}`;

        // Show loading
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Genererar...';
        codePreview.innerHTML = `
            <div class="code-placeholder">
                <div class="spinner"></div>
                <p>AI genererar din kod...</p>
                <small>Detta kan ta 10-30 sekunder</small>
            </div>
        `;

        try {
            const response = await fetch('/vr-studio/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    procedure_type: selectedProcedure,
                    complexity: complexity,
                    language: 'sv'
                })
            });

            const data = await response.json();

            if (data.success) {
                generatedProjectId = data.project_id;
                renderGeneratedCode(data);
                showToast('Kod genererad!');
            } else {
                throw new Error(data.error || 'Okänt fel');
            }
        } catch (error) {
            console.error('Generation error:', error);
            showToast('Fel: ' + error.message, 'error');
            codePreview.innerHTML = `
                <div class="code-placeholder">
                    <i class="fas fa-exclamation-triangle" style="color: var(--danger);"></i>
                    <p>Något gick fel</p>
                    <small>${error.message}</small>
                </div>
            `;
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generera Kod';
        }
    }

    function renderGeneratedCode(data) {
        const codePreview = document.getElementById('codePreview');

        if (!data.scripts || data.scripts.length === 0) {
            codePreview.innerHTML = '<div class="code-placeholder"><p>Ingen kod genererades</p></div>';
            return;
        }

        codePreview.innerHTML = data.scripts.map((script, i) => `
            <div class="script-block">
                <div class="script-header">
                    <span class="filename">
                        <i class="fas fa-file-code"></i>
                        ${script.filename}
                    </span>
                    <button class="copy-script-btn" onclick="copyScript(${i})">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
                <div class="script-code">
                    <pre><code class="language-csharp">${escapeHtml(script.content)}</code></pre>
                </div>
            </div>
        `).join('');

        // Store for copying
        window.generatedScripts = data.scripts;

        // Apply syntax highlighting
        document.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }

    // =========================================================================
    // Step 4: Download
    // =========================================================================

    function loadPackageList() {
        const packageList = document.getElementById('packageList');
        if (!packages || !packageList) return;

        packageList.innerHTML = packages.map(pkg => `
            <div class="package-item">
                <span>${pkg.name}</span>
                <a href="${pkg.url}" target="_blank">Läs mer <i class="fas fa-external-link-alt"></i></a>
            </div>
        `).join('');

        // Setup download button
        const downloadBtn = document.getElementById('downloadProjectBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', function() {
                if (generatedProjectId) {
                    window.location.href = `/vr-studio/download/${generatedProjectId}`;
                    showToast('Laddar ner...');
                } else {
                    showToast('Generera kod först (steg 3)', 'warning');
                }
            });
        }
    }

    // =========================================================================
    // Step 5: Tutorials
    // =========================================================================

    function loadTutorials() {
        const tutorialList = document.getElementById('tutorialList');
        if (!tutorials || !tutorialList) return;

        const allTutorials = [
            ...(tutorials.unity_basics || []),
            ...(tutorials.xr_toolkit || []),
            ...(tutorials.hand_tracking || [])
        ];

        tutorialList.innerHTML = allTutorials.slice(0, 5).map(tut => `
            <div class="tutorial-item">
                <div class="tutorial-info">
                    <span class="tutorial-title">${tut.title}</span>
                    <span class="tutorial-meta">${tut.platform} | ${tut.duration}</span>
                </div>
                <a href="${tut.url}" target="_blank">Öppna <i class="fas fa-external-link-alt"></i></a>
            </div>
        `).join('');
    }

    // =========================================================================
    // Utilities
    // =========================================================================

    window.copyScript = function(index) {
        if (window.generatedScripts && window.generatedScripts[index]) {
            copyToClipboard(window.generatedScripts[index].content);
            showToast('Kopierad!');
        }
    };

    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showToast(message, type = 'success') {
        toastMessage.textContent = message;
        toast.querySelector('i').className = type === 'error'
            ? 'fas fa-exclamation-circle'
            : type === 'warning'
                ? 'fas fa-exclamation-triangle'
                : 'fas fa-check-circle';
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }
});
