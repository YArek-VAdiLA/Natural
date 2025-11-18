from aiogram import Router, F, types


def register_fallback_handlers(router: Router):
    @router.message(
        ~F.text & ~F.voice & ~F.photo
    )
    async def fallback_handler(message: types.Message):
        await message.answer(
            "Я тебя не совсем понял \n"
            "Можешь задать вопрос по питанию, отправить голосовое или фото еды."
        )
