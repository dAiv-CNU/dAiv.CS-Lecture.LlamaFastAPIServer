
import ssl

import websockets
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



class Message(BaseModel):
    message: str


clients_histories = dict()

'''def get_recommendation(client_id,data):
    k = ""
    tokens, print_prompt = llama3.chat(clients_histories[client_id], data)
    for token in llama3.token_streamer(tokens, print_prompt):
        k += token
    return k'''


def get_recommendation(data):
    k = ""
    tokens, print_prompt = llama3.chat(chat_history, data)
    for token in llama3.token_streamer(tokens, print_prompt):
        k += token
    return k


@app.get("/client")
async def root():
    return clients_histories


@app.get("/chat")
async def chat():
    return chat_history

@app.post("/practice")
async def practice(data:str):
    uri = f"ws://localhost:8000/ws/156"
    async with websockets.connect(uri) as websocket:
        await websocket.send(data)
        answer = await websocket.recv()
        return answer




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
    '''
    chat_history.clear()
    try:
        print(clients_histories[client_id])
    except:
        clients_histories[client_id] = chat_history
        '''
    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client: {data}"
            await manager.broadcast(message)
            server_response = f'response : {get_recommendation(data)}'
            chat_history.append('Answer', server_response[10:])
            #await manager.send_personal_message(server_response, websocket)
            await manager.broadcast(server_response)
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
            <!-- Bootstrap CSS 추가 -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <!-- Font Awesome 아이콘 추가 -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
            <!-- Custom CSS 추가 -->
            <style>
                body {
                    background-color: #f4f6f9;
                    font-family: 'Arial', sans-serif;
                }
                .chat-container {
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
                    border: 1px solid #ddd;
                }
                h1 {
                    font-size: 28px;
                    margin-bottom: 20px;
                    color: #333;
                    text-align: center;
                }
                #messages {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                    height: 400px;
                    overflow-y: auto;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }
                #messages li {
                    padding: 12px 15px;
                    border-radius: 15px;
                    margin-bottom: 10px;
                    max-width: 80%;
                    word-wrap: break-word;
                    display: inline-block;
                    clear: both;
                }
                .message-client {
                    background-color: #e1f5fe;
                    color: #0277bd;
                    text-align: left;
                    margin-left: auto;
                    border: 1px solid #b3e5fc;
                    border-radius: 15px;
                    float: right;
                }
                .message-server {
                    background-color: #ffe0b2;
                    color: #e65100;
                    text-align: left;
                    border: 1px solid #ffcc80;
                    border-radius: 15px;
                    float: left;
                }
                .form-inline {
                    display: flex;
                    align-items: center;
                    margin-top: 20px;
                }
                .form-control {
                    border-radius: 25px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    box-shadow: none;
                }
                .form-control:focus {
                    border-color: #0277bd;
                    box-shadow: 0 0 0 0.2rem rgba(2, 119, 189, 0.25);
                }
                .btn-primary {
                    border-radius: 25px;
                    padding: 10px 20px;
                }
            </style>
        </head>
        <body>
            <div class="container chat-container">
                <h1 class="mb-4">GPT 도전기</h1>
                <ul id="messages"></ul>
                <form id="form" class="form-inline">
                    <input type="text" id="messageText" class="form-control mr-2" autocomplete="off" placeholder="Type your message here..."/>
                    <button type="submit" class="btn btn-primary">Send</button>
                </form>
            </div>
            <script>
                // 클라이언트 ID를 현재 시간으로 생성
                var client_id = Date.now();

                // WebSocket URL을 템플릿 리터럴을 사용하여 생성
                var ws = new WebSocket(`wss://127.0.0.1:8000/ws/${client_id}`);

                // 메시지를 수신하여 화면에 출력
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages');
                    var message = document.createElement('li');
                    message.className = 'message message-server';
                    message.textContent = event.data;
                    messages.appendChild(message);
                    messages.scrollTop = messages.scrollHeight;
                };

                // 폼 제출 시 메시지를 전송하고, 화면에 출력
                var form = document.getElementById('form');
                form.addEventListener('submit', function(event) {
                    event.preventDefault();  // 폼 제출로 인한 페이지 새로 고침 방지
                    var input = document.getElementById("messageText");
                    var messageText = input.value;  // 입력값 저장

                   // 사용자 입력 메시지를 화면에 표시
                    

                    ws.send(messageText);  // 서버로 메시지 전송

                    input.value = '';  // 입력란 초기화
                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                });
            </script>
        </body>
    </html>
    """)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
