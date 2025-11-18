import base64
import json
from io import BytesIO
from typing import Optional, Dict, Any

from openai import AsyncOpenAI

from app.config import settings
from app.domain.interfaces import AIProvider


class ChatResponse:
    def __init__(
        self,
        output_text: Optional[str] = None,
        is_function_call: bool = False,
        function_name: Optional[str] = None,
        function_args: Optional[Dict[str, Any]] = None,
    ):
        self.output_text = output_text or ""
        self.is_function_call = is_function_call
        self.function_name = function_name
        self.function_args = function_args or {}


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe_voice(self, audio_bytes: BytesIO) -> str:
        if not getattr(audio_bytes, "name", None):
            audio_bytes.name = "voice.ogg"

        audio_bytes.seek(0)

        resp = await self._client.audio.transcriptions.create(
            model=settings.whisper_model,
            file=audio_bytes,
        )

        return resp.text or ""

    async def tts(self, text: str) -> bytes:
        speech = await self._client.audio.speech.create(
            model=settings.tts_model,
            voice=settings.tts_voice,
            input=text,
        )

        audio_buf = speech.read()
        print("tts() returned type:", type(audio_buf))

        if isinstance(audio_buf, BytesIO):
            audio_bytes = audio_buf.getvalue()
        elif isinstance(audio_buf, (bytes, bytearray)):
            audio_bytes = audio_buf
        else:
            audio_bytes = bytes(audio_buf)

        return audio_bytes

    async def chat(self, messages: list, functions: list | None = None) -> ChatResponse:
        params = {
            "model": settings.openai_model,
            "messages": messages,
        }

        if functions:
            params["tools"] = functions
            params["tool_choice"] = "auto"

        resp = await self._client.chat.completions.create(**params)

        msg = resp.choices[0].message

        if msg.tool_calls:
            call = msg.tool_calls[0]

            return ChatResponse(
                is_function_call=True,
                function_name=call.function.name,
                function_args=json.loads(call.function.arguments),
            )

        return ChatResponse(output_text=msg.content or "")

    async def recognize_photo(self, image_bytes: bytes, system_prompt: str) -> str:
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        resp = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проанализируй это фото еды."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}"
                            },
                        },
                    ],
                },
            ],
        )

        return resp.choices[0].message.content.strip()

    async def ask_goal_assistant(self, user_text: str, current_goal: Optional[str] = None) -> Dict[str, Any]:

        system_prompt = (
            "Ты ассистент по определению фитнес-целей.\n"
            "Твоя задача — определить, говорит ли пользователь о своей цели:\n"
            "- похудеть\n"
            "- набрать вес\n"
            "- поддерживать форму\n"
            "- улучшить здоровье\n"
            "- увеличить мышечную массу\n"
            "- снизить жир\n"
            "\n"
            "Если ВЫРАЖЕНА НОВАЯ ЦЕЛЬ — вызывай save_target(goal).\n"
            "goal должно быть короткой фразой, например: 'похудеть на 5 кг'.\n"
            "\n"
            "Если в сообщении НЕТ цели — НЕ вызывай функцию.\n"
            "Тогда просто верни текстовый ответ: '' (пустую строку).\n"
            "Никакой выдумки — только явные цели в сообщении."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "save_target",
                    "description": "Сохранить фитнес-цель",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goal": {"type": "string"},
                        },
                        "required": ["goal"],
                    },
                },
            }
        ]

        messages = [{"role": "system", "content": system_prompt}]

        if current_goal:
            messages.append({
                "role": "system",
                "content": f"Текущая цель пользователя: {current_goal}",
            })

        messages.append({"role": "user", "content": user_text})

        resp = await self._client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        msg = resp.choices[0].message

        if not msg.tool_calls:
            return {
                "text": msg.content or "",
                "is_function_call": False,
            }

        call = msg.tool_calls[0]
        try:
            args = json.loads(call.function.arguments)
        except:
            args = {"goal": call.function.arguments}

        return {
            "text": None,
            "is_function_call": True,
            "function_name": call.function.name,
            "function_args": args,
        }

