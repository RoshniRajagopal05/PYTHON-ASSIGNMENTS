# Automated Text File Analyzer

A Python command-line application that analyzes `.txt` files in a specified directory and generates text statistics, word frequencies, and bigram analysis.

## Features

- Analyzes multiple text files.
- Calculates word, line, and character counts.
- Identifies frequently occurring words.
- Excludes common stop words from frequency analysis.
- Performs bigram analysis.
- Generates a consolidated CSV report.
- Handles empty files, missing directories, and unreadable files.

## Technologies

- Python
- pathlib
- collections.Counter
- CSV
- Regular Expressions

## Project Structure

```text
AutomatedTextFileAnalyzer/
├── main.py
├── .gitignore
├── test_data/
│   ├── empty.txt
│   ├── feedback1.txt
│   ├── feedback2.txt
│   └── feedback3.txt
└── output/
```

## How to Run

1. Clone or download the project.
2. Open the project directory in a terminal.
3. Run:

```bash
python main.py
```

4. Enter the folder path containing the `.txt` files when prompted.

## Output

The application displays file statistics, frequently occurring words, and bigrams in the terminal.

A consolidated CSV report is generated in the output directory.
