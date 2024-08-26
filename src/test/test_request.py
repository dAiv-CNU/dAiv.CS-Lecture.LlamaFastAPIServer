import asyncio
import websockets
import ssl


async def send_message():
    uri = "ws://localhost:8000/ws/634"
    ssl_context = ssl.create_default_context()

    async with websockets.connect(uri) as websocket:
        while True:
            # 서버로 메시지 전송
            message = input()
            if message == "quit":
                break
            await websocket.send(message)

            response = await websocket.recv()
            print(response)


# asyncio 이벤트 루프를 실행하여 비동기 함수를 실행
if __name__ == "__main__":
    asyncio.run(send_message())
