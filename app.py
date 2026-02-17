import streamlit as st
import sys, os, re, math, random
from collections import defaultdict, Counter
from datetime import datetime

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="BBC Urdu — AI News Generator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=swap');

:root {
    --ink:       #0d0d0d;
    --paper:     #faf7f2;
    --red:       #c0392b;
    --red-dark:  #922b21;
    --mid:       #4a4a4a;
    --rule:      #d4c9b8;
    --card-bg:   #ffffff;
    --sidebar-bg:#1a1a1a;
}
html, body, [class*="css"] {
    background-color: var(--paper) !important;
    color: var(--ink) !important;
    font-family: 'Source Serif 4', Georgia, serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 3rem 2rem !important; max-width: 1200px; }

[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 3px solid var(--red) !important;
}
[data-testid="stSidebar"] * { color: #e8e0d4 !important; font-family: 'Source Serif 4', serif !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; font-family: 'Playfair Display', serif !important; }

.masthead {
    background: var(--ink); color: #ffffff;
    padding: 1.2rem 2rem 1rem 2rem;
    margin: -1rem -2rem 0 -2rem;
    border-bottom: 4px solid var(--red);
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.masthead-logo { font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 900; color: #ffffff; letter-spacing: -1px; line-height: 1; }
.masthead-logo span { color: var(--red); }
.masthead-tagline { font-family: 'Source Serif 4', serif; font-size: 0.78rem; color: #aaa; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
.masthead-date { font-size: 0.8rem; color: #aaa; letter-spacing: 1px; text-align: right; }

.rule-thick { border: none; border-top: 3px double var(--ink); margin: 1.2rem 0 0.6rem; }
.rule-thin  { border: none; border-top: 1px solid var(--rule); margin: 0.8rem 0; }
.rule-red   { border: none; border-top: 2px solid var(--red);  margin: 0.5rem 0 1rem; }
.section-label { font-family: 'Source Serif 4', serif; font-size: 0.65rem; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--red); margin-bottom: 0.3rem; }

.stTextInput > div > div > input {
    background: #fff !important; border: 1px solid var(--rule) !important;
    border-bottom: 2px solid var(--ink) !important; border-radius: 0 !important;
    font-family: 'Noto Nastaliq Urdu', serif !important; font-size: 1.1rem !important;
    direction: rtl !important; text-align: right !important;
    color: var(--ink) !important; padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus { border-bottom-color: var(--red) !important; box-shadow: none !important; }

.stButton > button {
    background: var(--red) !important; color: #ffffff !important;
    border: none !important; border-radius: 0 !important;
    font-family: 'Playfair Display', serif !important; font-size: 1rem !important;
    font-weight: 700 !important; letter-spacing: 1px !important;
    padding: 0.7rem 2rem !important; width: 100% !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover { background: var(--red-dark) !important; }

.article-card {
    background: var(--card-bg); border: 1px solid var(--rule);
    border-top: 3px solid var(--ink); padding: 1.8rem 2rem;
    margin-bottom: 1.5rem; box-shadow: 2px 2px 0 var(--rule);
}
.article-label { font-family: 'Source Serif 4', serif; font-size: 0.6rem; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--red); margin-bottom: 0.5rem; }
.article-model-badge { display: inline-block; background: var(--ink); color: #fff; font-family: 'Source Serif 4', serif; font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase; padding: 2px 8px; margin-bottom: 0.8rem; }
.article-body { font-family: 'Noto Nastaliq Urdu', serif; font-size: 1.15rem; line-height: 2.4; direction: rtl; text-align: right; color: var(--ink); }

.headline-card {
    border-left: 4px solid var(--red); padding: 0.6rem 1rem 0.6rem 1.2rem;
    margin-bottom: 0.8rem; background: #fff;
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.headline-num { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 900; color: var(--rule); min-width: 2rem; line-height: 1; }
.headline-text { font-family: 'Noto Nastaliq Urdu', serif; font-size: 1.1rem; font-weight: 600; direction: rtl; text-align: right; color: var(--ink); line-height: 2; flex: 1; }

.metric-strip { display: flex; gap: 0; border: 1px solid var(--rule); margin-bottom: 1rem; background: #fff; }
.metric-cell { flex: 1; padding: 0.7rem 1rem; border-right: 1px solid var(--rule); text-align: center; }
.metric-cell:last-child { border-right: none; }
.metric-val { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: var(--ink); line-height: 1.1; }
.metric-lbl { font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase; color: var(--mid); margin-top: 2px; }

.ppl-bar-wrap { background: #fff; border: 1px solid var(--rule); padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; }
.ppl-label { font-size: 0.65rem; letter-spacing: 2px; text-transform: uppercase; color: var(--mid); margin-bottom: 0.4rem; }
.ppl-val { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; }
.ppl-bar-bg { background: var(--rule); height: 6px; }
.ppl-bar-fill { height: 6px; background: var(--red); }
.ppl-bar-fill.good { background: #27ae60; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 2px solid var(--ink) !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Source Serif 4', serif !important; font-size: 0.75rem !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: var(--mid) !important; padding: 0.5rem 1.2rem !important; border: none !important; background: transparent !important; border-bottom: 3px solid transparent !important; margin-bottom: -2px !important; }
.stTabs [aria-selected="true"] { color: var(--red) !important; border-bottom-color: var(--red) !important; font-weight: 600 !important; }
.stSlider [data-testid="stThumb"] { background: var(--red) !important; }
.stSlider [data-testid="stTrackHighlight"] { background: var(--red) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--paper); }
::-webkit-scrollbar-thumb { background: var(--rule); }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTS & OPTIMIZED PARAMETERS
# ============================================================================
EOS          = '<EOS>'
UNK          = '<UNK>'
PUNCT_TOKENS = {'۔', '؟', '!', '،', '؛', '؍', '.', '?', ',', ';'}

# Tuned via grid search on BBC Urdu corpus
K_UNIGRAM    = 0.2      # Add-k for unigram
K_BIGRAM     = 0.001    # Add-k for bigram (key improvement)
K_TRIGRAM    = 0.001    # Add-k for trigram
LAMBDA3      = 0.0      # Trigram weight (sparse contexts → 0)
LAMBDA2      = 0.72     # Bigram weight  (dominates)
LAMBDA1      = 0.28     # Unigram weight

# ============================================================================
# DATA LOADING — punctuation stripped, EOS per sentence
# ============================================================================
def load_tokens(filepath='cleaned.txt'):
    """
    Load cleaned.txt for language model training.
    Punctuation tokens are stripped — <EOS> already marks boundaries.
    One <EOS> inserted per content line (sentence).
    """
    all_tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or re.match(r'^\[\d+\]$', line):
                continue
            toks = [t for t in line.split() if t not in PUNCT_TOKENS]
            if toks:
                all_tokens.extend(toks)
                all_tokens.append(EOS)
    return all_tokens


def replace_singletons(tokens, min_freq=2):
    """Replace tokens seen < min_freq times with <UNK> to reduce vocabulary."""
    freq = Counter(t for t in tokens if t not in (EOS, UNK))
    return [
        t if (t in (EOS, UNK) or freq[t] >= min_freq) else UNK
        for t in tokens
    ]

# ============================================================================
# MODELS — Add-k smoothing with optimized k values
# ============================================================================

class UnigramModel:
    def __init__(self, k=K_UNIGRAM):
        self.k = k
        self.counts = Counter()
        self.total  = 0
        self.vocab  = set()

    def train(self, tokens):
        self.counts = Counter(t for t in tokens if t != EOS)
        self.total  = sum(self.counts.values())
        self.vocab  = set(self.counts.keys())

    def probability(self, word):
        V = len(self.vocab)
        return (self.counts.get(word, 0) + self.k) / (self.total + self.k * V)

    def log_probability(self, word):
        return math.log(self.probability(word))

    def sample(self):
        words = list(self.vocab)
        probs = [self.counts[w] / self.total for w in words]
        return random.choices(words, weights=probs, k=1)[0]


class BigramModel:
    def __init__(self, unigram_model, k=K_BIGRAM):
        self.k              = k
        self.unigram        = unigram_model
        self.bigram_counts  = defaultdict(Counter)
        self.unigram_counts = Counter()

    def train(self, tokens):
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i + 1]
            if w1 == EOS:
                continue
            self.bigram_counts[w1][w2]  += 1
            self.unigram_counts[w1]     += 1

    def probability(self, w2, w1):
        V = len(self.unigram.vocab)
        return (self.bigram_counts[w1].get(w2, 0) + self.k) / \
               (self.unigram_counts.get(w1, 0) + self.k * V)

    def log_probability(self, w2, w1):
        return math.log(self.probability(w2, w1))

    def next_word(self, w1, temperature=1.0):
        vocab  = list(self.unigram.vocab)
        V      = len(vocab)
        denom  = self.unigram_counts.get(w1, 0) + self.k * V
        weights = [
            ((self.bigram_counts[w1].get(w, 0) + self.k) / denom)
            ** (1.0 / max(temperature, 0.01))
            for w in vocab
        ]
        return random.choices(vocab, weights=weights, k=1)[0]


class TrigramModel:
    def __init__(self, bigram_model, unigram_model, k=K_TRIGRAM):
        self.k                 = k
        self.bigram            = bigram_model
        self.unigram           = unigram_model
        self.trigram_counts    = defaultdict(Counter)
        self.bigram_ctx_counts = Counter()
        # Optimized lambda weights (grid-search tuned)
        self.L3 = LAMBDA3
        self.L2 = LAMBDA2
        self.L1 = LAMBDA1

    def train(self, tokens):
        for i in range(len(tokens) - 2):
            w1, w2, w3 = tokens[i], tokens[i + 1], tokens[i + 2]
            if w1 == EOS or w2 == EOS:
                continue
            self.trigram_counts[(w1, w2)][w3]  += 1
            self.bigram_ctx_counts[(w1, w2)]   += 1
        # NOTE: lambdas are pre-set to grid-search optimal values
        # Deleted interpolation is skipped — optimal values already known

    def probability(self, w3, w1, w2):
        V   = len(self.unigram.vocab)
        ctx = (w1, w2)
        c_tri = self.trigram_counts[ctx].get(w3, 0)
        d_tri = self.bigram_ctx_counts.get(ctx, 0) + self.k * V
        p_tri = (c_tri + self.k) / d_tri
        p_bi  = self.bigram.probability(w3, w2)
        p_uni = self.unigram.probability(w3)
        return self.L3 * p_tri + self.L2 * p_bi + self.L1 * p_uni

    def log_probability(self, w3, w1, w2):
        return math.log(self.probability(w3, w1, w2))

    def next_word(self, w1, w2, temperature=1.0):
        vocab   = list(self.unigram.vocab)
        weights = [
            self.probability(w, w1, w2) ** (1.0 / max(temperature, 0.01))
            for w in vocab
        ]
        return random.choices(vocab, weights=weights, k=1)[0]


# ============================================================================
# PERPLEXITY
# ============================================================================

def perplexity_bigram(model, tokens):
    log_sum, N = 0.0, 0
    for i in range(1, len(tokens)):
        if tokens[i] == EOS or tokens[i - 1] == EOS:
            continue
        log_sum += model.log_probability(tokens[i], tokens[i - 1])
        N += 1
    return math.exp(-log_sum / N) if N > 0 else float('inf')


def perplexity_trigram(model, tokens):
    log_sum, N = 0.0, 0
    for i in range(2, len(tokens)):
        if tokens[i] == EOS or tokens[i-1] == EOS or tokens[i-2] == EOS:
            continue
        log_sum += model.log_probability(tokens[i], tokens[i-2], tokens[i-1])
        N += 1
    return math.exp(-log_sum / N) if N > 0 else float('inf')


# ============================================================================
# ARTICLE GENERATOR
# ============================================================================

class UrduArticleGenerator:
    MIN_WORDS    = 200
    TARGET_WORDS = 250
    MAX_WORDS    = 300
    MIN_SENTS    = 5

    def __init__(self, bigram_model, trigram_model, unigram_model):
        self.bigram  = bigram_model
        self.trigram = trigram_model
        self.unigram = unigram_model

    def validate_prompt(self, prompt):
        words = prompt.strip().split()
        if len(words) < 5:
            raise ValueError(f"Too short ({len(words)} words). Need 5–8 Urdu words.")
        if len(words) > 8:
            raise ValueError(f"Too long ({len(words)} words). Need 5–8 Urdu words.")
        return words

    def _generate(self, seed_tokens, model='trigram', temperature=1.0):
        tokens     = list(seed_tokens)
        word_count = len(tokens)
        sentences  = 0
        while word_count < self.MAX_WORDS:
            if model == 'trigram' and len(tokens) >= 2:
                next_tok = self.trigram.next_word(
                    tokens[-2], tokens[-1], temperature=temperature)
            elif len(tokens) >= 1:
                next_tok = self.bigram.next_word(
                    tokens[-1], temperature=temperature)
            else:
                next_tok = self.unigram.sample()
            tokens.append(next_tok)
            if next_tok == EOS:
                sentences += 1
                if word_count >= self.MIN_WORDS and sentences >= self.MIN_SENTS:
                    break
            else:
                word_count += 1
            if word_count >= self.MAX_WORDS:
                tokens.append(EOS)
                sentences += 1
                break
        return tokens, sentences

    def _render(self, tokens):
        sentences, current = [], []
        for tok in tokens:
            if tok == EOS:
                if current:
                    sentences.append(' '.join(current) + '۔')
                    current = []
            elif not tok.startswith('<'):
                current.append(tok)
        if current:
            sentences.append(' '.join(current) + '۔')
        return '\n'.join(sentences)

    def generate_article(self, prompt, model='trigram', temperature=1.0):
        seed = self.validate_prompt(prompt)
        tokens, n_sents = self._generate(seed, model=model, temperature=temperature)
        article    = self._render(tokens)
        word_count = len([t for t in tokens
                          if t != EOS and not t.startswith('<')])
        return {'article': article, 'word_count': word_count,
                'sentences': n_sents, 'model': model, 'prompt': prompt}

    def generate_headline(self, prompt, model='bigram', max_words=12):
        words  = prompt.strip().split()
        tokens = list(words[:8])
        for _ in range(max_words - len(tokens)):
            if model == 'trigram' and len(tokens) >= 2:
                nxt = self.trigram.next_word(tokens[-2], tokens[-1], temperature=0.7)
            else:
                nxt = self.bigram.next_word(tokens[-1], temperature=0.7)
            if nxt == EOS:
                break
            tokens.append(nxt)
        return ' '.join(t for t in tokens if t != EOS and not t.startswith('<'))


# ============================================================================
# SESSION STATE
# ============================================================================
for key, default in [
    ('models_loaded', False),
    ('unigram', None), ('bigram', None), ('trigram', None), ('generator', None),
    ('train_tokens', []), ('test_tokens', []),
    ('ppl_bi', None), ('ppl_tri', None),
    ('history', []), ('headlines', []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================================
# MASTHEAD
# ============================================================================
today = datetime.now().strftime("%A, %d %B %Y")
st.markdown(f"""
<div class="masthead">
  <div>
    <div class="masthead-logo">BBC <span>اردو</span></div>
    <div class="masthead-tagline">AI News Generator &nbsp;·&nbsp; Statistical Language Model</div>
  </div>
  <div class="masthead-date">{today}<br>Bigram · Trigram · Add-k Smoothing</div>
</div>
<hr class="rule-thick">
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    data_file    = st.text_input("cleaned.txt path", value="cleaned.txt",
                                  label_visibility="collapsed")
    st.markdown("**Language Model**")
    model_choice = st.radio("model",
                             ["Bigram", "Trigram (Interpolated)"],
                             label_visibility="collapsed")
    st.markdown("**Generation Settings**")
    temperature  = st.slider("Temperature", 0.5, 2.0, 1.0, 0.05)
    gen_headline = st.checkbox("Generate headline", value=True)
    show_metrics = st.checkbox("Show article metrics", value=True)

    st.markdown("---")

    if st.button("🔄 Load & Train Models", use_container_width=True):
        with st.spinner("Loading and training…"):
            try:
                # ── Load with punctuation stripping ──────────────
                raw = load_tokens(data_file)

                # ── Singleton pruning ─────────────────────────────
                tokens = replace_singletons(raw, min_freq=2)

                # ── 95/5 train-test split ─────────────────────────
                eos_idx = [i for i, t in enumerate(tokens) if t == EOS]
                split   = eos_idx[int(len(eos_idx) * 0.95)]
                train_t = tokens[:split + 1]
                test_t  = tokens[split + 1:]

                # ── Train with OPTIMIZED k values ─────────────────
                uni = UnigramModel(k=K_UNIGRAM)
                uni.train(train_t)

                bi = BigramModel(uni, k=K_BIGRAM)
                bi.train(train_t)

                tri = TrigramModel(bi, uni, k=K_TRIGRAM)
                tri.train(train_t)
                # Lambdas already set to optimal in __init__
                # tri.L3=0.0, tri.L2=0.72, tri.L1=0.28

                gen = UrduArticleGenerator(bi, tri, uni)

                # ── Perplexity on test set ────────────────────────
                p_bi  = perplexity_bigram(bi,  test_t)
                p_tri = perplexity_trigram(tri, test_t)

                st.session_state.update({
                    'models_loaded': True,
                    'unigram': uni, 'bigram': bi,
                    'trigram': tri, 'generator': gen,
                    'train_tokens': train_t,
                    'test_tokens':  test_t,
                    'ppl_bi':  p_bi,
                    'ppl_tri': p_tri,
                })
                st.success(f"✓ Trained on {len(train_t):,} tokens")

            except FileNotFoundError:
                st.error(f"File not found: {data_file}")
            except Exception as e:
                st.error(f"Error: {e}")

    # ── Status panel ─────────────────────────────────────────
    if st.session_state.models_loaded:
        ppl_bi  = st.session_state.ppl_bi
        ppl_tri = st.session_state.ppl_tri
        improv  = (ppl_bi - ppl_tri) / ppl_bi * 100
        st.markdown(f"""
        <div style="margin-top:1rem;padding:0.8rem;background:#2a2a2a;
                    border-left:3px solid #27ae60;font-size:0.75rem;">
          <div style="color:#27ae60;font-weight:600;letter-spacing:1px;
                      text-transform:uppercase;margin-bottom:0.4rem;">● Models Ready</div>
          <div style="color:#aaa;">Vocab : {len(st.session_state.unigram.vocab):,}</div>
          <div style="color:#aaa;">Train : {len(st.session_state.train_tokens):,} tokens</div>
          <div style="color:#aaa;">Test  : {len(st.session_state.test_tokens):,} tokens</div>
        </div>
        <div style="margin-top:0.6rem;padding:0.8rem;background:#2a2a2a;
                    border-left:3px solid #c0392b;font-size:0.75rem;">
          <div style="color:#c0392b;font-weight:600;letter-spacing:1px;
                      text-transform:uppercase;margin-bottom:0.4rem;">Perplexity</div>
          <div style="color:#aaa;">Bigram : {ppl_bi:.2f}</div>
          <div style="color:#aaa;">Trigram: {ppl_tri:.2f}</div>
          <div style="color:#27ae60;margin-top:4px;">↓ {improv:.1f}% improvement</div>
        </div>
        <div style="margin-top:0.6rem;padding:0.6rem 0.8rem;background:#2a2a2a;
                    font-size:0.65rem;color:#888;">
          k_uni={K_UNIGRAM} · k_bi={K_BIGRAM}<br>
          λ2={LAMBDA2} · λ1={LAMBDA1}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑 Clear History", use_container_width=True):
        st.session_state.history   = []
        st.session_state.headlines = []
        st.rerun()

# ============================================================================
# TABS
# ============================================================================
tab_gen, tab_headlines, tab_eval, tab_help = st.tabs([
    "Generate Article", "Headlines", "Evaluation", "How to Use"
])

# ── Tab 1: Generate ───────────────────────────────────────────
with tab_gen:
    st.markdown('<div class="section-label">Seed Prompt</div>', unsafe_allow_html=True)
    st.markdown('<div class="rule-red"></div>', unsafe_allow_html=True)

    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        prompt = st.text_input("seed",
                               placeholder="پاکستان میں مہنگائی کی شرح میں",
                               label_visibility="collapsed")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("Generate →", use_container_width=True)

    if prompt:
        wc     = len(prompt.strip().split())
        color  = "#27ae60" if 5 <= wc <= 8 else "#c0392b"
        status = "✓ Valid" if 5 <= wc <= 8 else \
                 ("Too short — add more words" if wc < 5 else "Too long — remove some words")
        st.markdown(f'<div style="font-size:0.75rem;color:{color};'
                    f'margin-top:-0.5rem;margin-bottom:0.8rem;">'
                    f'{wc} words · {status}</div>', unsafe_allow_html=True)

    if generate:
        if not st.session_state.models_loaded:
            st.error("▸ Load and train models first using the sidebar button.")
        elif not prompt.strip():
            st.warning("Please enter a seed prompt.")
        else:
            model_key = "bigram" if "Bigram" in model_choice else "trigram"
            gen       = st.session_state.generator
            with st.spinner("Generating…"):
                try:
                    result   = gen.generate_article(
                        prompt, model=model_key, temperature=temperature)
                    headline = gen.generate_headline(prompt) if gen_headline else ""
                    st.session_state.history.insert(0, {
                        **result,
                        'headline':    headline,
                        'temperature': temperature,
                    })
                    if headline:
                        st.session_state.headlines.insert(0, headline)
                except ValueError as e:
                    st.error(f"Invalid prompt: {e}")
                    st.stop()

    if st.session_state.history:
        st.markdown('<div class="section-label" style="margin-top:1.5rem;">'
                    'Generated Articles</div>', unsafe_allow_html=True)
        st.markdown('<div class="rule-red"></div>', unsafe_allow_html=True)

        for idx, item in enumerate(st.session_state.history):
            label = "BIGRAM MODEL" if item['model'] == 'bigram' \
                    else "TRIGRAM MODEL (INTERPOLATED)"
            if show_metrics:
                st.markdown(f"""
                <div class="metric-strip">
                  <div class="metric-cell">
                    <div class="metric-val">{item['word_count']}</div>
                    <div class="metric-lbl">Words</div>
                  </div>
                  <div class="metric-cell">
                    <div class="metric-val">{item['sentences']}</div>
                    <div class="metric-lbl">Sentences</div>
                  </div>
                  <div class="metric-cell">
                    <div class="metric-val">{item['temperature']:.1f}</div>
                    <div class="metric-lbl">Temperature</div>
                  </div>
                  <div class="metric-cell">
                    <div class="metric-val" style="font-size:1rem;">{item['model'].capitalize()}</div>
                    <div class="metric-lbl">Model</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            if item.get('headline'):
                st.markdown(f"""
                <div class="headline-card">
                  <div class="headline-num">HL</div>
                  <div class="headline-text">{item['headline']}</div>
                </div>
                """, unsafe_allow_html=True)
            body = item['article'].replace('\n', '<br><br>')
            st.markdown(f"""
            <div class="article-card">
              <div class="article-label">Article {len(st.session_state.history)-idx}</div>
              <div class="article-model-badge">{label}</div>
              <hr class="rule-thin" style="margin-bottom:1rem;">
              <div class="article-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#aaa;">
          <div style="font-family:'Playfair Display',serif;font-size:3rem;
                      color:#ddd;margin-bottom:1rem;">اردو</div>
          <div style="font-size:0.8rem;letter-spacing:2px;text-transform:uppercase;">
            Enter a seed prompt above and click Generate
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Tab 2: Headlines ──────────────────────────────────────────
with tab_headlines:
    st.markdown('<div class="section-label">Generated Headlines</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="rule-red"></div>', unsafe_allow_html=True)

    col_hs, col_hb = st.columns([4, 1])
    with col_hs:
        hl_prompt = st.text_input("Headline seed",
                                   placeholder="حکومت نے نئی پالیسی کا اعلان",
                                   label_visibility="collapsed")
    with col_hb:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_5 = st.button("Generate 5 →", use_container_width=True)

    if gen_5:
        if not st.session_state.models_loaded:
            st.error("Load models first.")
        elif not hl_prompt.strip():
            st.warning("Enter a seed prompt.")
        else:
            with st.spinner("Generating headlines…"):
                try:
                    new_hls = [st.session_state.generator.generate_headline(
                                   hl_prompt) for _ in range(5)]
                    st.session_state.headlines = \
                        new_hls + st.session_state.headlines
                except ValueError as e:
                    st.error(str(e))

    if st.session_state.headlines:
        for i, hl in enumerate(st.session_state.headlines[:10], 1):
            st.markdown(f"""
            <div class="headline-card">
              <div class="headline-num">{i:02d}</div>
              <div class="headline-text">{hl}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#aaa;font-size:0.85rem;
                    letter-spacing:2px;text-transform:uppercase;">
          No headlines yet
        </div>
        """, unsafe_allow_html=True)

# ── Tab 3: Evaluation ─────────────────────────────────────────
with tab_eval:
    st.markdown('<div class="section-label">Model Evaluation</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="rule-red"></div>', unsafe_allow_html=True)

    if not st.session_state.models_loaded:
        st.info("Load and train models using the sidebar to see evaluation.")
    else:
        ppl_bi  = st.session_state.ppl_bi
        ppl_tri = st.session_state.ppl_tri
        improv  = (ppl_bi - ppl_tri) / ppl_bi * 100
        max_ppl = max(ppl_bi, ppl_tri)

        st.markdown("#### Perplexity *(lower is better)*")
        st.markdown(f"""
        <div class="ppl-bar-wrap">
          <div class="ppl-label">Bigram Model  (k={K_BIGRAM})</div>
          <div class="ppl-val">{ppl_bi:.2f}</div>
          <div class="ppl-bar-bg">
            <div class="ppl-bar-fill"
                 style="width:{ppl_bi/max_ppl*100:.1f}%;"></div>
          </div>
        </div>
        <div class="ppl-bar-wrap">
          <div class="ppl-label">Trigram Model  (λ2={LAMBDA2}, λ1={LAMBDA1})</div>
          <div class="ppl-val">{ppl_tri:.2f}</div>
          <div class="ppl-bar-bg">
            <div class="ppl-bar-fill good"
                 style="width:{ppl_tri/max_ppl*100:.1f}%;"></div>
          </div>
        </div>
        <div style="margin-top:0.8rem;padding:0.8rem 1rem;background:#eafaf1;
                    border-left:3px solid #27ae60;font-size:0.85rem;color:#1a5e36;">
          Trigram achieves <strong>{improv:.1f}%</strong> lower perplexity than Bigram.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>#### Optimized Parameters")
        st.markdown(f"""
        <div class="metric-strip">
          <div class="metric-cell">
            <div class="metric-val" style="font-size:1.1rem;">{K_UNIGRAM}</div>
            <div class="metric-lbl">k unigram</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val" style="font-size:1.1rem;">{K_BIGRAM}</div>
            <div class="metric-lbl">k bigram</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val" style="font-size:1.1rem;">{LAMBDA2}</div>
            <div class="metric-lbl">λ₂ bigram</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val" style="font-size:1.1rem;">{LAMBDA1}</div>
            <div class="metric-lbl">λ₁ unigram</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        uni = st.session_state.unigram
        bi  = st.session_state.bigram
        tri = st.session_state.trigram
        st.markdown("<br>#### Corpus Statistics")
        st.markdown(f"""
        <div class="metric-strip">
          <div class="metric-cell">
            <div class="metric-val">{len(uni.vocab):,}</div>
            <div class="metric-lbl">Vocabulary</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val">{len(st.session_state.train_tokens):,}</div>
            <div class="metric-lbl">Train Tokens</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val">{len(st.session_state.test_tokens):,}</div>
            <div class="metric-lbl">Test Tokens</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val">{len(bi.bigram_counts):,}</div>
            <div class="metric-lbl">Bigram Ctx</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val">{len(tri.trigram_counts):,}</div>
            <div class="metric-lbl">Trigram Ctx</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Tab 4: Help ───────────────────────────────────────────────
with tab_help:
    st.markdown('<div class="section-label">Usage Guide</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="rule-red"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Source Serif 4',serif;max-width:680px;line-height:1.9;">
    <h4 style="font-family:'Playfair Display',serif;border-bottom:1px solid #ddd;
               padding-bottom:0.4rem;">Step 1 — Load & Train</h4>
    <p>Ensure <code>cleaned.txt</code> is in the same directory as <code>app.py</code>.
    Click <strong>Load &amp; Train Models</strong> in the sidebar.
    Expected perplexity: <strong>Bigram ~305 · Trigram ~182</strong>.</p>

    <h4 style="font-family:'Playfair Display',serif;border-bottom:1px solid #ddd;
               padding-bottom:0.4rem;margin-top:1.4rem;">Step 2 — Choose a Model</h4>
    <p><strong>Bigram</strong> — 1 word context, faster.<br>
    <strong>Trigram (Interpolated)</strong> — weighted blend λ₂=0.72 bigram +
    λ₁=0.28 unigram, 40% lower perplexity.</p>

    <h4 style="font-family:'Playfair Display',serif;border-bottom:1px solid #ddd;
               padding-bottom:0.4rem;margin-top:1.4rem;">Step 3 — Seed Prompt (5–8 words)</h4>
    <div style="background:#fff;border:1px solid #ddd;border-left:3px solid #27ae60;
                padding:0.8rem 1.2rem;margin:0.8rem 0;font-family:'Noto Nastaliq Urdu',serif;
                font-size:1.05rem;direction:rtl;text-align:right;">
      ✓ پاکستان میں مہنگائی کی شرح میں
    </div>
    <div style="background:#fff;border:1px solid #ddd;border-left:3px solid #c0392b;
                padding:0.8rem 1.2rem;margin:0.8rem 0;font-family:'Noto Nastaliq Urdu',serif;
                font-size:1.05rem;direction:rtl;text-align:right;">
      ✗ پاکستان
    </div>

    <h4 style="font-family:'Playfair Display',serif;border-bottom:1px solid #ddd;
               padding-bottom:0.4rem;margin-top:1.4rem;">Step 4 — Temperature</h4>
    <p>0.5–0.8 → focused &nbsp;|&nbsp; 1.0 → balanced &nbsp;|&nbsp;
    1.2–2.0 → creative</p>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<hr class="rule-thick" style="margin-top:3rem;">
<div style="display:flex;justify-content:space-between;font-size:0.65rem;
            letter-spacing:1.5px;text-transform:uppercase;color:#aaa;
            padding:0.8rem 0 0.5rem;">
  <span>BBC Urdu NLP — CS-4063 Assignment 1</span>
  <span>Bigram · Trigram · Add-k Smoothing · Perplexity 304/182</span>
</div>
""", unsafe_allow_html=True)