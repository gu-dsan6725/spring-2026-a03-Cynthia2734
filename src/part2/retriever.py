import logging
from pathlib import Path
import re
import pandas as pd

logger = logging.getLogger(__name__)

_DEFAULT_CSV = "../data/structured/daily_sales.csv"
_DEFAULT_TEXT_DIR = "../data/unstructured"


def _extract_rating(content: str) -> float:
    m = re.search(r"(\d+\.?\d*)\s*/\s*5", content)
    return float(m.group(1)) if m else 0.0


def _extract_product_name(content: str) -> str:
    m = re.search(r"^Product:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().lower() if m else ""


def retrieve_from_csv(
    question: str,
    csv_path: str = _DEFAULT_CSV,
    all_products: bool = True,
) -> str:
    """
    Retrieve relevant data from the sales CSV based on the question.

    Args:
        question: The user's natural language question.
        csv_path: Path to the daily_sales.csv file.

    Returns:
        Formatted string with relevant sales statistics.
    """
    logger.info("Retrieving from CSV...")
    q = question.lower()
    df = pd.read_csv(csv_path, parse_dates=["date"])

    parts: list[str] = []

    parts.append("=== Sales Data Overview ===")
    parts.append(f"Total records: {len(df)}")
    parts.append(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    parts.append(f"Total revenue (all time): ${df['total_revenue'].sum():,.2f}")
    parts.append(f"Total units sold (all time): {df['units_sold'].sum():,}")

    parts.append("\n=== Revenue by Category ===")
    cat_rev = df.groupby("category")["total_revenue"].sum().sort_values(ascending=False)
    parts.append(cat_rev.to_string())

    parts.append("\n=== Sales Volume (Units) by Region ===")
    reg_units = df.groupby("region")["units_sold"].sum().sort_values(ascending=False)
    parts.append(reg_units.to_string())

    parts.append("\n=== Revenue by Region ===")
    reg_rev = df.groupby("region")["total_revenue"].sum().sort_values(ascending=False)
    parts.append(reg_rev.to_string())

    if any(m in q for m in ["october", "oct"]):
        parts.append("\n=== October 2024 Revenue by Category ===")
        oct_df = df[df["date"].dt.month == 10]
        parts.append(
            oct_df.groupby("category")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
            .to_string()
        )

    if any(m in q for m in ["november", "nov"]):
        parts.append("\n=== November 2024 Revenue by Category ===")
        nov_df = df[df["date"].dt.month == 11]
        parts.append(
            nov_df.groupby("category")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
            .to_string()
        )

    if any(m in q for m in ["december", "dec"]):
        parts.append("\n=== December 2024 Revenue by Category ===")
        dec = df[df["date"].dt.month == 12]
        parts.append(
            dec.groupby("category")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
            .to_string()
        )

    if all_products:
        parts.append("\n=== All Products: Units Sold + Revenue ===")
        all_prod = (
            df.groupby("product_name")[["units_sold", "total_revenue"]]
            .sum()
            .sort_values("units_sold", ascending=False)
        )
        parts.append(all_prod.to_string())
    else:
        parts.append("\n=== Top 10 Products by Units Sold ===")
        top_products = (
            df.groupby("product_name")["units_sold"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        parts.append(top_products.to_string())

    if "west" in q:
        parts.append("\n=== West Region - Top Products by Units Sold ===")
        west = df[df["region"] == "West"]
        parts.append(
            west.groupby("product_name")["units_sold"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .to_string()
        )

    if any(kw in q for kw in ["fitness", "sport", "exercise"]):
        parts.append("\n=== Sports Category Sales ===")
        sports = df[df["category"].str.lower().str.contains("sport")]
        if len(sports) > 0:
            parts.append(
                sports.groupby("product_name")[["units_sold", "total_revenue"]]
                .sum()
                .sort_values("units_sold", ascending=False)
                .to_string()
            )

    context: str = "\n".join(parts)
    logger.info(f"CSV context length: {len(context)} chars")
    return context


def retrieve_from_text(
    question: str,
    text_dir: str = _DEFAULT_TEXT_DIR,
    max_chars: int = 6000,
) -> str:
    """
    Retrieve relevant content from product text files.

    Args:
        question:  The user's natural language question.
        text_dir:  Directory containing *_product_page.txt files.
        max_chars: Maximum characters to return.

    Returns:
        Concatenated content from the most relevant product files.
    """
    logger.info("Retrieving from text files...")
    q = question.lower()
    q_words: set[str] = set(q.split())

    scored: list[tuple[float, Path, str]] = []
    for txt_file in sorted(Path(text_dir).glob("*.txt")):
        content: str = txt_file.read_text(encoding="utf-8")
        content_words: set[str] = set(content.lower().split())

        score: float = float(len(q_words & content_words))
        
        prod_name = _extract_product_name(content)
        if prod_name:
            name_words = set(prod_name.split())
            score += len(name_words & q_words) * 50
            
        sku_m = re.search(r"\b[A-Z]{3,5}\d{3}\b", content)
        if sku_m and sku_m.group(0).lower() in q:
            score += 30

        scored.append((score, txt_file, content))

    scored.sort(key=lambda x: x[0], reverse=True)

    parts: list[str] = []
    total_chars = 0
    
    rating_trigger = any(
        kw in q
        for kw in [
            "best",
            "highest rated",
            "most reviewed",
            "top rated",
            "best review",
            "best customer",
            "highly rated",
        ]
    )
    if rating_trigger:
        summary_lines = ["=== Product Ratings Summary (all products) ==="]
        for _, txt_file, content in scored:
            rating = _extract_rating(content)
            prod = _extract_product_name(content)
            sku_m = re.search(r"\bSKU:\s*(\S+)", content)
            sku = sku_m.group(1) if sku_m else txt_file.stem
            summary_lines.append(f"{sku} | {prod} | rating: {rating}/5")
        ratings_block: str = "\n".join(summary_lines)
        parts.append(ratings_block)
        total_chars += len(ratings_block)

    for score, txt_file, content in scored[:3]:
        header = f"=== {txt_file.name} (relevance score: {score:.0f}) ==="
        chunk: str = header + "\n" + content
        if total_chars + len(chunk) > max_chars:
            remaining = max_chars - total_chars
            if remaining > 200:
                parts.append(chunk[:remaining] + "\n... [truncated]")
            break
        parts.append(chunk)
        total_chars += len(chunk)

    context: str = "\n\n".join(parts)
    logger.info(f"Text context length: {len(context)} chars from {len(scored)} files")
    return context
