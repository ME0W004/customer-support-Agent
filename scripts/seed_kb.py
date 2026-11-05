import sys
from pathlib import Path

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from app.db import upsert_knowledge_base_section, list_knowledge_base_sections

SECTIONS = [
    {
        "slug": "products",
        "title": "CloudScale AI Subscription Plans, Features & Add-ons",
        "file": "products.md"
    },
    {
        "slug": "shipping",
        "title": "Digital Provisioning, Billing & Tax Invoicing",
        "file": "shipping.md"
    },
    {
        "slug": "returns",
        "title": "14-Day Money-Back Guarantee, Refunds & Cancellation",
        "file": "returns.md"
    },
    {
        "slug": "warranty",
        "title": "Service Level Agreement (SLA), Security & Uptime Commitment",
        "file": "warranty.md"
    },
    {
        "slug": "faq",
        "title": "Developer FAQs, API Key Management & Troubleshooting",
        "file": "faq.md"
    }
]

def main():
    base_dir = Path("app/knowledge_base/sections")
    print("Seeding Knowledge Base for CloudScale AI (International Version) into Supabase...")
    
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
