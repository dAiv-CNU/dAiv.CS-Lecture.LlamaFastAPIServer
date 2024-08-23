from typing import List
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from model import llama3
from ws.manager import ConnectionManager
from model.llama3 import ChatHistory

chat_history = ChatHistory()
manager = ConnectionManager()
token_streamer = llama3.token_streamer
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSL_KEYFILE = os.path.join(BASE_DIR, "../../certs/private.key")
SSL_CERTFILE = os.path.join(BASE_DIR, "../../certs/certificate.crt")
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    def get_recommendation():
        k = ""
        tokens, print_prompt = llama3.chat(chat_history, data)
        for token in llama3.token_streamer(tokens, print_prompt):
            k += token
        return k
    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client: {data}"
            await manager.broadcast(message)

            server_response = f'response : {get_recommendation()}'
            chat_history.append('Answer',server_response[10:])
            await manager.send_personal_message(server_response, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@app.get("/")
async def get():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>gpt 도전기</h1>
            <form id="form">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id="messages"></ul>
            <script>
                var client_id = Date.now()
                var ws = new WebSocket(`wss://localhost:8000/ws/${client_id}`);

                // 메시지를 수신하여 화면에 출력
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };

                // 폼 제출 시 메시지를 전송하고, 화면에 출력
                var form = document.getElementById('form')
                form.addEventListener('submit', function(event) {
                    event.preventDefault()
                    var input = document.getElementById("messageText")
                    ws.send(input.value)  // 서버로 메시지 전송

                    // 보낸 메시지를 화면에 바로 출력
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    message.appendChild(content)
                    messages.appendChild(message)

                    input.value = ''  // 입력란 초기화
                })
            </script>
        </body>
    </html>
    """)


if __name__ == '__main__':
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        ssl_keyfile=SSL_KEYFILE,
        ssl_certfile=SSL_CERTFILE
    )
