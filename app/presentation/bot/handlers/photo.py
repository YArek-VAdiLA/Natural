from aiogram import Router, types
from io import BytesIO
from aiogram.types import Message

from app.application.nutrition_service import NutritionService
from app.domain.interfaces import AIProvider


def register_photo_handlers(
    router: Router,
    nutrition_service: NutritionService,
    ai_provider: AIProvider,
):
    @router.message(lambda m: m.photo is not None)
    async def photo_handler(message: Message):
        try:
            photo = message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)

            buf = BytesIO()
            await message.bot.download_file(file_info.file_path, buf)
            buf.seek(0)

            image_bytes = buf.read()

            result = await nutrition_service.analyze_photo(image_bytes)

            await message.answer(result.text)
        except Exception as e:
            await message.answer(f" Ошибка при распознавании фото: {type(e).__name__}: {e}")
