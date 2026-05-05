"""
Project 2 - DNA & RNA Sequence Analyzer
CSC 442 - Computational Biology & Interdisciplinary Studies

A web-based application that analyzes DNA and RNA sequences,
walking users through transcription, translation, and protein
characterization with plain-English explanations.
"""

from flask import Flask, render_template, request, jsonify
import re
import requests
import json

app = Flask(__name__)
app.secret_key = "dna_rna_analyzer_secret_key_2025"

# ==========================================
# GENETIC CODE - CODON TO AMINO ACID MAPPING
# ==========================================
GENETIC_CODE = {
    # Phenylalanine
    "UUU": ("Phenylalanine", "Phe", "F"),
    "UUC": ("Phenylalanine", "Phe", "F"),
    # Leucine
    "UUA": ("Leucine", "Leu", "L"),
    "UUG": ("Leucine", "Leu", "L"),
    "CUU": ("Leucine", "Leu", "L"),
    "CUC": ("Leucine", "Leu", "L"),
    "CUA": ("Leucine", "Leu", "L"),
    "CUG": ("Leucine", "Leu", "L"),
    # Isoleucine
    "AUU": ("Isoleucine", "Ile", "I"),
    "AUC": ("Isoleucine", "Ile", "I"),
    "AUA": ("Isoleucine", "Ile", "I"),
    # Methionine (Start)
    "AUG": ("Methionine", "Met", "M"),
    # Valine
    "GUU": ("Valine", "Val", "V"),
    "GUC": ("Valine", "Val", "V"),
    "GUA": ("Valine", "Val", "V"),
    "GUG": ("Valine", "Val", "V"),
    # Serine
    "UCU": ("Serine", "Ser", "S"),
    "UCC": ("Serine", "Ser", "S"),
    "UCA": ("Serine", "Ser", "S"),
    "UCG": ("Serine", "Ser", "S"),
    "AGU": ("Serine", "Ser", "S"),
    "AGC": ("Serine", "Ser", "S"),
    # Proline
    "CCU": ("Proline", "Pro", "P"),
    "CCC": ("Proline", "Pro", "P"),
    "CCA": ("Proline", "Pro", "P"),
    "CCG": ("Proline", "Pro", "P"),
    # Threonine
    "ACU": ("Threonine", "Thr", "T"),
    "ACC": ("Threonine", "Thr", "T"),
    "ACA": ("Threonine", "Thr", "T"),
    "ACG": ("Threonine", "Thr", "T"),
    # Alanine
    "GCU": ("Alanine", "Ala", "A"),
    "GCC": ("Alanine", "Ala", "A"),
    "GCA": ("Alanine", "Ala", "A"),
    "GCG": ("Alanine", "Ala", "A"),
    # Tyrosine
    "UAU": ("Tyrosine", "Tyr", "Y"),
    "UAC": ("Tyrosine", "Tyr", "Y"),
    # Stop codons
    "UAA": ("Stop", "Stop", "*"),
    "UAG": ("Stop", "Stop", "*"),
    "UGA": ("Stop", "Stop", "*"),
    # Histidine
    "CAU": ("Histidine", "His", "H"),
    "CAC": ("Histidine", "His", "H"),
    # Glutamine
    "CAA": ("Glutamine", "Gln", "Q"),
    "CAG": ("Glutamine", "Gln", "Q"),
    # Asparagine
    "AAU": ("Asparagine", "Asn", "N"),
    "AAC": ("Asparagine", "Asn", "N"),
    # Lysine
    "AAA": ("Lysine", "Lys", "K"),
    "AAG": ("Lysine", "Lys", "K"),
    # Aspartic Acid
    "GAU": ("Aspartic Acid", "Asp", "D"),
    "GAC": ("Aspartic Acid", "Asp", "D"),
    # Glutamic Acid
    "GAA": ("Glutamic Acid", "Glu", "E"),
    "GAG": ("Glutamic Acid", "Glu", "E"),
    # Cysteine
    "UGU": ("Cysteine", "Cys", "C"),
    "UGC": ("Cysteine", "Cys", "C"),
    # Tryptophan
    "UGG": ("Tryptophan", "Trp", "W"),
    # Arginine
    "CGU": ("Arginine", "Arg", "R"),
    "CGC": ("Arginine", "Arg", "R"),
    "CGA": ("Arginine", "Arg", "R"),
    "CGG": ("Arginine", "Arg", "R"),
    "AGA": ("Arginine", "Arg", "R"),
    "AGG": ("Arginine", "Arg", "R"),
    # Glycine
    "GGU": ("Glycine", "Gly", "G"),
    "GGC": ("Glycine", "Gly", "G"),
    "GGA": ("Glycine", "Gly", "G"),
    "GGG": ("Glycine", "Gly", "G"),
}

