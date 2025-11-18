FUNCTIONS = [
    {
        "name": "save_target",
        "description": "Сохраняет цель пользователя (похудение, набор массы, поддержание веса).",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "Цель пользователя, сформулированная в одном коротком предложении."
                }
            },
            "required": ["goal"]
        }
    }
]
