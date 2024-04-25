import os
import sys
import PyPDF2
from ebooklib import epub


def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
    return text


def detect_chapters(text):
    chapters = []
    lines = text.split('\n')
    current_chapter = ''
    for line in lines:
        # Example: if font size changes, treat it as a new chapter
        if line.strip() and line.strip()[0].isdigit():
            if current_chapter:
                chapters.append(current_chapter.strip())
            current_chapter = line
        else:
            current_chapter += '\n' + line
    if current_chapter:
        chapters.append(current_chapter.strip())
    return chapters


def create_epub(chapters, output_file):
    book = epub.EpubBook()
    book.set_title("Converted ePub")
    book.set_language("en")

    for index, chapter_text in enumerate(chapters, start=1):
        chapter = epub.EpubHtml(
            title=f"Chapter {index}", file_name=f"chapter_{index}.xhtml")
        chapter.content = f"<h1>Chapter {index}</h1><p>{chapter_text}</p>"
        book.add_item(chapter)
        book.toc.append(chapter)

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = 'body { font-family: Times, Times New Roman, serif; }'
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    book.spine = ['nav'] + list(book.get_items())

    epub.write_epub(output_file, book, {})


if __name__ == "__main__":
    # Check if PDF file name is provided as command-line argument
    if len(sys.argv) != 2:
        print("Usage: python main.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    # Output ePub file with the same base name as PDF file
    epub_file = os.path.splitext(pdf_file)[0] + ".epub"

    text = extract_text_from_pdf(pdf_file)
    chapters = detect_chapters(text)
    create_epub(chapters, epub_file)

    print(f"Conversion complete. ePub saved as {epub_file}")
