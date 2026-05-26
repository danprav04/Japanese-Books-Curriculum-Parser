import os
import argparse
import sys

# Ensure stdout and stderr support utf-8 to avoid crash on Japanese characters
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from extractor import extract_and_chunk
from curriculum_builder import build_curriculum_for_book

def main():
    parser = argparse.ArgumentParser(description="Japanese Books Curriculum Parser")
    parser.add_argument("input_file", help="Path to the book file (.txt, .epub, .mobi, .azw)")
    parser.add_argument("--output_dir", default="output", help="Directory to save the parsed chapters and curriculum")
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_dir = args.output_dir
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return
        
    print(f"Processing {input_file}...")
    
    # 1. Extract and chunk the book into chapters
    book_title, chapter_files = extract_and_chunk(input_file, output_dir)
    if not chapter_files:
        print("Error: Could not extract any chapters.")
        return
        
    print(f"Extracted {len(chapter_files)} chapters for '{book_title}'.")
    
    # 2. Build the JLPT curriculum
    book_output_dir = os.path.join(output_dir, book_title)
    print("Generating curriculum...")
    curriculum_file = build_curriculum_for_book(book_title, book_output_dir, chapter_files)
    
    print(f"\nSuccess! Curriculum generated at: {curriculum_file}")

if __name__ == "__main__":
    main()
