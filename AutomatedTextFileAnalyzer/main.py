
from pathlib import Path
from collections import Counter
import csv
import re


STOP_WORDS = {
    "the", "is", "and", "a", "an", "are", "was", "were",
    "in", "on", "at", "to", "of", "for", "with", "this",
    "that", "it", "as", "by", "be", "from", "or", "but",
    "have", "has", "had", "i", "we", "you", "he", "she",
    "they", "my", "our", "your", "their", "its"
}


def tokenize(text):
    """Convert text into lowercase word tokens."""
    return re.findall(r"\b[\w']+\b", text.lower())


def analyze_file(file_path):
    """Calculate file statistics and word frequencies."""

    try:
        text = file_path.read_text(encoding="utf-8")

        words = tokenize(text)

        # Statistics are calculated independently of stop words.
        total_words = len(words)
        total_lines = len(text.splitlines())
        total_characters = len(text)

        # Remove stop words only for frequency analysis.
        filtered_words = [
            word for word in words if word not in STOP_WORDS
        ]

        word_counts = Counter(filtered_words)

        # Bigrams are calculated from consecutive filtered words.
        bigrams = [
            f"{filtered_words[i]} {filtered_words[i + 1]}"
            for i in range(len(filtered_words) - 1)
        ]

        bigram_counts = Counter(bigrams)

        return {
            "file": file_path.name,
            "words": total_words,
            "lines": total_lines,
            "characters": total_characters,
            "word_counts": word_counts,
            "bigram_counts": bigram_counts,
        }

    except (OSError, UnicodeDecodeError) as error:
        print(f"\nUnable to read {file_path.name}: {error}")
        return None


def save_csv_report(results, output_path):
    """Save consolidated file statistics to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(["File", "Words", "Lines", "Characters"])

        for result in results:
            writer.writerow([
                result["file"],
                result["words"],
                result["lines"],
                result["characters"]
            ])


def main():
    print("=" * 55)
    print("          AUTOMATED TEXT FILE ANALYZER")
    print("=" * 55)

    folder_input = input("Enter folder path containing text files: ").strip()

    folder_path = Path(folder_input)

    if not folder_path.exists():
        print("\nError: Directory does not exist.")
        return

    if not folder_path.is_dir():
        print("\nError: The specified path is not a directory.")
        return

    # Only .txt files directly inside the specified directory.
    text_files = sorted(
        file for file in folder_path.iterdir()
        if file.is_file() and file.suffix.lower() == ".txt"
    )

    if not text_files:
        print("\nNo text files found in the specified directory.")
        return

    print(f"\nText files found: {len(text_files)}")
    print("\nAnalyzing files...")

    results = []
    overall_word_counts = Counter()
    overall_bigram_counts = Counter()

    for file_path in text_files:
        result = analyze_file(file_path)

        if result is None:
            continue

        results.append(result)

        overall_word_counts.update(result["word_counts"])
        overall_bigram_counts.update(result["bigram_counts"])

        print(f"Analyzed: {result['file']}")

    if not results:
        print("\nNo files could be successfully analyzed.")
        return

    # Display consolidated statistics.
    print("\n" + "=" * 55)
    print("                 FILE STATISTICS")
    print("=" * 55)

    print(f"{'File':<25}{'Words':<10}{'Lines':<10}{'Characters':<12}")
    print("-" * 55)

    for result in results:
        print(
            f"{result['file']:<25}"
            f"{result['words']:<10}"
            f"{result['lines']:<10}"
            f"{result['characters']:<12}"
        )

    # Most frequent words.
    print("\n" + "=" * 55)
    print("          MOST FREQUENT WORDS")
    print("=" * 55)

    if overall_word_counts:
        for word, count in overall_word_counts.most_common(10):
            print(f"{word:<20} : {count}")
    else:
        print("No words available for frequency analysis.")

    # Most frequent bigrams.
    print("\n" + "=" * 55)
    print("          MOST FREQUENT BIGRAMS")
    print("=" * 55)

    if overall_bigram_counts:
        for bigram, count in overall_bigram_counts.most_common(10):
            print(f"{bigram:<30} : {count}")
    else:
        print("No bigrams available for analysis.")

    # Generate consolidated CSV report.
    output_path = folder_path / "output" / "text_analysis_report.csv"

    save_csv_report(results, output_path)

    print("\n" + "=" * 55)
    print("                 REPORT GENERATED")
    print("=" * 55)

    print(f"CSV report saved to: {output_path}")
    print(f"Successfully analyzed files: {len(results)}")


if __name__ == "__main__":
    main()
