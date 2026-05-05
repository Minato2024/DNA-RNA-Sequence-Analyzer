# 🧬 DNA & RNA Sequence Analyzer

**CSC 442 — Computational Biology & Interdisciplinary Studies**
Faculty of Physical Sciences, Department of Computer Science
2024/2025 Second Semester

## Project Overview

A web-based application that analyzes DNA and RNA sequences and walks users through the fundamental processes of molecular biology — from a raw nucleotide sequence all the way to a characterized protein, with plain-English explanations at every step.

## Features

### 1. Sequence Input (10 marks)
Three ways to input sequences:
- **Type/Paste**: Direct text entry with live validation
- **File Upload**: Browse and select .txt, .fasta, .fa, or .seq files
- **Upload Drag & Drop**: Drop files directly onto the file upload area

### 2. Sequence Type Detection (15 marks)
- Automatic DNA/RNA identification
- Invalid sequence detection (mixed T/U, invalid characters)
- Plain-English explanation of detection method
- Live validation feedback as you type

### 3. DNA Strand Type (Implicit in Transcription)
- For DNA sequences: user selects Non-Template (Coding/Sense) or Template (Antisense) strand
- Affects how transcription is performed
- Option hidden for RNA input

### 4. Transcription (15 marks)
- Produces mRNA from DNA
- Handles both strand types correctly
- Displays input sequence and resulting mRNA
- Plain-English explanation of the transcription process

### 5. Translation (20 marks)
- Reads mRNA in codons (groups of 3 bases)
- Displays each codon with its amino acid
- Handles start codon (AUG) and stop codons (UAA, UAG, UGA)
- Plain-English explanation of translation

### 6. Amino Acids / Polypeptide Chain (15 marks)
- Full polypeptide chain displayed
- Names and abbreviations (3-letter and 1-letter)
- Plain-English explanation of amino acids and polypeptides

### 7. Protein Characterization & Database Lookup (20 marks)
- Protein composition and properties
- Molecular weight estimation
- Amino acid composition analysis
- **UniProt database search** via REST API
- Real protein names, organisms, and functions
- Plain-English explanations throughout

### Overall Quality (5 marks)
- Clean, responsive interface
- Progressive disclosure (steps appear sequentially)
- All explanations written for non-scientists
- Smooth animations and visual feedback

## Biological Pipeline

```
Raw Sequence → Type Detection → (Strand Selection if DNA) → Transcription → Translation → Amino Acids → Protein + UniProt Search
```

## Technical Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript (no frameworks needed)
- **Styling**: Custom CSS with CSS variables
- **Database**: UniProt REST API (protein search)
- **Hosting**: Render / Railway / PythonAnywhere (free tiers)

## Genetic Code

The application implements the full standard genetic code with all 64 codons mapping to 20 amino acids plus 3 stop codons.

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open in browser
http://localhost:5000
```

## Deployment

### Render (Recommended)
1. Push code to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`

### Railway
1. Push code to GitHub
2. Deploy from [railway.app](https://railway.app)
3. Environment variable: `PORT=5000`

### PythonAnywhere
1. Upload files to [pythonanywhere.com](https://pythonanywhere.com)
2. Configure WSGI to point to `app.py`
3. Reload web app

## File Structure

```
project2/
├── app.py                    # Flask application
├── requirements.txt          # Dependencies
├── Procfile                  # Hosting configuration
├── static/
│   ├── css/style.css         # Stylesheet
│   ├── js/app.js             # Frontend logic
│   └── uploads/              # File uploads (if needed)
└── templates/
    └── index.html            # Single-page application
```

## Marking Scheme Compliance

| Component | Marks | Status |
|-----------|-------|--------|
| Sequence Input | 10 | ✅ Type/paste and file upload with drag & drop |
| Sequence Detection | 15 | ✅ DNA/RNA ID, invalid detection, explanation |
| Transcription | 15 | ✅ mRNA for both strand types, explanation |
| Translation | 20 | ✅ Codon reading, amino acids, start/stop, explanation |
| Amino Acids | 15 | ✅ Polypeptide chain, names/abbreviations, explanation |
| Protein & Database | 20 | ✅ Characterization + UniProt API search |
| Overall Quality | 5 | ✅ Clean UI, all explanations present |
| **TOTAL** | **100** | |

## API Note

The UniProt REST API is used for protein database search. If the API is temporarily unavailable, the application gracefully falls back to demo mode with example results to demonstrate the expected functionality.

## Author
Individual Assignment — CSC 442, 400 Level
