# Sentiment Analysis Project

A complete, production-grade NLP pipeline for classifying text sentiment
(positive / negative / neutral) and detecting discrete emotions, built on a
realistic multi-source dataset (Amazon-style reviews, social media posts,
news headlines, and forum comments).

---

## 📁 Project Structure

```
sentiment_analysis_project/
├── data/
│   ├── generate_dataset.py     # Synthetic multi-source text generator
│   └── sample_reviews.csv      # Pre-generated 3,000+ row text dataset
├── src/
│   ├── __init__.py
│   ├── logger_config.py        # Centralized rotating-file + console logging
│   ├── data_loader.py          # Loading + validation of the text dataset
│   ├── preprocessor.py         # Text cleaning & normalization
│   ├── sentiment_analyzer.py   # VADER + TextBlob ensemble sentiment classifier
│   ├── emotion_detector.py     # Lexicon-based emotion detection (6 emotions)
│   ├── visualizer.py           # Sentiment/emotion chart generation
│   └── report_generator.py     # Compiles a single Markdown analysis report
├── logs/                        # Rotating log files (auto-created)
├── output/                      # Generated report, charts, results CSV
├── screenshots/                 # Sample pre-generated output images
├── main.py                      # Orchestrates the full pipeline
├── requirements.txt
├── run.bat                      # One-click Windows setup + run
├── .gitignore
├── LICENSE
└── README.md
```

## 🧠 What This Project Does

1. **Loads** a multi-source dataset of Amazon-style reviews, tweets, news
   headlines, Facebook comments, and forum posts.
2. **Cleans** raw text — strips URLs, @mentions, hashtags, and noise;
   removes empty and duplicate entries.
3. **Classifies sentiment** using an **ensemble of VADER and TextBlob** —
   VADER is tuned for informal/social text (handles emojis and punctuation
   emphasis), while TextBlob provides a general-purpose polarity score. The
   two are combined with weighted averaging for a more robust final label.
4. **Detects specific emotions** — joy, anger, sadness, fear, trust, and
   surprise — using an embedded, curated lexicon (no external downloads
   required, fully offline).
5. **Evaluates accuracy** against the dataset's ground-truth sentiment
   labels using precision, recall, and F1-score (via scikit-learn).
6. **Visualizes results**: sentiment distribution, sentiment composition by
   source, emotion breakdown, sentiment trend over time, and top keywords
   in negative feedback (a direct source of "what's going wrong" insight).
7. **Reports** everything in a single, decision-oriented Markdown file with
   business recommendations.

## 🏗️ Architecture

Clean, modular **object-oriented design**:

| Class | Responsibility |
|---|---|
| `DataLoader` | Loads and validates the CSV, raises `DataLoadError` on failure |
| `TextPreprocessor` | Cleans text, strips noise, removes empty/duplicate rows |
| `SentimentAnalyzer` | Runs the VADER + TextBlob ensemble and scores accuracy |
| `EmotionDetector` | Scans text against an embedded emotion lexicon |
| `SentimentVisualizer` | Generates and saves all charts |
| `ReportGenerator` | Assembles findings into one Markdown report |
| `SentimentPipeline` (in `main.py`) | Coordinates every step end-to-end |

## ⚙️ Installation & Setup

### Requirements
- Python 3.9+

### Steps

```bash
# 1. Extract the ZIP file
cd sentiment_analysis_project

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python main.py
```

### Windows Quick Start
Double-click **`run.bat`** — it installs dependencies and runs the pipeline
automatically.

> **Note:** This project uses VADER and TextBlob's built-in pattern-based
> analyzer, **not** NLTK's corpora-based analyzer — so no additional corpus
> downloads are required. Everything works fully offline after
> `pip install -r requirements.txt`.

## ▶️ What Happens When You Run It

```
✅ Sentiment analysis pipeline completed successfully.
📊 Records analyzed: 1243
🎯 Accuracy vs ground truth: 78.36%
📄 Report: output/sentiment_report.md
🖼️  Charts (5): output/*.png
💾 Full results CSV: output/processed_results.csv
📝 Logs: logs/sentiment_project.log
```

(Note: exact record counts/accuracy will match what you see when you run it,
since duplicate/near-identical synthetic template combinations are removed
during preprocessing.)

## 📊 Sample Outputs

Pre-generated sample charts are included in `screenshots/`:
- `sentiment_distribution.png`
- `sentiment_by_source.png`
- `emotion_breakdown.png`
- `sentiment_trend.png`
- `negative_keyword_frequency.png`

The full narrative report is generated at `output/sentiment_report.md`, and
the complete row-level results (sentiment scores + emotion counts per text)
are saved to `output/processed_results.csv`.

## 📦 Dataset

The dataset (`data/sample_reviews.csv`) is synthetically generated from
curated positive/negative/neutral templates combined with 24 product/topic
subjects and 5 text sources, producing 3,000+ varied text samples with a
retained ground-truth `true_sentiment` label for accuracy evaluation. No
internet connection or manual download is required. Regenerate a fresh copy
with:

```bash
python data/generate_dataset.py
```

To analyze your **own** text data instead, replace `data/sample_reviews.csv`
with any CSV containing a `text` column (a `true_sentiment` column is
optional, and only used for accuracy scoring if present).

## 🛡️ Error Handling & Logging

- `DataLoader` raises a clear `DataLoadError` if the file is missing, empty,
  or missing the required `text` column.
- `main.py` automatically regenerates the dataset if it's missing rather
  than crashing.
- All pipeline steps are logged to `logs/sentiment_project.log` (rotating,
  max 2 MB, 5 backups) as well as the console.
- Empty, whitespace-only, and duplicate text entries are automatically
  filtered out during preprocessing rather than crashing the pipeline.

## 🧩 Extending This Project

- Add new emotions or expand the lexicon in `src/emotion_detector.py`
  (`EMOTION_LEXICON` dictionary).
- Swap in a transformer-based model (e.g. Hugging Face) by adding a new
  method to `SentimentAnalyzer` — the rest of the pipeline stays unchanged.
- Point `DATA_PATH` in `main.py` at real Amazon/Twitter/news export data
  (same `text` column schema) to analyze real-world text.

## 📄 License

Released under the MIT License — see `LICENSE` for details.