# Amino acid properties for characterization
AMINO_ACID_PROPERTIES = {
    "Alanine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Arginine": {"type": "Basic", "charge": "Positive", "polarity": "Polar"},
    "Asparagine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Aspartic Acid": {"type": "Acidic", "charge": "Negative", "polarity": "Polar"},
    "Cysteine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Glutamic Acid": {"type": "Acidic", "charge": "Negative", "polarity": "Polar"},
    "Glutamine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Glycine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Histidine": {"type": "Basic", "charge": "Positive", "polarity": "Polar"},
    "Isoleucine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Leucine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Lysine": {"type": "Basic", "charge": "Positive", "polarity": "Polar"},
    "Methionine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Phenylalanine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Proline": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Serine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Threonine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Tryptophan": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
    "Tyrosine": {"type": "Polar", "charge": "Neutral", "polarity": "Polar"},
    "Valine": {"type": "Non-polar", "charge": "Neutral", "polarity": "Non-polar"},
}


# ==========================================
# BIOLOGICAL FUNCTIONS
# ==========================================

def clean_sequence(sequence):
    """Remove whitespace and convert to uppercase."""
    return re.sub(r'[^ATCGUatcgu]', '', sequence).upper()

def sequence_for_detection(sequence):
    """Normalize sequence text for validation without discarding invalid bases."""
    lines = sequence.splitlines()
    sequence_lines = [line.strip() for line in lines if not line.strip().startswith(">")]
    return re.sub(r'\s+', '', ''.join(sequence_lines)).upper()

def detect_sequence_type(sequence):
    """
    Detect whether a sequence is DNA, RNA, or invalid.

    Returns:
        dict with keys: type, confidence, explanation, invalid_chars
    """
    normalized = sequence_for_detection(sequence)

    if not normalized:
        return {
            "type": "invalid",
            "confidence": 0,
            "explanation": "The sequence contains no valid nucleotide characters. A valid sequence must contain only A, T, C, G (for DNA) or A, U, C, G (for RNA).",
            "invalid_chars": [],
            "ambiguous": False
        }

    invalid_chars = sorted({c for c in normalized if c not in "ATCGU"})
    has_t = "T" in normalized
    has_u = "U" in normalized

    if invalid_chars:
        return {
            "type": "invalid",
            "confidence": 0,
            "explanation": f"The sequence contains invalid characters: {', '.join(invalid_chars)}. Valid nucleotides are only A, T, C, G (for DNA) or A, U, C, G (for RNA).",
            "invalid_chars": invalid_chars,
            "ambiguous": False
        }

    if has_t and has_u:
        return {
            "type": "invalid",
            "confidence": 0,
            "explanation": "The sequence contains both T (thymine) and U (uracil). A valid biological sequence cannot contain both — DNA uses T, while RNA uses U. This suggests the sequence may be corrupted or incorrectly entered.",
            "invalid_chars": [],
            "ambiguous": False
        }

    if has_u and not has_t:
        return {
            "type": "RNA",
            "confidence": 100,
            "explanation": "This is an RNA sequence. We detected the presence of Uracil (U) and the absence of Thymine (T). In nature, RNA uses Uracil instead of Thymine, which is found only in DNA. The sequence contains only valid RNA nucleotides: A (Adenine), U (Uracil), C (Cytosine), and G (Guanine).",
            "invalid_chars": [],
            "ambiguous": False
        }

    if has_t and not has_u:
        return {
            "type": "DNA",
            "confidence": 100,
            "explanation": "This is a DNA sequence. We detected the presence of Thymine (T) and the absence of Uracil (U). DNA uses Thymine (T) as one of its four nucleotide bases, while RNA uses Uracil (U) instead. The sequence contains only valid DNA nucleotides: A (Adenine), T (Thymine), C (Cytosine), and G (Guanine).",
            "invalid_chars": [],
            "ambiguous": False
        }

    # Neither T nor U — ambiguous but could be DNA (default assumption)
    return {
        "type": "DNA",
        "confidence": 50,
        "explanation": "This sequence contains only A, C, and G, so there is no Thymine (T) or Uracil (U) marker to distinguish DNA from RNA. The app will treat it as DNA by default for the remaining analysis, but biologically this input is ambiguous.",
        "invalid_chars": [],
        "ambiguous": True
    }


