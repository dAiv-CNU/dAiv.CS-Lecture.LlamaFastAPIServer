import asyncio
import websockets
import ssl

async def send_message():
    uri = "wss://localhost:8000/ws/153"
    ssl_context = ssl.create_default_context()
    # 웹소켓 서버 URI, client_id는 원하는 숫자로 변경 가능

    async with websockets.connect(uri) as websocket:
        while True:
            # 서버로 메시지 전송
            message = input()
            if message == "quit":
                break
            await websocket.send(message)

            # 서버로부터 응답 수신
            response = await websocket.recv()

            response2 = await websocket.recv()
            print(f"Received from server: {response2}")

# asyncio 이벤트 루프를 실행하여 비동기 함수를 실행
if __name__ == "__main__":
    asyncio.run(send_message())
