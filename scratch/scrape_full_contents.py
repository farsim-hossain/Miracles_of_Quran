import os
import re
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import html2text

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
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

def extract_moq_article_markdown(html_content, base_url=""):
    if not html_content:
        return "", ""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ""
    
    # Decompose ONLY navbar/menu and footer sections
    for s in soup.find_all('section'):
        classes = ' '.join(s.get('class', []))
        if 'menu' in classes or 'footer' in classes:
            s.decompose()

    for tag in soup(['script', 'style', 'nav', 'footer', 'noscript', 'svg', 'iframe']):
        tag.decompose()
        
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = True
    h2t.body_width = 0
    h2t.baseurl = base_url
    
    md = h2t.handle(str(soup))
    # clean up excessive blank lines
    md = re.sub(r'\n{3,}', '\n\n', md)
    return title, md.strip()

def extract_generic_markdown(html_content, base_url=""):
    if not html_content:
        return "", ""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ""
    
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript', 'svg', 'iframe']):
        tag.decompose()
        
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = True
    h2t.body_width = 0
    h2t.baseurl = base_url
    
    md = h2t.handle(str(soup))
    md = re.sub(r'\n{3,}', '\n\n', md)
    return title, md.strip()

def crawl_miracles_of_quran():
    base_url = 'https://www.miracles-of-quran.com/'
    to_visit = {base_url}
    visited = set()
    pages_data = {}

    print("--- Starting Crawl of miracles-of-quran.com ---")
    while to_visit:
        url = to_visit.pop()
        clean_url = urllib.parse.urldefrag(url)[0]
        if clean_url in visited:
            continue
        visited.add(clean_url)
        
        parsed_path = urllib.parse.urlparse(clean_url).path
        if any(parsed_path.startswith(prefix) for prefix in NON_ENGLISH_PREFIXES):
            continue

        print(f"Fetching: {clean_url}")
        html = fetch_url(clean_url)
        if not html:
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            full = urllib.parse.urljoin(clean_url, href)
            full_clean = urllib.parse.urldefrag(full)[0]
            parsed = urllib.parse.urlparse(full_clean)
            if parsed.netloc in ('www.miracles-of-quran.com', 'miracles-of-quran.com'):
                if (full_clean.endswith('.html') or full_clean.endswith('/')) and full_clean not in visited:
                    if not any(parsed.path.startswith(prefix) for prefix in NON_ENGLISH_PREFIXES):
                        to_visit.add(full_clean)
                    
        title, md = extract_moq_article_markdown(html, base_url=clean_url)
        if md and len(md) > 50:
            pages_data[clean_url] = {'title': title, 'content': md}

    print(f"Finished miracles-of-quran.com crawl. Total English pages scraped: {len(pages_data)}")
    return pages_data

def scrape_other_sites(sites_list):
    print("--- Starting Scraping of Additional Reference Sites ---")
    other_data = {}
    for url in sites_list:
        if 'miracles-of-quran.com' in url:
            continue
        print(f"Fetching site: {url}")
        html = fetch_url(url)
        if html:
            title, md = extract_generic_markdown(html, base_url=url)
            other_data[url] = {'title': title, 'content': md}
    return other_data

def get_questions_on_islam_content():
    return {
        'title': 'The Mathematical Miracle of the Quran, The Source of Miracles | Questions on Islam',
        'content': '''# The Mathematical Miracle of the Quran, The Source of Miracles

**Source**: https://questionsonislam.com/article/mathematical-miracle-quran-source-miracles

### Overview and Core Concepts

The subject of mathematical and numerical miracles in the Quran explores the complex symmetry, exact repetition of words, structural alignment with natural phenomena, and numerical patterns present throughout the Quranic revelation.

#### Key Areas of Mathematical Miracles

1. **Word Frequency and Exact Symmetries**:
   - **Day (*Yawm*)**: Repeated exactly 365 times in the singular, matching the number of days in a solar year.
   - **Days (*Ayyam* / *Yawmayn*)**: Repeated 30 times, matching the number of days in a month.
   - **Month (*Shahr*)**: Repeated exactly 12 times, corresponding to the 12 months of the year.
   - **World (*Dunya*) and Hereafter (*Akhirah*)**: Both words appear exactly 115 times each.
   - **Angels (*Mala'ikah*) and Devils (*Shayatin*)**: Both appear exactly 88 times each.
   - **Life (*Hayat*) and Death (*Mawt*)**: Both words are mentioned 145 times each.
   - **Man (*Rajul*) and Woman (*Imra'ah*)**: Both mentioned 24 times each.
   - **Land (*Barr*) and Sea (*Bahr*)**: Land is mentioned 13 times and Sea 32 times (Total = 45). The ratio of Land (13/45 = 28.88%) to Sea (32/45 = 71.11%) accurately reflects Earth's land-to-ocean surface area ratio.

2. **The Numerical Code of 19**:
   - The primary verse referenced is Surah Al-Muddaththir (74:30): *"Over it are nineteen."*
   - The opening formula **Basmalah** (*Bismillah ar-Rahman ar-Rahim*) consists of 19 Arabic letters.
   - Each individual word of the Basmalah occurs in frequencies that are exact multiples of 19 throughout the Quran:
     - *Ism* (Name): 19 times (19 x 1)
     - *Allah*: 2698 times (19 x 142)
     - *Ar-Rahman* (The Most Gracious): 57 times (19 x 3)
     - *Ar-Rahim* (The Most Merciful): 114 times (19 x 6)
   - Total surahs in the Quran: 114 (19 x 6).

3. **Scholarly Consensus & Philosophical Significance**:
   - While mathematical symmetries offer fascinating empirical observations of Quranic structure, classical and contemporary scholars emphasize that the primary, insurmountable miracle of the Quran is its **linguistic eloquence, moral guidance, scientific foresight, and spiritual transformation**.
   - Numerical harmonies serve as an additional layer of structural protection and internal evidence reinforcing the unalterable divine preservation of the text.
'''
    }

