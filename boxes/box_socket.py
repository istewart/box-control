import asyncio
import websockets
import json


async def connect():
    uri = "ws://localhost:8000/sockets/box/TODO/"

    async with websockets.connect(uri) as websocket:
        data = {'type': 'todo', 'data': {'foo': 1}}
        print('CONNECTED')
        await websocket.send(json.dumps(data))
        print('sent!')
        response = await websocket.recv()
        response_event = json.loads(response)

        response_type = response_event['type']
        response_data = response_event['data']

        print(response_event)

        print('session started!')

        for _ in range(100):
            print('sending')
            await asyncio.sleep(2)
            await websocket.send(json.dumps({'type': 'dataStream', 'data': [3,4,5,6]}))

        print('done sending!!')


asyncio.get_event_loop().run_until_complete(connect())