import asyncio
import json
import websockets
from models import Card, Player, Deck, Table

SELECT_MESSAGES = {7, 9}
TABLE_SELECTION_MESSAGE_INDEX = 10
tc_count = 0
start = False
end = False
prize = 0


async def select_table(websocket, table_id):
    await send_and_receive(websocket, {
        "id": 1016, "password": "", "playerEntryIdx": 0, "t": "SelectTable", "tableId": table_id
    })
    await send_and_receive(websocket, {
        "id": 1017, "isRealTable": False, "playerEntryIdx": 0, "t": "SelectTable", "tableId": table_id
    })


async def connect_and_send_messages():
    uri = "wss://fs.1win-prodlike.tech/front"
    async with websockets.connect(uri) as websocket:
        print("Соединение установлено.")
        print(websocket.response_headers)
        messages_to_send = [
            {"clientVersion": "HTML5", "locale": "ru", "protocolVersion": 0, "skinName": "1winpoker", "id": 1001,
             "t": "ClientVersion"},
            {"id": 1003, "convertersVersion": 1699763696, "miniConfigVersion": 1699763695, "t": "GetClientConfig"},
            {"id": 1004, "prizeConfigVersion": 1699763696, "levelsConfigVersion": 1699763696,
             "t": "RulesConfigRequest"},
            {"playerId": 0, "itemType": 0, "itemId": 0, "id": 1005, "t": "GetAllowedPlayerPermissions"},
            {"id": 1006, "t": "GetPlayerLevels"},
            {"id": 1007, "t": "GetCountries", "locale": "", "skin": "", "version": 1686220543},
            {"id": 1002, "t": "GetLobbyState"},
            {
                "deviceLabel": "platform=H;os=M;os_ver=10.15.7;device_id=202eb34fcd0cad5863f15a387a3d860f;"
                               "res=3360x2100;browser=C;browser_ver=120.0.0.0;app_ver=23.1.1.hb5d7d-s6c29c-bc73d0",
                "id": 1008, "t": "SetDeviceLabel"},
            {"displayMoneyType": 0, "id": 1009, "t": "SetSessionDisplayMoneyType"},
            {"id": 1010, "t": "GetLobbyChatHistory"},
            {"gametype": 0, "id": 1011, "showPlayNowChildTables": False, "t": "GetTablesList"}
        ]

        for i, message in enumerate(messages_to_send):
            if i in SELECT_MESSAGES:
                await send_message(websocket, message)
            else:
                await send_and_receive(websocket, message, i)

        table_id = int(input('Enter the id of the table: '))
        if table_id:
            await select_table(websocket, table_id)

            # Бесконечный цикл для приема сообщений от сервера
            while True:
                response = await websocket.recv()
                process_game_state(response)


async def send_and_receive(websocket, message, i=None):
    await send_message(websocket, message)
    response = await websocket.recv()
    if i == TABLE_SELECTION_MESSAGE_INDEX:
        print('Texas Holdem tables:')
        json_response = json.loads(response)
        tables = json_response["tables"]
        sorted_tables = sorted(tables, key=lambda x: x["n"], reverse=True)

        for table in sorted_tables:
            if table["g"] == 72:
                print(f"ID: {table['i']} Name: {table['n']} Bets: {table['s'] / 100}$/{table['bb'] / 100}$ "
                      f"Players: {table['mp']}")


def process_game_state(response):
    global tc_count
    global end
    global prize
    global start

    try:
        json_response = json.loads(response)
        if json_response["t"] == "Chat":
            chat_message = json_response["chatMessage"][0]["m"]
            if chat_message == "Новая игра":
                print("Новая игра")
                start = True
                end = False
            elif chat_message == "Игра закончена":
                print("Игра закончена\n")
                end = True
                tc_count = 0

        elif json_response["t"] == "GameState":
            game_state = json_response["gameState"]
            if "d" in game_state and "c" in game_state["d"]:
                card_values = [int(value) for value in game_state["d"]["c"].split(";")]
                if len(card_values) > tc_count and not end:
                    tc_count = len(card_values)
                    if tc_count > 3:
                        print(Card.get_card_by_code(card_values[-1]))
                    else:
                        for code in card_values:
                            print(Card.get_card_by_code(code))
            if "s" in game_state and start:
                players = []

                # Добавление каждого игрока в список players
                for player_data in game_state["s"]:
                    if player_data:
                        player = Player(player_data)
                        print(player)
                        players.append(player)

                start = False

            if "events" in json_response:
                events = json_response["events"]
                if events:
                    elem = events[0]
                    action_dict = {
                        4: "Ставка",
                        9: "Фолд" if elem.get("a") == 1 else ("Чек" if elem.get("a") == 2 else "Итог")
                    }

                    action = action_dict.get(elem.get("t"))
                    player = elem.get("s", 0)

                    if action == "Ставка":
                        money = int(elem.get("f", 0)) / 100

                        prize += money
                        # получить доступ к объекту класса
                        # сделать ставки из класса, если фолд, убирать игрока из класса
                        print(f"Игрок {player}: {action} {money}$")
                    elif action == "Итог":

                        print(f'Результат: Игрок {player} выиграл {prize}')
                        prize = 0
                    else:
                        if action:
                            print(f"Игрок {player}: {action}")

    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
    except KeyError as e:
        print(f"Ключ не найден: {e}")


async def send_message(websocket, message):
    message_json = json.dumps(message)
    await websocket.send(message_json)


# Запускаем асинхронное выполнение
asyncio.get_event_loop().run_until_complete(connect_and_send_messages())
