import bs4

def first_paragraph_text(html):
    soup = bs4.BeautifulSoup(html)
    for paragraph in soup.find_all('p'):
        text = paragraph.get_text()
        if not text:
            continue
        return text
    return ""

def truncate_first_paragraph(html, max_length):
    """
    Truncate the first non-empty paragraph from an html text such that its
    total length (including '...') is less than or equal to max_length.
    """
    text = first_paragraph_text(html)
    if len(text) <= max_length:
        return text
    else:
        new_text_length = max(max_length - 3, 0)
        return text[:new_text_length] + "..."
