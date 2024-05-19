import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def count_words(text):
    # Simple word count by splitting on whitespace.
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def get_chapter_text(item):
    soup = BeautifulSoup(item.get_body_content(), 'html.parser')
    text = soup.get_text()
    word_count = count_words(text)
    return word_count

def main(epub_file):
    book = epub.read_epub(epub_file)
    chapter_word_counts = {}
    total_word_count = 0

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT and item.get_name().startswith('ch'):
            chapter_count = get_chapter_text(item)
            chapter_word_counts[item.get_name()] = chapter_count
            total_word_count += chapter_count

    sorted_chapters = sorted(chapter_word_counts.items())

    for chapter, count in sorted_chapters:
        print(f"{chapter}: {count} words")

    print(f"Total word count: {total_word_count} words")

if __name__ == "__main__":
    epub_file = '1.epub'
    main(epub_file)
