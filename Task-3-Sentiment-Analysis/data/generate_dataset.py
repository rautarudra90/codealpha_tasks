"""
generate_dataset.py
--------------------
Generates a realistic, synthetic multi-source text dataset (Amazon-style
product reviews, social media posts, and news headlines) for sentiment
analysis. Text is built from curated positive / negative / neutral
templates combined with randomized products/topics so the language is
varied and realistic, while a ground-truth label is retained for accuracy
evaluation.

Run directly to regenerate data/sample_reviews.csv:
    python data/generate_dataset.py
"""

import os
import numpy as np
import pandas as pd

POSITIVE_TEMPLATES = [
    "Absolutely love this {item}, it exceeded all my expectations!",
    "This {item} is fantastic, best purchase I've made all year.",
    "I'm so happy with the {item}, works perfectly and looks great.",
    "Highly recommend the {item} to anyone looking for quality.",
    "The {item} arrived quickly and the build quality is amazing.",
    "Five stars for the {item}, it changed the way I do things.",
    "What a wonderful {item}! Great value for the price.",
    "The customer service team was super helpful with my {item} order.",
    "This {item} is a game changer, I use it every single day.",
    "Excellent {item}, exactly as described and super reliable.",
    "I'm impressed by how well the {item} performs, truly outstanding.",
    "Great {item}! My whole family loves it.",
]

NEGATIVE_TEMPLATES = [
    "Terrible {item}, broke after just two days of use.",
    "I'm so disappointed with this {item}, complete waste of money.",
    "The {item} stopped working and support was unhelpful.",
    "Awful experience with the {item}, would not recommend at all.",
    "This {item} is poorly made and feels cheap.",
    "Very frustrated with the {item}, it never worked as advertised.",
    "The {item} arrived damaged and customer service ignored me.",
    "Worst {item} I have ever bought, total regret.",
    "The {item} is overpriced for such low quality.",
    "I hate how unreliable this {item} turned out to be.",
    "Disappointing {item}, definitely returning it.",
    "This {item} caused nothing but problems since day one.",
]

NEUTRAL_TEMPLATES = [
    "The {item} arrived on time and matches the description.",
    "I bought the {item} last week, still testing it out.",
    "The {item} does what it's supposed to do, nothing special.",
    "Received the {item} today, packaging was standard.",
    "The {item} is okay, not great but not bad either.",
    "Here is my honest review of the {item} after a week of use.",
    "The {item} has some pros and cons worth mentioning.",
    "Considering whether to keep the {item} or exchange it.",
    "The {item} works as expected, average performance overall.",
    "Just unboxed the {item}, will update this review later.",
    "The {item} meets the basic requirements, nothing more.",
    "Comparing the {item} to similar products on the market now.",
]

ITEMS = [
    "wireless headphones", "laptop stand", "coffee maker", "running shoes",
    "smartphone case", "fitness tracker", "backpack", "desk lamp",
    "bluetooth speaker", "kitchen blender", "office chair", "water bottle",
    "gaming mouse", "yoga mat", "air purifier", "electric toothbrush",
    "streaming service", "mobile app", "airline", "restaurant chain",
    "customer support experience", "software update", "delivery service",
    "subscription plan",
]

SOURCES = ["Amazon Review", "Twitter/X Post", "News Headline", "Facebook Comment", "Product Forum"]


def generate_dataset(n_rows: int = 3000, seed: int = 7) -> pd.DataFrame:
    """Generate a synthetic multi-source sentiment dataset.

    Args:
        n_rows (int): Number of text samples to generate.
        seed (int): Random seed for reproducibility.

    Returns:
        pd.DataFrame: Generated dataset with columns:
            text, source, true_sentiment, item, review_date
    """
    rng = np.random.default_rng(seed)
    rows = []

    sentiment_pool = (
        [("positive", t) for t in POSITIVE_TEMPLATES] +
        [("negative", t) for t in NEGATIVE_TEMPLATES] +
        [("neutral", t) for t in NEUTRAL_TEMPLATES]
    )

    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")

    for _ in range(n_rows):
        sentiment, template = sentiment_pool[rng.integers(0, len(sentiment_pool))]
        item = ITEMS[rng.integers(0, len(ITEMS))]
        text = template.format(item=item)

        # Add small variety / noise: random emoji or punctuation emphasis.
        if sentiment == "positive" and rng.random() < 0.3:
            text += rng.choice([" :)", " 😊", "!!", " Love it!"])
        elif sentiment == "negative" and rng.random() < 0.3:
            text += rng.choice([" :(", " 😡", "!!", " Never again."])

        source = SOURCES[rng.integers(0, len(SOURCES))]
        date = rng.choice(dates)

        rows.append({
            "text": text,
            "source": source,
            "item": item,
            "true_sentiment": sentiment,
            "review_date": date,
        })

    df = pd.DataFrame(rows)

    # Inject minor data-quality issues: a few empty/whitespace-only texts,
    # a couple of duplicate rows, and one missing source value.
    idx_empty = rng.choice(df.index, size=5, replace=False)
    df.loc[idx_empty, "text"] = "   "

    dup_rows = df.sample(n=10, random_state=seed)
    df = pd.concat([df, dup_rows], ignore_index=True)

    idx_missing_source = rng.choice(df.index, size=3, replace=False)
    df.loc[idx_missing_source, "source"] = np.nan

    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    df.insert(0, "review_id", [f"REV{100000+i}" for i in range(len(df))])

    return df


def main():
    df = generate_dataset()
    out_path = os.path.join(os.path.dirname(__file__), "sample_reviews.csv")
    df.to_csv(out_path, index=False)
    print(f"Dataset generated: {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
