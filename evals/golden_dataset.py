from dataclasses import dataclass
from typing import Literal

@dataclass
class TestCase:
    id: str
    subject: str
    body: str
    expected_section: str
    expected_action: Literal["reply", "escalate", "skip"]
    expected_is_support: bool


GOLDEN_EMAILS: list[TestCase] = [
    # 1. Product & Plan Inquiries (Starter, Pro, Enterprise)
    TestCase(
        id="case_1_plan_comparison_pro_vs_starter",
        subject="مقایسه پلن استارتر و پرو",
        body="سلام وقت بخیر، شرکت ما ۵ نفر پرسنل دارد. تفاوت سهمیه API و فضای ابری بین پلن استارتر و پرو چیست و آیا امکان تست وجود دارد؟",
        expected_section="products",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_2_add_ons_pricing",
        subject="هزینه کاربر اضافه و حجم مازاد",
        body="درود، ما اشتراک پلن Pro داریم اما می‌خواهیم ۳ کاربر جدید اضافه کنیم و ۵۰ گیگابایت فضای بیشتر لازم داریم. تعرفه افزودنی‌ها چقدر است؟",
        expected_section="products",
        expected_action="reply",
        expected_is_support=True
    ),
    
    # 2. Billing & License Activation
    TestCase(
        id="case_3_license_activation_time",
        subject="نحوه دریافت لایسنس و کلید API بعد از خرید",
        body="سلام، اگر پلن سالانه رو آنلاین پرداخت کنم چقدر طول میکشه تا لایسنس فعال بشه و به دسترسی دست پیدا کنم؟",
        expected_section="shipping",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_4_tax_invoice_human_escalation",
        subject="درخواست صدور فاکتور رسمی مودیان فاکتور ۷۸۲۱",
        body="سلام و احترام، ما اشتراک سازمانی خریدیم و نیاز به ثبت فاکتور در کارپوشه سامانه مودیان داریم. شناسه ملی شرکت: ۱۰۱۰۱۲۳۴۵۶۷ و کد اقتصادی: ۴۱۱۳۹۸۷۶۵۴۳۲. لطفا فاکتور رسمی را صادر فرمایید.",
        expected_section="shipping",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 3. Refunds & Cancellation
    TestCase(
        id="case_5_14_day_refund_policy",
        subject="شرایط ضمانت بازگشت وجه ۱۴ روزه",
        body="سلام، اگر اشتراک یکساله ابریار رو خریداری کنیم و بعد از ۱۰ روز متوجه بشیم نرم‌افزار برای شرکت مناسب نیست، آیا کل پول عودت داده میشه؟",
        expected_section="returns",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_6_refund_request_human_escalation",
        subject="درخواست عودت وجه اشتراک فاکتور ۵۵۴۰",
        body="سلام، من ۵ روز پیش پلن پرو خریدم ولی به دلیل لغو پروژه می‌خواهم اشتراک را کنسل کنم. شماره شبا جهت استرداد وجه: IR980120000000012345678901 به نام شرکت داده‌پردازان. لطفا مبلغ را برگردانید.",
        expected_section="returns",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 4. SLA, Uptime & Server Issues
    TestCase(
        id="case_7_uptime_sla_and_backup",
        subject="تعهد آپ‌تایم و وضعیت بک‌آپ‌گیری داده‌ها",
        body="سلام، آیا دیتابیس ما به صورت منظم بک‌آپ گرفته می‌شود و تضمین آپ‌تایم شبکه ابریار در ماه چقدر است؟",
        expected_section="warranty",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_8_critical_server_down_outage",
        subject="قطعی کامل دسترسی به پنل و خطای 502",
        body="فوری: از نیم ساعت پیش کل پرسنل شرکت ما نمی‌توانند وارد پنل ابریار شوند و خطای 502 Bad Gateway دریافت می‌کنیم! کار متوقف شده لطفا سریعا پیگیری کنید.",
        expected_section="warranty",
        expected_action="escalate",
        expected_is_support=True
    ),

    # 5. Technical FAQ & API
    TestCase(
        id="case_9_api_rate_limit_429",
        subject="خطای 429 Too Many Requests در وب‌سرویس",
        body="سلام، در حین ارسال داده به API ابریار خطای ۴۲۹ دریافت کردیم. علت این خطا چیست و چه راهکاری برای افزایش سهمیه داریم؟",
        expected_section="faq",
        expected_action="reply",
        expected_is_support=True
    ),
    TestCase(
        id="case_10_migration_from_trello",
        subject="انتقال پروژه‌ها از ترلو و اکسل",
        body="سلام، آیا امکان وارد کردن تسک‌ها و فایل‌های اکسل و بردهای ترلو به صورت مستقیم در ابریار وجود داره؟",
        expected_section="faq",
        expected_action="reply",
        expected_is_support=True
    ),

    # 6. Negative / Spam / Irrelevant
    TestCase(
        id="case_11_spam_promotional",
        subject="پیشنهاد ویژه افزایش بازدید سایت شما",
        body="سلام مدیر محترم، شرکت ما پکیج ویژه تبلیغات گوگل و رپورتاژ آگهی با ۶۰ درصد تخفیف ویژه دارد. برای اطلاعات بیشتر تماس بگیرید.",
        expected_section="irrelevant",
        expected_action="skip",
        expected_is_support=False
    ),
    TestCase(
        id="case_12_furious_customer_escalation",
        subject="شکایت شدید از مدیریت و تهدید به پیگیری حقوقی",
        body="واقعا برای تیم شما متاسفم! الان دو روزه مشکل ما بلاتکلیف مونده و هیچکس جواب نمیده. اگر تا ۲ ساعت دیگه مدیر ارشد شما تماس نگیره قرارداد را فسخ کرده و موضوع را از صنف پیگیری می‌کنیم!",
        expected_section="general",
        expected_action="escalate",
        expected_is_support=True
    )
]
