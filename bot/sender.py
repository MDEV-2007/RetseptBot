import logging

logger = logging.getLogger(__name__)


async def send_prescription_document(
    token: str,
    recipient,          # @username (str) yoki numeric chat_id (int)
    pdf_bytes: bytes,
    prescription_number: str,
    patient_name: str,
    description: str = "",
) -> None:
    """Send a prescription PDF via Telegram Bot API.

    recipient can be:
      - "@username"  — public Telegram username
      - 123456789   — numeric chat ID
    """
    try:
        from aiogram import Bot
        from aiogram.types import BufferedInputFile
    except ImportError as exc:
        raise RuntimeError("aiogram is not installed. Run: pip install aiogram") from exc

    # Normalize: "@username" yoki int
    if isinstance(recipient, str):
        r = recipient.strip()
        if r.lstrip('-').isdigit():
            chat_id = int(r)
        else:
            chat_id = r if r.startswith('@') else f'@{r}'
    else:
        chat_id = recipient

    caption = f"📋 *Prescription {prescription_number}*\n👤 Patient: {patient_name}"
    if description:
        caption += f"\n\n📝 {description}"

    bot = Bot(token=token)
    try:
        document = BufferedInputFile(
            pdf_bytes,
            filename=f"prescription_{prescription_number}.pdf",
        )
        await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode="Markdown",
        )
        logger.info("Prescription %s sent to %s", prescription_number, chat_id)
    finally:
        await bot.session.close()
