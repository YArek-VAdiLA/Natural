from __future__ import annotations

from typing import Optional

from app.domain.entities import NutritionAnswer, PhotoAnalysisResult, UserEntity
from app.domain.interfaces import AIProvider


class NutritionService:

    def __init__(self, ai_provider: AIProvider, doc_knowledge: str):
        self._ai = ai_provider
        self._doc = doc_knowledge or ""

    async def answer_text(
        self,
        text: str,
        user: Optional[UserEntity] = None,
    ) -> NutritionAnswer:
        user_goal_part = (
            f" Цель пользователя: {user.goal}."
            if user and user.goal
            else ""
        )

        system_prompt = (
            "Ты — эксперт по питанию.\n"
            "Отвечай строго на основе предоставленного ниже документа.\n"
            "Нельзя придумывать факты, которых нет в документе.\n"
            "Если в документе нет нужной информации, то ответь основываясь на своих знаниях. "
            "'ТЫ НЕ ДОЛЖЕН ОТВЕЧАТЬ НА ТЕМЫ НЕ СВЯЗАНЫЕ С ЗДОРОВЫМ ОБРОЗОМ ЖИЗНИ.'\n"
            f"{user_goal_part}\n\n"
            f"Документ:\n{self._doc}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]

        resp = await self._ai.chat(messages)

        if resp.is_function_call:
            return NutritionAnswer(
                text="",
                is_function_call=True,
                function_name=resp.function_name,
                function_args=resp.function_args,
            )

        reply_text = (resp.output_text or "").strip()

        if not self._doc.strip():
            if not reply_text:
                reply_text = (
                    "Сейчас у меня нет загруженного документа с советами по питанию, "
                    "поэтому я не могу ответить строго по нему."
                )

        return NutritionAnswer(
            text=reply_text,
            is_function_call=False,
        )

    async def answer_voice(
        self,
        transcript: str,
        user: Optional[UserEntity] = None,
    ) -> NutritionAnswer:

        return await self.answer_text(transcript, user=user)

    async def analyze_photo(self, image_bytes: bytes) -> PhotoAnalysisResult:
        system_prompt = (
            "Ты — эксперт мирового уровня по нутрициологии и анализу изображений еды. "
            "Работай с минимальной погрешностью.\n\n"
            "Задача: определить ВСЕ продукты на фото, оценить массу каждого (в граммах) "
            "и примерную калорийность.\n\n"
            "Формат ответа:\n"
            "Название продукта: X г (оценка), Y ккал.\n"
            "...\n"
            "ИТОГО: Z ккал."
        )

        text = await self._ai.recognize_photo(
            image_bytes=image_bytes,
            system_prompt=system_prompt,
        )

        return PhotoAnalysisResult(text=text)
