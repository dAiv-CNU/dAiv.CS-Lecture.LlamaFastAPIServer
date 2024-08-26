
import os
from urllib.request import Request

from pydantic import BaseModel

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
SSL_KEYFILE = os.path.join(BASE_DIR, "../../certs/localhost.key")
SSL_CERTFILE = os.path.join(BASE_DIR, "../../certs/localhost.crt")


class Message(BaseModel):
    message: str


clients_histories = dict()


def get_recommendation(data):
    k = ""
    tokens, print_prompt = llama3.chat(chat_history, data)
    for token in llama3.token_streamer(tokens, print_prompt):
        k += token
    return k


@app.get("/chat")
async def chat():
    return chat_history


@app.post("/chat_response/")
async def chat_response(message: str):
    # 요청된 대화를 받아서 특정 응답을 생성
    response = get_recommendation(message)
    chat_history.append('Answer', response)
    return chat_history
    # 간단한 응답 로직 (실제 로직을 더 복잡하게 작성할 수 있음)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client: {data}"
            await manager.broadcast(message)

            server_response = f'response : {get_recommendation(data)}'
            chat_history.append('Answer', server_response[10:])
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
                var ws = new WebSocket(`wss://127.0.0.1:8000/ws/${client_id}`);

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
                    var content = document.createTextNode(input.value)  // content 변수를 여기서 정의
                
                    ws.send(input.value)  // 서버로 메시지 전송
                
                    
                
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
        ssl_certfile = SSL_CERTFILE,  # Add SSL certificate file
        ssl_keyfile = SSL_KEYFILE,

    )
