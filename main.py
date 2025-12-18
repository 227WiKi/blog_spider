from dotenv import load_dotenv
from scraper import BlogScraper

if __name__ == "__main__":
    load_dotenv()
    
    scraper = BlogScraper()
    scraper.run()