def transcribe_dna(dna_sequence, strand_type="non-template"):
    """
    Transcribe DNA to mRNA.

    Args:
        dna_sequence: The DNA sequence
        strand_type: "non-template" (coding/sense) or "template" (antisense)

    Returns:
        dict with mRNA sequence and explanation
    """
    dna = clean_sequence(dna_sequence)

    if strand_type == "non-template":
        # Non-template (coding) strand: replace T with U directly
        mrna = dna.replace("T", "U")
        explanation = (
            "You provided the **Non-Template Strand** (also called the Coding Strand or Sense Strand). "
            "This strand has the same sequence as the mRNA, except that Thymine (T) is replaced by Uracil (U). "
            "Think of the non-template strand as the 'readable' version — it directly tells us what the mRNA will look like. "
            "We simply replaced every T with U to get the mRNA sequence."
        )
    else:
        # Template (antisense) strand: complement then replace T with U
        complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
        template_complement = "".join(complement.get(base, base) for base in dna)
        mrna = template_complement.replace("T", "U")
        explanation = (
            "You provided the **Template Strand** (also called the Antisense Strand). "
            "This is the strand that RNA polymerase actually reads during transcription. "
            "Because the template strand is complementary to the mRNA, we first find its complement "
            "(A→T, T→A, C→G, G→C), and then replace Thymine (T) with Uracil (U) to get the final mRNA. "
            "The resulting mRNA is identical to the non-template (coding) strand."
        )

    return {
        "mrna": mrna,
        "explanation": explanation,
        "strand_type": strand_type
    }


def transcribe_rna(rna_sequence):
    """
    If input is already RNA, return it as mRNA.
    """
    rna = clean_sequence(rna_sequence)
    return {
        "mrna": rna,
        "explanation": (
            "You provided an RNA sequence directly. Since the input is already RNA, "
            "no transcription is needed — the sequence itself serves as the mRNA. "
            "Transcription is the process of creating mRNA from DNA, so when we start with RNA, "
            "we skip this step and proceed directly to translation."
        ),
        "strand_type": "RNA"
    }


def translate_mrna(mrna_sequence):
    """
    Translate mRNA to amino acids (polypeptide chain).

    Returns:
        dict with codons, amino acids, and explanations
    """
    mrna = clean_sequence(mrna_sequence).replace("T", "U")

    # Find start codon (AUG)
    start_index = mrna.find("AUG")

    if start_index == -1:
        return {
            "error": True,
            "explanation": (
                "No start codon (AUG) was found in the mRNA sequence. "
                "Translation cannot begin without a start codon, which signals the ribosome where to start reading. "
                "AUG codes for Methionine and is the universal start signal for protein synthesis."
            ),
            "codons": [],
            "amino_acids": [],
            "polypeptide": ""
        }

    # Start from AUG
    coding_region = mrna[start_index:]

    # Split into codons
    codons = [coding_region[i:i+3] for i in range(0, len(coding_region), 3) if len(coding_region[i:i+3]) == 3]

    amino_acids = []
    stopped = False

    for codon in codons:
        aa_info = GENETIC_CODE.get(codon, ("Unknown", "???", "?"))
        amino_acids.append({
            "codon": codon,
            "name": aa_info[0],
            "three_letter": aa_info[1],
            "one_letter": aa_info[2],
            "is_start": codon == "AUG",
            "is_stop": aa_info[0] == "Stop"
        })
        if aa_info[0] == "Stop":
            stopped = True
            break

    # Build polypeptide chain (exclude stop codon)
    polypeptide = "".join([aa["one_letter"] for aa in amino_acids if aa["name"] != "Stop"])

    explanation = (
        "**Translation** is the process where the ribosome reads the mRNA in groups of three bases called **codons**. "
        "Each codon specifies one amino acid. The ribosome starts at the **start codon AUG** (Methionine) and continues "
        "reading until it encounters a **stop codon** (UAA, UAG, or UGA), which signals the end of translation. "
        "In your sequence, we found the start codon at position " + str(start_index + 1) + ". "
        "We then read the mRNA three bases at a time, matching each codon to its corresponding amino acid using the genetic code."
    )

    return {
        "error": False,
        "explanation": explanation,
        "codons": codons,
        "amino_acids": amino_acids,
        "polypeptide": polypeptide,
        "start_position": start_index + 1,
        "stopped": stopped
    }


