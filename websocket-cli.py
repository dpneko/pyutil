from sqlalchemy import true
import websocket
import pathos


def on_message(ws, message):
    print(ws)
    # print(message)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("### closed ###")


websocket.enableTrace(True)

def func(i):
    ws = websocket.WebSocketApp("wss://greyapi.tdr.org/tdr_websocket",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
    while true:
        print(i)


if __name__ == '__main__':
    pool = pathos.pools.ProcessPool(4)
    pool.imap(func, range(4))
