from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from model import llama3
from socket.manager import ConnectionManager


manager = ConnectionManager()
token_streamer = llama3.token_streamer
app = FastAPI()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    def get_recommendation():
        k = ''
        for chunk in token_streamer(*llama3.chat(, data)):
            k += model.token_stream(chunk)
        return k
    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client: {data}"
            await manager.broadcast(message)

            server_response = f'response : {get_recommendation()}'
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
        ssl_keyfile="./res/cert/private.key",
        ssl_certfile="./res/cert/certificate.crt"
    )