def characterize_protein(polypeptide, amino_acids):
    """
    Characterize the protein based on its amino acid composition.
    """
    if not polypeptide:
        return {
            "length": 0,
            "molecular_weight": 0,
            "properties": {},
            "explanation": "No protein was produced because no valid translation occurred."
        }

    # Calculate approximate molecular weight (average amino acid ≈ 110 Da)
    mw = len(polypeptide) * 110

    # Count properties
    properties_count = {"Non-polar": 0, "Polar": 0, "Acidic": 0, "Basic": 0}
    charge_count = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for aa in amino_acids:
        if aa["name"] == "Stop":
            continue
        props = AMINO_ACID_PROPERTIES.get(aa["name"], {})
        aa_type = props.get("type", "Unknown")
        charge = props.get("charge", "Neutral")
        if aa_type in properties_count:
            properties_count[aa_type] += 1
        if charge in charge_count:
            charge_count[charge] += 1

    total = sum(properties_count.values())

    # Determine dominant property
    dominant = max(properties_count, key=properties_count.get)

    characterization = {
        "length": len(polypeptide),
        "molecular_weight_approx": mw,
        "amino_acid_composition": properties_count,
        "charge_distribution": charge_count,
        "dominant_property": dominant,
        "isoelectric_estimate": "acidic" if charge_count["Negative"] > charge_count["Positive"] else 
                                  "basic" if charge_count["Positive"] > charge_count["Negative"] else "neutral"
    }

    explanation = (
        "A **protein** is a functional molecule made from one or more polypeptide chains. "
        "After translation, the polypeptide chain folds into a specific 3D shape to become a working protein. "
        "Your protein is " + str(characterization["length"]) + " amino acids long with an approximate molecular weight of " + 
        f"{mw:,}" + " Daltons. "
        "The amino acid composition determines the protein's properties: "
        f"{properties_count['Non-polar']} non-polar, {properties_count['Polar']} polar, "
        f"{properties_count['Acidic']} acidic, and {properties_count['Basic']} basic amino acids. "
        "The overall charge character is estimated as **" + characterization["isoelectric_estimate"] + "**."
    )

    return {
        "characterization": characterization,
        "explanation": explanation
    }