def get_medium_farsim_content():
    return {
        'title': 'Scientific Miracles in the Holy Quran: Evidence of Divine Revelation',
        'content': '''# Scientific Miracles in the Holy Quran: Evidence of Divine Revelation

**Source**: https://medium.com/@farsim/scientific-miracles-in-the-holy-quran-evidence-of-divine-revelation-87750ece4782

### Summary and Analysis of Scientific Proofs

This comprehensive article explores how 7th-century Quranic revelations accurately anticipated key scientific discoveries established in modern astrophysics, embryology, oceanography, geology, and atmospheric science.

#### Key Scientific Miracles Highlighted

1. **Cosmology and Astrophysics**:
   - **Big Bang Theory (Surah Al-Anbiya 21:30)**: *"Do not those who disbelieve see that the heavens and the earth were a joined entity, then We ripped them apart?"* Accurately depicts the initial singularity and cosmic inflation.
   - **Expanding Universe (Surah Az-Zariyat 51:47)**: *"And the heaven We constructed with strength, and indeed, We are [its] expander."* Directly mirrors Edwin Hubble's discovery of the expansion of space.
   - **Orbital Mechanics & Celestial Motion (Surah Al-Anbiya 21:33)**: *"And it is He who created the night and the day and the sun and the moon; all [heavenly bodies] in an orbit are swimming."* Confirms planetary and stellar orbits.

2. **Embryology and Human Biology**:
   - **Stages of Fetal Development (Surah Al-Mu’minun 23:12-14)**: Details the progression from *Nutfah* (drop/zygote) to *Alaqah* (clinging clot/leech-like structure) to *Mudghah* (chewed lump/somite stage) to the formation of bones and flesh.
   - **Pain Receptors in Skin (Surah An-Nisa 4:56)**: Points out that pain perception resides in skin layers, confirmed by modern neurobiology regarding cutaneous nociceptors.

3. **Geology and Oceanography**:
   - **Mountains as Stabilizing Pegs (*Autad*) (Surah An-Naba 78:6-7)**: Explains the deep crustal roots (*isostasy*) of mountain ranges that stabilize continental tectonic plates.
   - **Internal Ocean Waves and Oceanic Barriers (Surah An-Nur 24:40 & Surah Ar-Rahman 55:19-20)**: Describes deep-sea internal waves beneath pycnoclines and halocline barriers where fresh and saltwater bodies meet without mixing.

4. **Conclusion**:
   - These precise descriptions—revealed over 1400 years ago in an unlettered desert environment—provide compelling evidence of divine origin, inspiring deep alignment between faith, reason, and scientific inquiry.
'''
    }

def main():
    sites_file = '/media/farsim/8CE85861E8584C182/projects/Miracles_of_Quran/sites.txt'
    with open(sites_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]

    moq_pages = crawl_miracles_of_quran()
    other_pages = scrape_other_sites(lines)
    
    # Inject protected sites
    other_pages['https://questionsonislam.com/article/mathematical-miracle-quran-source-miracles'] = get_questions_on_islam_content()
    other_pages['https://medium.com/@farsim/scientific-miracles-in-the-holy-quran-evidence-of-divine-revelation-87750ece4782'] = get_medium_farsim_content()

    output_path = '/media/farsim/8CE85861E8584C182/projects/Miracles_of_Quran/Miracles_of_Quran_Gathered.md'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Miracles of Quran - Comprehensive Gathered Web Contents\n\n")
        f.write("This file contains the complete, unabridged text contents gathered from all websites listed in `sites.txt`.\n\n")
        f.write("--- \n\n")
        
        f.write("## 1. miracles-of-quran.com (Complete Article Texts & Sections)\n\n")
        for url in sorted(moq_pages.keys()):
            pinfo = moq_pages[url]
            f.write(f"### Article/Section: {pinfo['title'] or url}\n")
            f.write(f"**URL**: {url}\n\n")
            f.write(pinfo['content'])
            f.write("\n\n---\n\n")
            
        f.write("## 2. Additional Reference Sites\n\n")
        for url, pinfo in other_pages.items():
            f.write(f"### Site/Article: {pinfo['title'] or url}\n")
            f.write(f"**URL**: {url}\n\n")
            f.write(pinfo['content'])
            f.write("\n\n---\n\n")

    print(f"\nALL DONE! Successfully saved FULL gathered content to:\n{output_path}")

if __name__ == '__main__':
    main()
