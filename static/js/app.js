/* ==========================================
   DNA & RNA Sequence Analyzer
   CSC 442 - Web GUI JavaScript
   ========================================== */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const sequenceInput = document.getElementById('sequenceInput');
    const charCount = document.getElementById('charCount');
    const liveValidation = document.getElementById('liveValidation');
    const btnAnalyze = document.getElementById('btnAnalyze');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const fileInput = document.getElementById('fileInput');
    const fileUploadZone = document.getElementById('fileUploadZone');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const btnContinueStrand = document.getElementById('btnContinueStrand');

    let currentSequence = '';
    let currentStrandType = 'non-template';
    let analysisData = null;

    // ==================== TAB SWITCHING ====================
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    // ==================== LIVE VALIDATION ====================
    sequenceInput.addEventListener('input', debounce(async () => {
        const seq = sequenceInput.value.trim();
        charCount.textContent = seq.length + ' characters';

        if (seq.length === 0) {
            liveValidation.className = 'validation-pending';
            liveValidation.textContent = 'Enter a sequence to validate';
            btnAnalyze.disabled = true;
            return;
        }

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sequence: seq })
            });
            const data = await response.json();

            if (data.type === 'invalid') {
                liveValidation.className = 'validation-invalid';
                liveValidation.textContent = '❌ ' + data.explanation.substring(0, 80) + '...';
                btnAnalyze.disabled = true;
            } else if (data.ambiguous) {
                liveValidation.className = 'validation-valid';
                liveValidation.textContent = 'Valid DNA/RNA sequence; type is ambiguous until T or U appears';
                btnAnalyze.disabled = false;
            } else {
                liveValidation.className = 'validation-valid';
                liveValidation.textContent = '✅ Detected as ' + data.type + ' (' + data.confidence + '% confidence)';
                btnAnalyze.disabled = false;
            }
        } catch (e) {
            liveValidation.className = 'validation-pending';
            liveValidation.textContent = 'Validation unavailable';
        }
    }, 300));

    // ==================== FILE UPLOAD ====================
    fileUploadZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFile(fileInput.files[0]);
        }
    });

    removeFile.addEventListener('click', () => {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        fileUploadZone.style.display = 'block';
        currentSequence = '';
        btnAnalyze.disabled = true;
    });

    // ==================== FILE UPLOAD DRAG & DROP ====================
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileUploadZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        fileUploadZone.addEventListener(eventName, () => fileUploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileUploadZone.addEventListener(eventName, () => fileUploadZone.classList.remove('dragover'), false);
    });

    fileUploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleFile(file) {
        const validTypes = ['text/plain', 'application/octet-stream'];
        const validExts = ['.txt', '.fasta', '.fa', '.seq'];
        const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

        if (!validExts.includes(ext) && !validTypes.includes(file.type)) {
            alert('Please upload a .txt, .fasta, .fa, or .seq file.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            let content = e.target.result;
            // Parse FASTA format
            if (ext === '.fasta' || ext === '.fa') {
                const lines = content.split('\n');
                content = lines.filter(l => !l.startsWith('>')).join('');
            }
            currentSequence = content.trim();
            sequenceInput.value = currentSequence;
            charCount.textContent = currentSequence.length + ' characters';

            // Switch to paste tab and show file info
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            document.querySelector('[data-tab="paste"]').classList.add('active');
            document.getElementById('tab-paste').classList.add('active');

            fileName.textContent = file.name + ' (' + formatBytes(file.size) + ')';
            fileInfo.style.display = 'flex';
            fileUploadZone.style.display = 'none';

            // Trigger validation
            sequenceInput.dispatchEvent(new Event('input'));
        };
        reader.readAsText(file);
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // ==================== ANALYZE BUTTON ====================
    btnAnalyze.addEventListener('click', async () => {
        currentSequence = sequenceInput.value.trim();
        if (!currentSequence) return;

        // Show loading on analyze button
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<span class="btn-icon">⏳</span> Analyzing...';

        // Reset all steps
        hideAllSteps();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sequence: currentSequence,
                    strand_type: currentStrandType
                })
            });

            analysisData = await response.json();

            if (analysisData.error) {
                alert('Error: ' + analysisData.error);
                return;
            }

            // Show detection step
            showDetection(analysisData.detection);

            if (analysisData.detection.type === 'invalid') {
                showStep('step-invalid');
                document.getElementById('invalidMessage').innerHTML = `
                    <span class="invalid-icon">⚠️</span>
                    <h3>Invalid Sequence Detected</h3>
                    <p>${formatMarkdown(analysisData.detection.explanation)}</p>
                    ${analysisData.detection.invalid_chars.length > 0 ? 
                        '<p><strong>Invalid characters found:</strong> ' + analysisData.detection.invalid_chars.join(', ') + '</p>' : ''}
                `;
                return;
            }

            // If DNA, show strand selection
            if (analysisData.detection.type === 'DNA') {
                showStep('step-strand');
            } else {
                // RNA - skip strand selection, go straight to transcription
                showTranscription();
            }

        } catch (e) {
            alert('Analysis failed. Please try again.');
            console.error(e);
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<span class="btn-icon">🔬</span> Analyze Sequence';
        }
    });

    // ==================== STRAND TYPE SELECTION ====================
    btnContinueStrand.addEventListener('click', () => {
        const selected = document.querySelector('input[name="strandType"]:checked');
        currentStrandType = selected ? selected.value : 'non-template';

        // Re-analyze with strand type
        fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sequence: currentSequence,
                strand_type: currentStrandType
            })
        })
        .then(r => r.json())
        .then(data => {
            analysisData = data;
            showTranscription();
        });
    });

    // ==================== DISPLAY FUNCTIONS ====================
    function hideAllSteps() {
        document.querySelectorAll('.step-section:not(#step-input)').forEach(s => {
            s.classList.add('hidden');
            s.classList.remove('active');
        });
    }

    function showStep(stepId) {
        const step = document.getElementById(stepId);
        step.classList.remove('hidden');
        step.classList.add('active');
        step.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showDetection(detection) {
        showStep('step-detection');
        const resultDiv = document.getElementById('detectionResult');
        const explDiv = document.getElementById('detectionExplanation');

        const typeClass = detection.type.toLowerCase();
        const icon = detection.type === 'DNA' ? '🧬' : detection.type === 'RNA' ? '🧪' : '⚠️';
        const title = detection.type === 'invalid'
            ? 'Invalid Sequence'
            : detection.ambiguous
                ? 'DNA Sequence Assumed'
                : detection.type + ' Sequence Detected';

        resultDiv.className = 'detection-result ' + typeClass;
        resultDiv.innerHTML = `
            <span class="detection-icon">${icon}</span>
            <div class="detection-info ${typeClass}">
                <h3>${title}</h3>
                <span class="detection-meta">Confidence: ${detection.confidence}%</span>
            </div>
        `;

        explDiv.innerHTML = formatExplanation('How we detected this:', detection.explanation);
    }

    function showTranscription() {
        showStep('step-transcription');
        const tx = analysisData.transcription;

        document.getElementById('transcriptionExplanation').innerHTML =
            formatExplanation('What is Transcription?', tx.explanation);

        document.getElementById('inputSeqDisplay').textContent = currentSequence;
        document.getElementById('mrnaDisplay').textContent = tx.mrna;

        // Auto-advance to translation after a brief delay
        setTimeout(() => {
            showTranslation();
        }, 500);
    }

    function showTranslation() {
        showStep('step-translation');
        const tr = analysisData.translation;

        if (tr.error) {
            document.getElementById('translationExplanation').innerHTML =
                formatExplanation('Translation Error:', tr.explanation);
            document.getElementById('codonTableBody').innerHTML =
                '<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--accent);">' +
                'No translation possible — ' + formatMarkdown(tr.explanation) + '</td></tr>';
            return;
        }

        document.getElementById('translationExplanation').innerHTML =
            formatExplanation('What is Translation?', tr.explanation);

        // Build codon table
        const tbody = document.getElementById('codonTableBody');
        tbody.innerHTML = '';

        tr.amino_acids.forEach((aa, i) => {
            const row = document.createElement('tr');
            const codonClass = aa.is_start ? 'codon-start' : aa.is_stop ? 'codon-stop' : 'codon-normal';
            const badgeClass = aa.is_start ? 'badge-start' : aa.is_stop ? 'badge-stop' : 'badge-normal';
            const badgeText = aa.is_start ? 'START' : aa.is_stop ? 'STOP' : 'CODON';

            row.innerHTML = `
                <td>${i + 1}</td>
                <td class="${codonClass}">${aa.codon}</td>
                <td>${aa.name}</td>
                <td>${aa.three_letter}</td>
                <td class="${codonClass}">${aa.one_letter}</td>
                <td><span class="badge ${badgeClass}">${badgeText}</span></td>
            `;
            tbody.appendChild(row);
        });

        // Auto-advance to amino acids
        setTimeout(() => {
            showAminoAcids();
        }, 500);
    }

    function showAminoAcids() {
        showStep('step-amino');
        const tr = analysisData.translation;

        document.getElementById('aminoAcidsExplanation').innerHTML =
            formatExplanation('What are Amino Acids?', analysisData.amino_acids_explanation);

        document.getElementById('polypeptideSeq').textContent = tr.polypeptide;

        const threeLetter = tr.amino_acids
            .filter(aa => aa.name !== 'Stop')
            .map(aa => aa.three_letter)
            .join(' — ');
        document.getElementById('polypeptideSeq3').textContent = threeLetter;

        // Auto-advance to protein
        setTimeout(() => {
            showProtein();
        }, 500);
    }

    function showProtein() {
        showStep('step-protein');
        const protein = analysisData.protein;

        if (!protein) {
            document.getElementById('proteinExplanation').innerHTML =
                formatExplanation('No Protein Produced:', 'Translation did not produce a valid polypeptide chain, so no protein characterization is available.');
            document.getElementById('proteinStats').innerHTML = '';
            document.getElementById('uniprotSection').style.display = 'none';
            return;
        }

        document.getElementById('proteinExplanation').innerHTML =
            formatExplanation('What is a Protein?', protein.explanation);

        const char = protein.characterization;
        document.getElementById('proteinStats').innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${char.length}</div>
                <div class="stat-label">Amino Acids</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">~${char.molecular_weight_approx.toLocaleString()}</div>
                <div class="stat-label">Da (Molecular Weight)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${char.dominant_property}</div>
                <div class="stat-label">Dominant Property</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${char.isoelectric_estimate}</div>
                <div class="stat-label">Charge Character</div>
            </div>
        `;

        // UniProt results
        const uniprot = protein.uniprot;
        document.getElementById('uniprotExplanation').innerHTML = formatMarkdown(uniprot.explanation);

        const resultsDiv = document.getElementById('uniprotResults');
        resultsDiv.innerHTML = '';

        if (uniprot.demo_mode) {
            const demoBadge = document.createElement('span');
            demoBadge.className = 'demo-badge';
            demoBadge.textContent = 'DEMO MODE — Live API temporarily unavailable';
            resultsDiv.appendChild(demoBadge);
        }

        uniprot.results.forEach(result => {
            const card = document.createElement('div');
            card.className = 'uniprot-card';
            card.innerHTML = `
                <div class="uniprot-card-header">
                    <h4>${result.protein_name}</h4>
                    <span class="uniprot-id">${result.uniprot_id}</span>
                </div>
                <div class="uniprot-meta">
                    <strong>Organism:</strong> ${result.organism} &nbsp;|&nbsp;
                    <strong>Gene:</strong> ${result.gene} &nbsp;|&nbsp;
                    <strong>Length:</strong> ${result.sequence_length} aa
                </div>
                <div class="uniprot-function">${result.function}</div>
            `;
            resultsDiv.appendChild(card);
        });
    }

    // ==================== UTILITY ====================
    function formatExplanation(label, text) {
        return '<strong>' + escapeHtml(label) + '</strong> ' + formatMarkdown(text);
    }

    function formatMarkdown(text) {
        return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});