def search_uniprot(protein_sequence):
    """
    Search UniProt for similar protein sequences.
    Uses UniProt's peptide search API.
    """
    try:
        # For demo purposes, we'll use a mock search or try the UniProt API
        # UniProt peptide search endpoint
        url = "https://rest.uniprot.org/uniprotkb/search"

        # Search with the peptide sequence
        params = {
            "query": protein_sequence[:30] if len(protein_sequence) > 30 else protein_sequence,
            "format": "json",
            "size": 5
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            results = []
            for result in data.get("results", [])[:3]:
                protein_name = result.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown Protein")
                organism = result.get("organism", {}).get("scientificName", "Unknown Organism")
                gene = result.get("genes", [{}])[0].get("geneName", {}).get("value", "N/A") if result.get("genes") else "N/A"
                function_text = ""
                comments = result.get("comments", [])
                for comment in comments:
                    if comment.get("commentType") == "FUNCTION":
                        texts = comment.get("texts", [])
                        if texts:
                            function_text = texts[0].get("value", "No function description available.")
                        break

                results.append({
                    "protein_name": protein_name,
                    "organism": organism,
                    "gene": gene,
                    "function": function_text[:200] + "..." if len(function_text) > 200 else function_text,
                    "uniprot_id": result.get("primaryAccession", "N/A"),
                    "sequence_length": result.get("sequence", {}).get("length", "N/A")
                })

            return {
                "success": True,
                "results": results,
                "explanation": (
                    "We searched the **UniProt** database — the world's most comprehensive resource for protein information — "
                    "to find real-world proteins that match or are similar to your sequence. "
                    "The results below show actual proteins from living organisms, along with their names, "
                    "the organisms they come from, and what biological functions they perform. "
                    "This helps connect your theoretical sequence to real biology."
                )
            }
        else:
            return mock_uniprot_results(protein_sequence)

    except Exception as e:
        return mock_uniprot_results(protein_sequence)


def mock_uniprot_results(protein_sequence):
    """Return demo UniProt results when API is unavailable."""
    return {
        "success": True,
        "demo_mode": True,
        "results": [
            {
                "protein_name": "Cytochrome c",
                "organism": "Homo sapiens (Human)",
                "gene": "CYCS",
                "function": "Electron carrier protein. The oxidized form of the cytochrome c heme group can accept an electron from the bc1 complex and transfer it to the cytochrome oxidase complex.",
                "uniprot_id": "P99999",
                "sequence_length": 105
            },
            {
                "protein_name": "Hemoglobin subunit beta",
                "organism": "Homo sapiens (Human)",
                "gene": "HBB",
                "function": "Involved in oxygen transport from the lung to the various peripheral tissues. Hemoglobin beta binds to oxygen in the capillaries of the lung and transports it to tissues.",
                "uniprot_id": "P68871",
                "sequence_length": 147
            },
            {
                "protein_name": "Insulin",
                "organism": "Homo sapiens (Human)",
                "gene": "INS",
                "function": "Insulin decreases blood glucose concentration. It increases cell permeability to monosaccharides, amino acids and fatty acids. It accelerates glycolysis, the pentose phosphate cycle, and glycogen synthesis in liver.",
                "uniprot_id": "P01308",
                "sequence_length": 110
            }
        ],
        "explanation": (
            "We attempted to search the **UniProt** database for proteins matching your sequence. "
            "While the live database connection may be temporarily unavailable, the examples below demonstrate "
            "the type of information a successful search would return: real protein names, their source organisms, "
            "and their biological functions. In a production environment with stable API access, "
            "these would be actual matches to your specific sequence."
        )
    }


# ==========================================
# FLASK ROUTES
# ==========================================

@app.route("/")
def index():
    """Main application page."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Main analysis endpoint."""
    data = request.get_json()
    sequence = data.get("sequence", "").strip()
    strand_type = data.get("strand_type", "non-template")

    if not sequence:
        return jsonify({"error": "No sequence provided"}), 400

    # Step 1: Detect sequence type
    detection = detect_sequence_type(sequence)

    if detection["type"] == "invalid":
        return jsonify({
            "detection": detection,
            "transcription": None,
            "translation": None,
            "amino_acids": None,
            "protein": None
        })

    # Step 2: Transcription
    if detection["type"] == "DNA":
        transcription = transcribe_dna(sequence, strand_type)
    else:
        transcription = transcribe_rna(sequence)

    # Step 3: Translation
    translation = translate_mrna(transcription["mrna"])

    # Step 4: Amino Acids (included in translation)
    amino_acids_explanation = (
        "**Amino acids** are the building blocks of proteins. There are 20 different amino acids in nature, "
        "each with unique chemical properties. When linked together in a chain, they form a **polypeptide**. "
        "The sequence of amino acids determines how the chain will fold into a functional protein. "
        "Each amino acid has a full name (e.g., Methionine), a three-letter abbreviation (e.g., Met), "
        "and a one-letter code (e.g., M). Your polypeptide chain contains the following amino acids:"
    )

    # Step 5: Protein characterization
    protein = None
    if not translation.get("error") and translation["polypeptide"]:
        protein = characterize_protein(translation["polypeptide"], translation["amino_acids"])

        # Search UniProt
        uniprot_results = search_uniprot(translation["polypeptide"])
        protein["uniprot"] = uniprot_results

    return jsonify({
        "detection": detection,
        "transcription": transcription,
        "translation": translation,
        "amino_acids_explanation": amino_acids_explanation,
        "protein": protein
    })


@app.route("/api/validate", methods=["POST"])
def validate():
    """Quick validation endpoint for real-time feedback."""
    data = request.get_json()
    sequence = data.get("sequence", "").strip()
    detection = detect_sequence_type(sequence)
    return jsonify(detection)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
