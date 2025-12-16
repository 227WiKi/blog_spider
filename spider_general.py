import os
import hashlib
import re
import shutil
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urljoin
from tqdm import tqdm

# --- Configuration ---
BASE_URL = "https://nanabunnonijyuuni-mobile.com"
BLOG_LIST_URL = f"{BASE_URL}/s/n110/diary/official_blog/list"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
}

NAME_MAP = {
    "天城サリー": "sally", "河瀬詩": "uta", "西條和": "nagomi", "涼花萌": "moe",
    "相川奈央": "nao", "麻丘真央": "mao", "椎名桜月": "satsuki", "四条月": "luna",
    "月城咲舞": "emma", "望月りの": "rino", "折本美玲": "mirei", "北原実咲": "misaki",
    "黒崎ありす": "alice", "橘茉奈": "mana", "桧山依子": "iko", "三雲遥加": "haruka",
    "南伊織": "minami", "吉沢珠璃": "julie"
}

@dataclass
class BlogPost:
    title: str
    author_raw: str
    author_en: str
    date: str
    description: str
    link: str
    cover: str
    
    def get_id(self):
        """Generates MD5 hash (Strictly compatible with old logic)"""
        # Logic: author_en + "-" + date + "-" + raw_title (no strip)
        raw_str = f"{self.author_en}-{self.date}-{self.title}"
        return hashlib.md5(raw_str.encode('utf-8')).hexdigest()

class BlogScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        self.base_dir = os.getcwd()
        self.latest_file = os.path.join(self.base_dir, "latest")
        self.updates_dir = os.path.join(self.base_dir, "updates")
        
        self.new_posts_count = 0

    def get_soup(self, url):
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code != 200: return None
            return BeautifulSoup(resp.text, "html.parser")
        except:
            return None

    def parse_list_page(self, page_num):
        url = f"{BLOG_LIST_URL}?page={page_num}"
        soup = self.get_soup(url)
        
        if not soup or "記事がありません" in soup.text:
            return []

        posts = []
        titles = soup.find_all('div', class_="blog-list__title")
        descs = soup.find_all('div', class_="blog-list__txt")
        links = soup.find_all('div', class_="blog-list__more")
        thumbs = soup.find_all('div', class_="blog-list__thumb")
        
        for t, d, l, th in zip(titles, descs, links, thumbs):
            date_str = t.find('p', class_="date").text.replace(".", "-")
            title_str = t.find('p', class_="title").text
            author_raw = t.find('p', class_="name").text
            author_en = NAME_MAP.get(author_raw, "unknown")
            
            desc_text = d.find('p', class_="txt").text
            desc_text = desc_text.replace("\n","").replace("\ufeff","").replace("\u3000"," ").replace("&nbsp"," ")
            
            link_url = l.find('a').get('href')
            
            thumb_style = th.find("img").attrs.get("style", "")
            cover_url = " "
            if "noimage.jpg" not in thumb_style:
                match = re.search(r'url\((.*?)\)', thumb_style)
                if match:
                    cover_url = urljoin(BASE_URL, match.group(1))

            posts.append(BlogPost(
                title=title_str, author_raw=author_raw, author_en=author_en,
                date=date_str, description=desc_text, link=link_url, cover=cover_url
            ))
        return posts

    def download_image(self, url, author_en):
        if not url.startswith("http"): return
        filename = os.path.basename(url)
        
        save_dir = os.path.join(self.updates_dir, author_en)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)

        if not os.path.exists(save_path):
            try:
                r = self.session.get(url, stream=True, timeout=20)
                if r.status_code == 200:
                    total_size = int(r.headers.get('content-length', 0))
                    # Progress bar for individual image download
                    with open(save_path, 'wb') as f, tqdm(
                        desc=f"Img: {filename[:10]}", 
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        leave=False,
                        ncols=80
                    ) as bar:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                            bar.update(len(chunk))
            except Exception as e:
                tqdm.write(f"! Image download failed: {filename} - {e}")

    def process_content(self, post: BlogPost):
        full_link = urljoin(BASE_URL, post.link)
        soup = self.get_soup(full_link)
        if not soup: return ""

        if soup.find('div', class_="btnTweet"):
            soup.find('div', class_="btnTweet").decompose()

        content_div = soup.find('div', class_="blog_detail__main")
        if not content_div: return ""

        for p in content_div.find_all('p'):
            if p.get('style'):
                p['style'] = re.sub(r'(caret-color|color):[^;]+;?', '', p['style'])

        imgs = content_div.find_all('img')
        for img in imgs:
            src = img.get('src')
            if src:
                abs_src = urljoin(BASE_URL, src)
                self.download_image(abs_src, post.author_en)
                
                filename = os.path.basename(abs_src)
                # Wiki link format
                new_link = f"https://files.227wiki.eu.org/d/Backup/Blog/{post.author_en}/{filename}"
                img['src'] = new_link
        
        if post.cover.strip() != "":
             self.download_image(post.cover, post.author_en)

        return str(content_div)

    def save_markdown(self, post: BlogPost, content_html):
        post_id = post.get_id()
        filename = f"{post_id}.md"
        
        cover_link = ""
        if post.cover.strip():
             cover_name = os.path.basename(post.cover)
             cover_link = f"https://files.227wiki.eu.org/d/Backup/Blog/{post.author_en}/{cover_name}"

        md_content = (
            "---\n"
            f"title: {post.title}\n"
            f"date: {post.date}\n"
            f"tags: {post.author_raw}\n"
            "categories: \n- 成员博客\n- " + post.author_raw + "\n"
            f"description: {post.description}\n"
            f"{'cover: ' + cover_link + chr(10) if cover_link else ''}"
            "---\n"
            f"{content_html}"
        )

        # Save to permanent author directory
        author_dir = os.path.join(self.base_dir, post.author_en)
        os.makedirs(author_dir, exist_ok=True)
        with open(os.path.join(author_dir, filename), 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Save to updates directory
        with open(os.path.join(self.updates_dir, filename), 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.new_posts_count += 1

    def run(self):
        last_hash = ""
        if os.path.exists(self.latest_file):
            with open(self.latest_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content: last_hash = content
        
        if os.path.exists(self.updates_dir):
            shutil.rmtree(self.updates_dir)
        os.makedirs(self.updates_dir)

        print(f"=== 22/7 Blog Scraper Started ===")
        print(f"Last hash: {last_hash if last_hash else 'None (Full Scrape)'}")
        
        page = 0
        new_latest_hash = None
        has_new_posts = False

        while True:
            posts = self.parse_list_page(page)
            
            if not posts:
                print("\nNo more pages.")
                break

            # Process posts with progress bar
            for post in tqdm(posts, desc=f"Page {page}", unit="post"):
                current_hash = post.get_id()

                if last_hash and current_hash == last_hash:
                    tqdm.write(f"\n> Reached previous hash: {post.title}. Stopping.")
                    tqdm.write(f"> Total new posts: {self.new_posts_count}")
                    
                    if has_new_posts and new_latest_hash:
                        with open(self.latest_file, 'w', encoding='utf-8') as f:
                            f.write(new_latest_hash)
                        print("> Latest hash updated.")
                    else:
                        print("> No new posts.")
                    return

                if new_latest_hash is None:
                    new_latest_hash = current_hash

                tqdm.write(f"> [NEW] {post.title[:25]}... ({post.author_raw})")
                content = self.process_content(post)
                self.save_markdown(post, content)
                has_new_posts = True

            page += 1

        if has_new_posts and new_latest_hash:
            with open(self.latest_file, 'w', encoding='utf-8') as f:
                f.write(new_latest_hash)
            print(f"\n> Full scrape complete. New posts: {self.new_posts_count}")

if __name__ == "__main__":
    BlogScraper().run()