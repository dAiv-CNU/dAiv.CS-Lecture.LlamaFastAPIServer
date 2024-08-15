from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import model
import uvicorn

app = FastAPI()

system_prompt = "You are a helpful, smart, kind, and efficient AI Assistant. You always fulfill the user's requests to the best of your ability. You need to keep listen to the conversations. Please answer in Korean language."


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    def get_recommendation():
        k = ''
        for chunk in model.llama3(system_prompt, data):
            k +=model.token_stream(chunk)
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


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="C:/Users/com/private.key",
        ssl_certfile="C:/Users/com/certificate.crt"
    )
