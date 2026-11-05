import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic_ai import Agent
from app.config import settings
from app.ai.schemas import Classification

logger = logging.getLogger(__name__)

os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

CLASSIFIER_SYSTEM_PROMPT = """
شما یک سیستم هوشمند دسته‌بندی ایمیل‌های ورودی پشتیبانی مشتریان شرکت نرم‌افزاری ابری «ابریار» (CloudYar) هستید.
وظیفه شما این است که موضوع و متن ایمیل دریافتی را تحلیل کرده و اطلاعات ساختاریافته زیر را استخراج کنید:

1. section: بخش مرتبط از پایگاه دانش:
   - products: سوالات پیرامون پلن‌های اشتراک (Starter, Pro, Enterprise)، قیمت‌ها، قابلیت‌ها، سهمیه API، امکانات اتوماسیون، ماژول CRM و بسته‌های افزودنی.
   - shipping: فعال‌سازی آنی لایسنس، روش‌های پرداخت آنلاین/پایا، دریافت صورت‌حساب، صدور فاکتور رسمی مالیاتی سامانه مودیان و چرخه تمدید اشتراک.
   - returns: درخواست استرداد و عودت وجه، ضمانت بازگشت پول ۱۴ روزه، لغو اشتراک و تسویه‌حساب دوره‌های سالانه.
   - warranty: توافق‌نامه سطح خدمات (SLA)، تضمین پایداری و آپ‌تایم ۹۹.۹٪، جبران خسارت قطعی، پشتیبان‌گیری منظم دیتابیس و امنیت اطلاعات.
   - faq: سوالات متداول فنی، کلید API و خطای 429، تنظیم وب‌هوک، درون‌ریزی داده‌ها (Migration)، بازیابی اکانت، احراز هویت دومرحله‌ای (2FA) و ساعات کاری.
   - general: مواردی که به پشتیبانی ربط دارد اما بخش اختصاصی مشخصی در پایگاه دانش ندارد.
   - irrelevant: ایمیل‌های اسپم، تبلیغاتی، بازاریابی، پیام‌های تست نامفهوم یا بی‌ربط.

2. is_support_request:
   اگر ایمیل یک پیام واقعی از سمت مشتری است true، اگر اسپم، پیام تست بی‌معنی یا تبلیغات است false.

3. customer_sentiment:
   لحن مشتری: satisfied (راضی/تشکر), neutral (معمولی/خنثی), confused (سردرگم/سوالی), angry (عصبانی/ناراضی), urgent (فوری).

4. summary:
   خلاصه کوتاه ۱ خطی به زبان فارسی از خواسته مشتری.
"""

classifier_agent = Agent(
    model="google:gemini-3.1-flash-lite",
    output_type=Classification,
    system_prompt=CLASSIFIER_SYSTEM_PROMPT
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    reraise=True
)
def classify_email(subject: str, body: str) -> Classification:
    """Classifies an incoming customer email with automatic retry on temporary errors."""
    user_prompt = f"موضوع ایمیل: {subject}\n\nمتن ایمیل:\n{body}"
    result = classifier_agent.run_sync(user_prompt)
    return result.output
