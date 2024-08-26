from typing import Iterable

system_prompt = "" \
    + "You are a helpful, smart, kind, and efficient AI Assistant. " \
    + "You always fulfill the user's requests to the best of your ability. " \
    + "Please answer in Korean language."


class ChatHistory(list):
    """ Chat history class """

    '''def __init__(self, initial_data: Iterable[dict] = [{'role':"system", 'content':system_prompt}]):
        """ Initialize the chat history with optional initial data. """
        if initial_data is None:
            super().__init__()
        else:
            if not all(isinstance(item, dict) and 'role' in item and 'content' in item for item in initial_data):
                raise ValueError("Initial data must be a list of dictionaries with 'role' and 'content' keys")
            super().__init__(initial_data)'''
    def append(self, role: str | Iterable[str], content: str | Iterable[str]):
        if isinstance(content, str):
            if isinstance(role, str):
                super().append({'role': role, 'content': content})
            else:
                raise ValueError("Role must be a string when content is a string")
        else:
            if isinstance(role, str):
                role = [role for _ in content]
            for r, c in zip(role, content):
                super().append({'role': r, 'content': c})

    def create_prompt(self, system_prompt: str, user_prompt: str = ""):
        return [
            {
                'role': "system",
                'content': system_prompt
            },
            *self,
            {
                'role': "user",
                'content': user_prompt
            }
        ]
