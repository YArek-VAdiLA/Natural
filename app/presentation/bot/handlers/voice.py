from io import BytesIO
from aiogram import Router
from aiogram.types import Message, BufferedInputFile
import traceback


def register_voice_handlers(
    router: Router,
    nutrition_service,
    user_service,
    ai_provider,
    goal_service,
):
    @router.message(lambda m: m.voice is not None)
    async def voice_handler(message: Message):
        try:
            telegram_id = str(message.from_user.id)

            # --- 1. Получаем файл голосового ---
            voice = message.voice
            file_info = await message.bot.get_file(voice.file_id)

            # Aiogram 3: bot.download(file_info) -> BytesIO-like object
            downloaded = await message.bot.download(file_info)
            file_bytes = downloaded.read()   # bytes

            if not file_bytes:
                await message.answer("Не смог скачать голосовое 😔")
                return

            # --- 2. Заворачиваем в BytesIO для Whisper ---
            audio_buf = BytesIO(file_bytes)
            audio_buf.name = "voice.ogg"
            audio_buf.seek(0)

            # --- 3. Распознаём речь ---
            transcript = await ai_provider.transcribe_voice(audio_buf)
            transcript = (transcript or "").strip()
            if not transcript:
                await message.answer("Не удалось распознать речь 😔")
                return

            # --- 4. Пользователь ---
            user = await user_service.get_or_create_user(telegram_id)

            # --- 5. Проверяем, не нужно ли обновить цель ---
            goal_resp = await goal_service.process_text(transcript, user)
            if goal_resp and goal_resp.is_function_call:
                ok = await goal_service.handle_function_call(goal_resp, user)
                await message.answer(
                    " Цель обновлена!" if ok else "Не удалось сохранить цель "
                )
                return

            answer = await nutrition_service.answer_voice(transcript, user)

            tts_bytes = await ai_provider.tts(answer.text)

            if not isinstance(tts_bytes, (bytes, bytearray)):
                await message.answer(" Ошибка: аудио от TTS в неверном формате.")
                return

            voice_file = BufferedInputFile(tts_bytes, filename="reply.mp3")

            await message.answer_voice(voice_file)
            if answer.text:
                await message.answer(answer.text)

        except Exception as e:
            traceback.print_exc()
            await message.answer(
                f" Ошибка обработки сообщения: {type(e).__name__}: {e}"
            )
