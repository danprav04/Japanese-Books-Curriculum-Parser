import os
import re
import shutil
import tempfile
import mobi
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_and_chunk(input_file, base_output_dir):
    """
    Takes an input book file, extracts the text, and chunks it by chapters.
    Returns the book title and a list of paths to the extracted chapter text files.
    """
    ext = os.path.splitext(input_file)[1].lower()
    basename = os.path.basename(input_file)
    book_title = os.path.splitext(basename)[0]
    
    book_output_dir = os.path.join(base_output_dir, book_title)
    os.makedirs(book_output_dir, exist_ok=True)
    
    chapter_files = []
    
    if ext == ".txt":
        chapter_files = chunk_text_file(input_file, book_output_dir)
    elif ext in [".mobi", ".azw", ".azw3"]:
        print(f"Unpacking {ext} file with mobi...")
        tempdir, epub_filepath = mobi.extract(input_file)
        chapter_files = chunk_epub_file(epub_filepath, book_output_dir)
        # Clean up temporary epub directory
        shutil.rmtree(tempdir, ignore_errors=True)
    elif ext == ".epub":
        chapter_files = chunk_epub_file(input_file, book_output_dir)
    else:
        print(f"Unsupported extension: {ext}")
        
    return book_title, chapter_files

def get_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script/style tags
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text(separator='\n')
    # Clean up empty lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def chunk_epub_file(epub_path, output_dir):
    book = epub.read_epub(epub_path)
    
    # 1. Parse TOC to get start markers for chapters
    # We map the filename (without the anchor) to the Chapter Title
    toc_mapping = {}
    
    def process_toc(items):
        for item in items:
            if isinstance(item, ebooklib.epub.Link):
                filename = item.href.split('#')[0]
                if filename not in toc_mapping:
                    toc_mapping[filename] = item.title
            elif isinstance(item, tuple):
                # Section with subchapters
                process_toc([item[0]])
                process_toc(item[1])
            elif isinstance(item, ebooklib.epub.Section):
                filename = item.href.split('#')[0]
                if filename not in toc_mapping:
                    toc_mapping[filename] = item.title
                    
    process_toc(book.toc)
    
    chapters = []
    current_chapter_title = "00 - Front Matter"
    current_chapter_text = []
    chapter_counter = 0
    
    # 2. Iterate through all document items (HTML files) in order
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        filename = item.get_name()
        
        # If this filename is in the TOC, it's the start of a new chapter
        if filename in toc_mapping:
            if current_chapter_text:
                chapters.append((current_chapter_title, "\n".join(current_chapter_text)))
            chapter_counter += 1
            raw_title = toc_mapping[filename]
            safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title)[:50].strip()
            current_chapter_title = f"{chapter_counter:02d} - {safe_title}"
            current_chapter_text = []
            
        # Extract text from this HTML chunk
        html_content = item.get_content()
        text = get_text_from_html(html_content)
        if text:
            current_chapter_text.append(text)
            
    # Add the last chapter
    if current_chapter_text:
        chapters.append((current_chapter_title, "\n".join(current_chapter_text)))
        
    # 3. Write out to text files
    saved_files = []
    for title, text_content in chapters:
        if not text_content.strip():
            continue
        file_path = os.path.join(output_dir, f"{title}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        saved_files.append(file_path)
        
    return saved_files

def chunk_text_file(txt_file, output_dir):
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    lines = content.split('\n')
    chapters = []
    current_chapter_title = "00 - Front Matter"
    current_chapter_lines = []
    chapter_counter = 0
    
    for line in lines:
        stripped = line.strip()
        if re.match(r'^(第[一二三四五六七八九十百\d]+章|プロローグ|エピローグ|特別付録|Chapter\s*\d+)', stripped, re.IGNORECASE):
            if current_chapter_lines:
                chapters.append((current_chapter_title, current_chapter_lines))
            chapter_counter += 1
            safe_title = re.sub(r'[\\/*?:"<>|]', "", stripped)[:50]
            current_chapter_title = f"{chapter_counter:02d} - {safe_title}"
            current_chapter_lines = [line]
        else:
            current_chapter_lines.append(line)
            
    if current_chapter_lines:
        chapters.append((current_chapter_title, current_chapter_lines))
        
    saved_files = []
    for title, chap_lines in chapters:
        text_content = "\n".join(chap_lines).strip()
        if not text_content:
            continue
        file_path = os.path.join(output_dir, f"{title}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        saved_files.append(file_path)
        
    return saved_files
