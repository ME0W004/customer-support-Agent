import sys
from pathlib import Path

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from app.db import upsert_knowledge_base_section, list_knowledge_base_sections

SECTIONS = [
    {
        "slug": "products",
        "title": "راهنمای پلن‌های اشتراک، امکانات و مشخصات فنی ابریار",
        "file": "products.md"
    },
    {
        "slug": "shipping",
        "title": "فعال‌سازی سرویس، تحویل آنی لایسنس و صدور صورت‌حساب رسمی",
        "file": "shipping.md"
    },
    {
        "slug": "returns",
        "title": "ضمانت بازگشت وجه ۱۴ روزه و قوانین لغو اشتراک",
        "file": "returns.md"
    },
    {
        "slug": "warranty",
        "title": "موافقت‌نامه سطح خدمات (SLA)، پایداری و امنیت داده‌ها",
        "file": "warranty.md"
    },
    {
        "slug": "faq",
        "title": "پرسش‌های متداول، راهنمای API و رفع اشکال حساب کاربری",
        "file": "faq.md"
    }
]

def main():
    base_dir = Path("app/knowledge_base/sections")
    print("Seeding Knowledge Base for CloudYar (ابریار) into Supabase...")
    
    for sec in SECTIONS:
        file_path = base_dir / sec["file"]
        if not file_path.exists():
            print(f"Warning: File {file_path} not found!")
            continue
        content = file_path.read_text(encoding="utf-8")
        upsert_knowledge_base_section(
            slug=sec["slug"],
            title=sec["title"],
            content=content
        )
        print(f"  [+] Seeded: {sec['slug']} -> {sec['title']}")

    total = list_knowledge_base_sections()
    print(f"\nDone! Total knowledge base articles in Supabase: {len(total)}")

if __name__ == "__main__":
    main()
