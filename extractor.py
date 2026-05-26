import os
import re
import shutil
import zipfile

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
        # Handle plain text format
        chapter_files = chunk_text_file(input_file, book_output_dir)
    elif ext in [".epub", ".mobi", ".azw", ".azw3"]:
        # Fallback basic extraction for epub using zipfile (if no ebooklib installed)
        # Note: True epub parsing would use ebooklib/BeautifulSoup
        # For this production script, we will treat it as text if possible or fail gracefully
        # In a real scenario, you'd use 'mobi' or 'epub' python libraries.
        print(f"Warning: Native {ext} extraction is basic. Consider converting to .txt first.")
        # Try to read as text anyway (might contain raw HTML)
        try:
            chapter_files = chunk_text_file(input_file, book_output_dir)
        except Exception as e:
            print(f"Failed to read {ext} as text: {e}")
    else:
        print(f"Unsupported extension: {ext}")
        
    return book_title, chapter_files

def chunk_text_file(txt_file, output_dir):
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Heuristic for Japanese novel chapters: "第X章", "Chapter X", "プロローグ", "エピローグ"
    # We will split the text when we encounter lines matching these patterns.
    lines = content.split('\n')
    
    chapters = []
    current_chapter_title = "00 - Front Matter"
    current_chapter_lines = []
    
    chapter_counter = 0
    
    for line in lines:
        stripped = line.strip()
        # Regex to match typical Japanese light novel chapter headings
        if re.match(r'^(第[一二三四五六七八九十百0-9]+章|プロローグ|エピローグ|Chapter\s*\d+)', stripped, re.IGNORECASE):
            # Save the previous chapter
            if current_chapter_lines:
                chapters.append((current_chapter_title, current_chapter_lines))
                
            chapter_counter += 1
            # Clean up title for filename safety
            safe_title = re.sub(r'[\\/*?:"<>|]', "", stripped)[:50]
            current_chapter_title = f"{chapter_counter:02d} - {safe_title}"
            current_chapter_lines = [line]
        else:
            current_chapter_lines.append(line)
            
    # Save the last chapter
    if current_chapter_lines:
        chapters.append((current_chapter_title, current_chapter_lines))
        
    saved_files = []
    for title, chap_lines in chapters:
        # Don't save empty chapters
        text_content = "\n".join(chap_lines).strip()
        if not text_content:
            continue
            
        file_path = os.path.join(output_dir, f"{title}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        saved_files.append(file_path)
        
    return saved_files
