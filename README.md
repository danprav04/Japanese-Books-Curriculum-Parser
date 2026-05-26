# Japanese Books Curriculum Parser

This repository contains a production-ready script that parses Japanese book files (currently tailored for `.txt` files containing entire novels, but accepts `.epub` and `.mobi` to extract raw text) into individual chapters. It then analyzes the Japanese text using MeCab to extract 100% of the vocabulary and key grammar points, generating a structured, JLPT-segregated Markdown curriculum for each chapter.

## Requirements

- Python 3.8+
- The `MeCab` morphological analyzer requires the `mecab-python3` and `unidic-lite` packages.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Japanese-Books-Curriculum-Parser.git
   cd Japanese-Books-Curriculum-Parser
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script by passing the path to the book file:

```bash
python main.py "path/to/your/book.txt"
```

By default, the script will output the chunked chapters and the generated `Curriculum.md` into an `output/` directory located in the current working directory. 

You can specify a custom output directory using the `--output_dir` flag:

```bash
python main.py "path/to/your/book.txt" --output_dir "custom_output"
```

## How It Works

1. **Extraction**: The script first attempts to split the text into chapters based on standard Japanese light novel headings (e.g., `第X章`, `プロローグ`).
2. **NLP Tokenization**: It uses `MeCab` to tokenize the Japanese text, extracting every noun, verb, and adjective in each chapter.
3. **JLPT Segregation**: Using built-in datasets in `jlpt_data/`, it categorizes the vocabulary into N5, N4, N3, N2, N1, and Unclassified groups.
4. **Grammar Extraction**: It scans for important Japanese grammar points (N5 to N1 levels).
5. **Curriculum Generation**: Finally, it compiles a `.md` curriculum file summarizing everything for each chapter.
