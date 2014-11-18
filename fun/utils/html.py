import bs4

def first_image_src(html):
    img = first_image(html)
    if img is None:
        return ""
    return img['src']

def first_image(html):
    soup = bs4.BeautifulSoup(html)
    return soup.find('img')

def first_paragraph_text(html, max_length=None):
    soup = bs4.BeautifulSoup(html)
    paragraph = soup.find('p')
    if paragraph is None:
        return ""
    text = paragraph.get_text()
    if max_length is not None:
        return text[:max_length]
    else:
        return text

