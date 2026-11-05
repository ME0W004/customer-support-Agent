import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic_ai import Agent
from app.config import settings
from app.ai.schemas import AgentReply
from app.db import get_knowledge_base_section, list_knowledge_base_sections

logger = logging.getLogger(__name__)

os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

SUPPORT_AGENT_PROMPT = """
شما «دستیار هوشمند پشتیبانی مشتریان شرکت ابریار (CloudYar)» هستید؛ ارائه‌دهنده پلتفرم یکپارچه ابری مدیریت پروژه‌ها، اتوماسیون فرآیندها و CRM سازمانی.
پاسخ‌های شما باید کاملاً محترمانه، گرم، مسلط، فنی، و به زبان فارسی روان، سلیس و ساختاریافته تدوین شوند.

قوانین حیاتی:
1. استناد به پایگاه دانش (Grounding in Knowledge Base):
   برای پاسخ دادن به هر سوال درباره پلن‌های اشتراک (Starter, Pro, Enterprise)، قیمت‌ها، تخفیف‌های سالانه، سهمیه API، امکانات اتوماسیون و وب‌هوک، شرایط فعال‌سازی، صدور فاکتور رسمی سامانه مودیان، استرداد وجه ۱۴ روزه، موافقت‌نامه سطح خدمات (SLA)، بک‌آپ‌گیری و رفع خطاهای فنی، حتماً از ابزار `fetch_knowledge_base` استفاده کنید و متن مستندات را بخوانید.
   هرگز از خود قیمت، تخفیف، عدد، یا قانون نسازید؛ اطلاعات باید دقیقاً منطبق بر پایگاه دانش ابریار باشد.

2. ارجاع به کارشناس انسان (Escalation Policy):
   در شرایط زیر باید حتماً پرچم `escalate_to_human=True` تنظیم شود و در فیلد `escalation_reason` علت آن شفاف نوشته شود:
   - درخواست عودت وجه یا استرداد وجه (Refund) یا ارسال شماره شبا برای تسویه حساب مالی.
   - درخواست صدور فاکتور رسمی مالیاتی با شناسه مودیان یا فاکتور حقوقی مهرشده شرکتی.
   - گزارش قطعی حاد و سراسری سرورها (P0 Outage) یا اختلال امنیتی بحرانی.
   - درخواست انتقال مالکیت حساب کاربری سازمان یا بازنشانی اضطراری احراز هویت دو مرحله‌ای (2FA).
   نکته مهم: حتی در صورت نیاز به ارجاع، در متن پاسخ به کاربر اطمینان و آرامش خاطر دهید، روند کار را شفاف توضیح دهید و اعلام فرمایید که پرونده به واحد مربوطه (مالی/فنی) ارجاع شده و پیگیری می‌شود.

3. ساختار و لحن پاسخ:
   - با درود رسمی و محترمانه شروع کنید (مثال: «درود بر شما کاربر گرامی ابریار» یا «سلام وقت شما بخیر»).
   - پاسخ دقیق سوال را به شکل شفاف، روشن و با استفاده از بولت‌پوینت بیان کنید.
   - با آرزوی موفقیت و عبارت احترام‌آمیز و امضای رسمی «تیم پشتیبانی ابریار» به پایان برسانید.
"""

support_agent = Agent(
    model="google:gemini-3.1-flash-lite",
    output_type=AgentReply,
    system_prompt=SUPPORT_AGENT_PROMPT
)


@support_agent.tool_plain
def fetch_knowledge_base(slug: str) -> str:
    """
    دریافت متن کامل مستندات یک بخش از پایگاه دانش.
    اسلاگ‌های معتبر: products, shipping, returns, warranty, faq
    """
    content = get_knowledge_base_section(slug)
    if content:
        return content
    return f"مستنداتی برای اسلاگ '{slug}' یافت نشد."


@support_agent.tool_plain
def list_available_topics() -> str:
    """لیست موضوعات و بخش‌های موجود در پایگاه دانش."""
    sections = list_knowledge_base_sections()
    if not sections:
        return "هیچ بخشی در پایگاه دانش ثبت نشده است."
    lines = [f"- {s['slug']}: {s['title']}" for s in sections]
    return "\n".join(lines)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    reraise=True
)
def answer_customer_email(
    customer_email: str,
    subject: str,
    body: str,
    category: str = "general",
    thread_history: str = ""
) -> AgentReply:
    """Generates a structured reply to the customer using Pydantic AI and KB tools with retries."""
    prompt = f"""
اطلاعات ایمیل ورودی مشتری:
- فرستنده: {customer_email}
- موضوع: {subject}
- دسته‌بندی احتمالی: {category}

متن ایمیل مشتری:
{body}
"""
    if thread_history:
        prompt += f"\n\nتاریخچه پیام‌های قبلی در این گفتگو:\n{thread_history}"

    result = support_agent.run_sync(prompt)
    return result.output
