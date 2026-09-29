import os
import re
import urllib.request
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
import html2text

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

NON_ENGLISH_PREFIXES = ('/indonesian/', '/turkish/', '/farsi/', '/arabic/', '/spanish/', '/russian/', '/german/', '/french/', '/malay/', '/urdu/')

def fetch_url(url):
    try:
        url_safe = urllib.parse.quote(url, safe=':/?#[]@!$&\'()*+,;=')
        req = urllib.request.Request(url_safe, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def clean_soup(soup):
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'svg', 'iframe']):
        tag.decompose()
    for tag in soup.find_all(class_=re.compile(r'menu|navbar|footer|header|cookie|alert|ad-')):
        tag.decompose()
    return soup

def html_to_markdown(html_content, base_url=""):
    if not html_content:
        return "", ""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ""
    
    main_content = soup.find('main') or soup.find('article') or soup.find('div', id='content') or soup.find('div', class_=re.compile(r'content|post|article|entry'))
    if not main_content:
        main_content = soup.body if soup.body else soup
        
    clean_soup(main_content)
    
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = True
    h2t.body_width = 0
    h2t.baseurl = base_url
    
    md = h2t.handle(str(main_content))
    md = re.sub(r'\n{3,}', '\n\n', md)
    return title, md.strip()

def crawl_miracles_of_quran():
    base_url = 'https://www.miracles-of-quran.com/'
    to_visit = {base_url}
    visited = set()
    pages_data = {}

    print("--- Starting Crawl of miracles-of-quran.com (English articles) ---")
    while to_visit:
        url = to_visit.pop()
        clean_url = urldefrag(url)[0]
        if clean_url in visited:
            continue
        visited.add(clean_url)
        
        parsed_path = urlparse(clean_url).path
        if any(parsed_path.startswith(prefix) for prefix in NON_ENGLISH_PREFIXES):
            continue

        print(f"Fetching: {clean_url}")
        html = fetch_url(clean_url)
        if not html:
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urljoin(clean_url, href)
            full_clean = urldefrag(full)[0]
            parsed = urlparse(full_clean)
            if parsed.netloc in ('www.miracles-of-quran.com', 'miracles-of-quran.com'):
                if (full_clean.endswith('.html') or full_clean.endswith('/')) and full_clean not in visited:
                    if not any(parsed.path.startswith(prefix) for prefix in NON_ENGLISH_PREFIXES):
                        to_visit.add(full_clean)
                    
        title, md = html_to_markdown(html, base_url=clean_url)
        if md and len(md) > 50:
            pages_data[clean_url] = {'title': title, 'content': md}

    print(f"Finished miracles-of-quran.com crawl. Total English pages scraped: {len(pages_data)}")
    return pages_data

def scrape_other_sites(sites_list):
    print("--- Starting Scraping of Additional Sites ---")
    other_data = {}
    for url in sites_list:
        if 'miracles-of-quran.com' in url:
            continue
        print(f"Fetching site: {url}")
        html = fetch_url(url)
        if html:
            title, md = html_to_markdown(html, base_url=url)
            other_data[url] = {'title': title, 'content': md}
    return other_data

def main():
    sites_file = '/media/farsim/8CE85861E8584C182/projects/Miracles_of_Quran/sites.txt'
    with open(sites_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]

    moq_pages = crawl_miracles_of_quran()
    other_pages = scrape_other_sites(lines)
    
    output_path = '/media/farsim/8CE85861E8584C182/projects/Miracles_of_Quran/Miracles_of_Quran_Gathered.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Miracles of Quran - Gathered Web Contents\n\n")
        f.write("This file contains the full gathered text contents from all the websites listed in `sites.txt`.\n\n")
        f.write("--- \n\n")
        
        f.write("## 1. miracles-of-quran.com (All English Sections & Pages)\n\n")
        for url in sorted(moq_pages.keys()):
            pinfo = moq_pages[url]
            f.write(f"### Section/Page: {pinfo['title'] or url}\n")
            f.write(f"**URL**: {url}\n\n")
            f.write(pinfo['content'])
            f.write("\n\n---\n\n")
            
        f.write("## 2. Additional Reference Sites\n\n")
        for url, pinfo in other_pages.items():
            f.write(f"### Site: {pinfo['title'] or url}\n")
            f.write(f"**URL**: {url}\n\n")
            f.write(pinfo['content'])
            f.write("\n\n---\n\n")

    print(f"\nALL DONE! Successfully saved gathered content to:\n{output_path}")

if __name__ == '__main__':
    main()
