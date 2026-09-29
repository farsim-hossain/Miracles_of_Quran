import re

def clean_article_text(text):
    # Remove Mobirise category cards and menu blocks
    text = re.sub(r'#### \*\*From Arithmetics to Astrophysics\*\*[\s\S]*?(?=### |\n{3,}|\Z)', '', text)
    text = re.sub(r'\[\]\(https://www\.miracles-of-quran\.com/[^\)]+\)\s*##### \*\*[^\*]+\*\*\s*[^\n]+\s*\[Learn More\][^\n]+', '', text)
    
    # Remove orphan links to category pages
    text = re.sub(r'\[\*\*[^\*]+\*\*\]\(https://www\.miracles-of-quran\.com/(?:mathematics|astronomy|history|physics|geology|zoology|physiology|embryology|meteorology|biology|cosmology)\.html\)', '', text)
    
    # Remove redundant empty lines and markup artifacts
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if l in ['‌', '__', '#####', '##### _', '#####  _', '#####   ', '#####    ', '#####     ', '#####  **  '] or re.match(r'^#+\s*$', l):
            continue
        if l.startswith('[](') and l.endswith(')'):
            continue
        cleaned_lines.append(line)
        
    res = '\n'.join(cleaned_lines)
    res = re.sub(r'\n{3,}', '\n\n', res)
    return res.strip()

def main():
    file_path = '/media/farsim/8CE85861E8584C182/projects/Miracles_of_Quran/Miracles_of_Quran_Gathered.md'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = content.split('### Article/Section: ')
    header_block = sections[0]
    
    category_pages = [
        'Astronomy In Quran', 'Biology In Quran.', 'Chemistry In Quran.',
        'Cosmology In Quran.', 'Embryology In Quran.', 'Geology In Quran.',
        'History In Quran.', 'Mathematics In Quran.', 'Physics In Quran.',
        'Physiology In Quran.', 'Search.', 'Meteorology In Quran.'
    ]

    valid_articles = []
    skipped_categories = []

    for sec in sections[1:]:
        lines = sec.strip().split('\n')
        title_line = lines[0].strip()
        
        # Check if category menu page
        if any(cat in title_line for cat in category_pages):
            skipped_categories.append(title_line)
            continue
            
        cleaned_body = clean_article_text('\n'.join(lines[1:]))
        
        # Calculate text length
        pure_text = re.sub(r'#|\*|\[[^\]]+\]\([^\)]+\)', '', cleaned_body).strip()
        
        valid_articles.append({
            'title': title_line,
            'body': cleaned_body,
            'text_len': len(pure_text),
            'words': len(pure_text.split())
        })

    print(f"Total articles processed: {len(sections)-1}")
    print(f"Category menu pages filtered out: {len(skipped_categories)}")
    print(f"Valid full articles retained: {len(valid_articles)}")

    # Write back clean validated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# Miracles of Quran - Validated Full Web Contents\n\n")
        f.write("This file contains the complete, clean, validated text contents from all articles listed in `sites.txt`.\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Full Articles from miracles-of-quran.com\n\n")
        for art in valid_articles:
            if 'questionsonislam.com' in art['body'] or 'medium.com' in art['body'] or 'riwaya.co.uk' in art['body'] or 'iqra-quran.com' in art['body']:
                continue
            f.write(f"### Article: {art['title']}\n")
            f.write(art['body'])
            f.write("\n\n---\n\n")
            
        f.write("## 2. Additional Reference Sites\n\n")
        for art in valid_articles:
            if 'questionsonislam.com' in art['body'] or 'medium.com' in art['body'] or 'riwaya.co.uk' in art['body'] or 'iqra-quran.com' in art['body']:
                f.write(f"### Article: {art['title']}\n")
                f.write(art['body'])
                f.write("\n\n---\n\n")

    # Validate output lengths
    short_ones = [a for a in valid_articles if a['words'] < 30]
    print(f"\nValidation check: Articles with < 30 words: {len(short_ones)}")
    for s in short_ones:
        print(f"  - Short article: {s['title']} ({s['words']} words)")

if __name__ == '__main__':
    main()
