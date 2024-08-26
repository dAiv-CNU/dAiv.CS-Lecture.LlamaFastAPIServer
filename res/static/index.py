from typing import Iterable
from browser import bind, document, websocket
from browser.widgets.dialog import InfoDialog


def on_open(evt):
    document['sendbtn'].disabled = False
    document['closebtn'].disabled = False
    document['openbtn'].disabled = True
    InfoDialog("websocket", f"Connection open")


def on_message(evt):
    # message received from server
    InfoDialog("websocket", f"Message received : {evt.data}")


def on_close(evt):
    # websocket is closed
    InfoDialog("websocket", "Connection is closed")
    document['openbtn'].disabled = False
    document['closebtn'].disabled = True
    document['sendbtn'].disabled = True


ws = None


@bind('#openbtn', 'click')
def _open(ev):
    if not websocket.supported:
        InfoDialog("websocket", "WebSocket is not supported by your browser")
        return
    global ws
    # open a web socket
    ws = websocket.WebSocket("wss://echo.websocket.events")
    # bind functions to web socket events
    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)


@bind('#sendbtn', 'click')
def send(ev):
    data = document["data"].value
    if data:
        ws.send(data)


@bind('#closebtn', 'click')
def close_connection(ev):
    ws.close()
    document['openbtn'].disabled = False



class ChatHistory(list):
    """ Chat history class """

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

    def extend(self, history: Iterable):
        for item in history:
            try:
                self.append(**item)
            except TypeError:
                self.append(**item.dict())

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
