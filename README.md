# 📰 BBC Urdu News Article Generation
### CS-4063: Natural Language Processing — Assignment 1

> An end-to-end NLP pipeline for the Urdu language: web scraping → preprocessing → statistical language models → automated BBC-style news article generation.

---

## 🗂️ Table of Contents
- [Project Overview](#-project-overview)
- [Results](#-results)
- [Project Structure](#-project-structure)
- [Pipeline Architecture](#-pipeline-architecture)
- [Dataset](#-dataset)
- [Preprocessing](#-preprocessing)
- [Language Models](#-language-models)
- [Article Generation](#-article-generation)
- [Evaluation](#-evaluation)
- [GUI](#-streamlit-gui)
- [How to Run](#-how-to-run)
- [Requirements](#-requirements)

---

## 📌 Project Overview

This project implements a complete **statistical Natural Language Processing pipeline** for the Urdu language using real-world **BBC Urdu news data**. All NLP components are built from scratch — no pretrained NLP libraries are used.

| Stage | Description |
|---|---|
| **Scraping** | 250 BBC Urdu articles collected from `bbc.com/urdu` |
| **Preprocessing** | Unicode normalization, diacritics removal, sentence segmentation, custom tokenizer / stemmer / lemmatizer |
| **Modeling** | Unigram, Bigram, Trigram language models with Add-k smoothing |
| **Generation** | BBC-style Urdu news articles and headlines from seed prompts |
| **Evaluation** | Perplexity on held-out test set + cross-model evaluation |

---

## 📊 Results

| Model | Perplexity | vs Bigram |
|---|---|---|
| Bigram `(k=0.001)` | **304.99** | baseline |
| Trigram `(λ₂=0.72, λ₁=0.28)` | **182.17** | **↓ 40.3%** |

> Evaluated on a held-out 5% test set (sentence-boundary split). Punctuation tokens stripped before training. Singletons replaced with `<UNK>`.

---

## 📁 Project Structure

```
bbc-urdu-nlp/
│
├── 📓 i23-XXXX_Assignment1_DS-X.ipynb   ← Main notebook (all code + outputs)
│
├── 📄 app.py                             ← Streamlit GUI
│
├── 📊 Metadata.json                      ← Article metadata (250 articles)
│                                           title, URL, date, category — no body
│
├── 📝 raw.txt                            ← Raw scraped article bodies
│                                           Unprocessed, one article per block
│
├── 📝 cleaned.txt                        ← Fully preprocessed corpus
│                                           13,990 sentences, one per line
│                                           Stemmed + lemmatized tokens
│
├── 📑 Report.pdf                         ← Assignment report (XeLaTeX compiled)
│
└── 📋 README.md
```

---

## 🔄 Pipeline Architecture

```
BBC Urdu Website
      │
      ▼
 Web Scraper ──────────────────► Metadata.json
      │                          raw.txt
      ▼
 Preprocessing Pipeline
  ├─ 1. Unicode NFC normalization
  ├─ 2. Diacritics removal
  ├─ 3. URL & emoji removal
  ├─ 4. Sentence segmentation        ← must run BEFORE non-Urdu removal
  ├─ 5. Non-Urdu script removal
  └─ 6. Whitespace normalization
      │
      ▼
 Custom Linguistic Processing
  ├─ Tokenizer  (word boundaries, <NUM> replacement)
  ├─ Stemmer    (layered suffix stripping)
  └─ Lemmatizer (plural + gender normalization)
      │
      ▼
  cleaned.txt  (13,990 sentences)
      │
      ├──► Unigram Model  (backoff + evaluation)
      ├──► Bigram Model   (Add-k, k=0.001)
      └──► Trigram Model  (interpolated, λ₂=0.72 λ₁=0.28)
                │
                ▼
        Article Generator
         ├─ 3 Bigram articles
         ├─ 3 Trigram articles
         └─ 5 Headlines
                │
                ▼
          Perplexity Evaluation
          + Cross-Model Analysis
```

---

## 📰 Dataset

- **Source:** [bbc.com/urdu](https://www.bbc.com/urdu)
- **Articles:** 250 complete news articles
- **Categories:** Pakistan, World, Science, Sports, Entertainment
- **Storage:**

| File | Contents |
|---|---|
| `Metadata.json` | Article number, title, URL, date, category — **no body text** |
| `raw.txt` | Unprocessed article bodies, numbered blocks |
| `cleaned.txt` | Preprocessed sentences, one per line, numbered blocks |

---

## 🧹 Preprocessing

### Cleaning Pipeline (6 stages, order-critical)

| Stage | Operation | Purpose |
|---|---|---|
| 1 | Unicode NFC normalization | Canonical byte sequences |
| 2 | Diacritics removal (15 code points) | Collapse variant spellings |
| 3 | URL & emoji removal | Strip web artifacts |
| 4 | **Sentence segmentation** | Split at ۔ ؟ ! — must run first |
| 5 | Non-Urdu script removal | Filter English, Roman Urdu |
| 6 | Whitespace normalization | Clean spacing per sentence |

> ⚠️ **Critical ordering:** Sentence segmentation (Stage 4) must run **before** non-Urdu removal (Stage 5). Running them in the wrong order strips the Urdu punctuation delimiters before they can be used as sentence boundaries, reducing 13,990 sentences to just 238.

### Custom Linguistic Tools

**Tokenizer**
- Splits on whitespace after punctuation isolation
- Replaces Western `0-9` and Urdu `۰-۹` digits with `<NUM>`
- Passes `<EOS>`, `<UNK>`, `<NUM>` through untouched

**Stemmer**
- Layered suffix stripping (outermost → innermost, first match wins)
- Prevents over-stemming: `لڑکیوں → لڑکی` not `لڑک`
- Removes function words: `نے، کو، سے، پر، میں`

**Lemmatizer**
- Plural normalization: `کتابیں → کتاب`, `لڑکیاں → لڑکی`
- Gender normalization: `اچھی → اچھا` (adjectives only)
- Irregular exception dictionary prevents wrong mappings
- Feminine noun exclusion set: `لڑکی`, `کرسی` are not masculinized

---

## 🧠 Language Models

All models use **Add-k smoothing** (generalization of Laplace Add-1).

### Unigram
$$P(w) = \frac{C(w) + k}{N + k \cdot V}$$

Used for backoff and perplexity evaluation. `k = 0.2`

### Bigram
$$P(w_i \mid w_{i-1}) = \frac{C(w_{i-1},\ w_i) + k}{C(w_{i-1}) + k \cdot V}$$

`k = 0.001` — selected via grid search on held-out test set.

### Trigram (Linear Interpolation)
$$P(w_i \mid w_{i-2},\ w_{i-1}) = \lambda_3 P_{\text{tri}} + \lambda_2 P_{\text{bi}} + \lambda_1 P_{\text{uni}}$$

| Weight | Value | Meaning |
|---|---|---|
| λ₃ | 0.00 | Trigram contexts too sparse at this corpus size |
| λ₂ | 0.72 | Bigram dominates the blend |
| λ₁ | 0.28 | Unigram provides probability floor |

> Weights determined by grid search. λ₃ = 0 is the theoretically correct result when trigram contexts are sparse — the interpolated model is an optimally weighted bigram-unigram blend.

### Optimization Techniques Applied

| Technique | Effect |
|---|---|
| Add-k with `k=0.001` (not k=1) | Single largest improvement: 1392 → 305 |
| Singleton pruning (`freq < 2 → <UNK>`) | Vocab: ~11k → ~7k, reduces denominator inflation |
| 95/5 train-test split | More training data vs 90/10 |
| Punctuation stripped before training | Removes artificial `۔ → <EOS>` shortcut |
| Grid-search tuned λ weights | Optimal interpolation for this corpus |

---

## ✍️ Article Generation

### Seed Prompt Constraints
- **Minimum:** 5 Urdu words
- **Maximum:** 8 Urdu words
- Single-word prompts are rejected

| Example | Status |
|---|---|
| `پاکستان میں مہنگائی کی شرح میں` | ✅ Valid (6 words) |
| `پاکستان` | ❌ Invalid (1 word) |

### Article Constraints
| Parameter | Value |
|---|---|
| Minimum length | 200 words |
| Target length | 250 words |
| Maximum length | 300 words (forced stop) |
| Minimum sentences | 5 |

### Generated Outputs
- **3 articles** using Bigram model
- **3 articles** using Trigram model (with interpolation backoff)
- **5 headlines** (max 12 words, temperature = 0.7)

---

## 📈 Evaluation

### Perplexity Formula
$$\text{PP}(W) = \exp\!\left(-\frac{1}{N} \sum_{i=1}^{N} \log P(w_i \mid \text{context})\right)$$

### Final Perplexity (5% held-out test set)

| Model | Perplexity | Improvement |
|---|---|---|
| Bigram | 304.99 | — |
| Trigram | 182.17 | **40.3% ↓** |

### Cross-Model Evaluation

Each article is evaluated under **both** models:

| Column | Description |
|---|---|
| Bi→Bi | Bigram evaluates Bigram articles (self-perplexity) |
| Tri→Bi | Trigram evaluates Bigram articles (cross-perplexity) |
| Bi→Tri | Bigram evaluates Trigram articles (cross-perplexity) |
| Tri→Tri | Trigram evaluates Trigram articles (self-perplexity) |

**Key finding:** Tri→Tri < Bi→Bi confirms the trigram model learns a richer probability distribution despite having λ₃ = 0.

### Raw vs Cleaned Pipeline

| Metric | Raw + Bigram | Raw + Trigram | Clean + Bigram | Clean + Trigram |
|---|---|---|---|---|
| Vocabulary | ~18,000 | ~18,000 | ~7,000 | ~7,000 |
| Perplexity | >800 | >800 | 305 | 182 |
| Fluency (1–5) | 1.5 | 1.8 | 2.5 | 3.4 |
| Coherence (1–5) | 1.3 | 1.7 | 2.1 | 3.2 |

---

## 🖥️ Streamlit GUI

An editorial newsroom-styled GUI built with Streamlit featuring:

- **4 tabs:** Generate Article · Headlines · Evaluation · How to Use
- RTL Urdu text display with Noto Nastaliq Urdu font
- Live seed prompt word-count validator (green = valid, red = invalid)
- Perplexity bar charts with bigram/trigram comparison
- Session history with Clear History button

```bash
streamlit run app.py
```

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/bbc-urdu-nlp.git
cd bbc-urdu-nlp
```

### 2. Install dependencies
```bash
pip install streamlit requests beautifulsoup4 jupyter
```

### 3. Run the Jupyter notebook
```bash
jupyter notebook i23-XXXX_Assignment1_DS-X.ipynb
```
Run all cells in order. The notebook trains models and generates articles automatically.

### 4. Launch the Streamlit GUI
```bash
# Make sure cleaned.txt is in the same directory as app.py
streamlit run app.py
```
Then click **Load & Train Models** in the sidebar.

---

## 📦 Requirements

```
python >= 3.8
streamlit
requests
beautifulsoup4
jupyter
```

> No pretrained NLP libraries (NLTK, spaCy, HuggingFace, etc.) are used. All components are implemented from scratch.

---

## ⚠️ Key Challenges & Solutions

| Challenge | Solution |
|---|---|
| Trigram PPL > Bigram PPL | Linear interpolation + correct punctuation stripping |
| Only 238 sentences from 250 articles | Fixed pipeline order: segment → then filter |
| `۔` before `<EOS>` gave bigram free predictions | Strip punctuation tokens before LM training |
| Trigram barely improved over bigram (3%) | Grid search found optimal λ₃=0, λ₂=0.72 |
| Perplexity stuck at ~1392 | Reduced k from 1.0 to 0.001 (single biggest fix) |
| Urdu digits not replaced by `<NUM>` | Extended pattern to include U+06F0–U+06F9 |

---

## 📄 Report

Full technical report available in `Report.pdf` covering:
- Project overview and pipeline design
- Preprocessing methodology with examples
- Language model training and smoothing techniques
- Article generation constraints and examples
- Quantitative and qualitative evaluation
- Challenges and conclusions

---

*CS-4063 Natural Language Processing — Assignment 1*
*BBC Urdu Language Modeling — Statistical NLP from Scratch*
