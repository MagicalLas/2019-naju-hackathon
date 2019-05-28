import json
import random

from utils import Singleton, hash


KET_WORD = {
    "네트워크": ["TCP", "IP", "3 way hand shake", "host", "UDP"],
    "디비": ["sql", "table", "column", "row", "select"],
    "회로": ["집적회로", "트랜지스터", "반가산기", "누산기", "플립플롭"],
    "컴구": ["CPU", "레지스터", "램", "운영체제", "ARM", "X86"],
    "자료구조": ["큐", "스택", "R-B Tree", "Linked List", "Heap"],
    "소프트웨어공학": ["애자일", "TDD", "DDD", "ATDD", "SOLID", "리스코프치환법칙"],
    "인공지능": ["GAN", "CNN", "K-Mean", "Convergence"],
    "IoT": ["mosquitto", "web", "arduino", "라즈베리파이"],
    "정보보안": ["리버싱", "GDB"],
    "알고리즘": ["동적계획법", "메모이제이션", "다익스트라 알고리즘", "시간복잡도", "재귀", "점화식"],
    "선생님": ["이명서", "고익종", "우주선", "김은희", "박호열"]
}


def get_keyword(subject):
    return random.choice(KET_WORD[subject])


class RoomManager(Singleton):
    rooms = []

    def new_rooms(self, name, user_name, desc):
        self.rooms.append(Room(name, user_name, desc))

    def get_room_infomation(self):
        return {
            "msgType": "rspRoomList",
            "Data": {
                "reqResult": True,
                "roomList": [i.dictionaly for i in self.rooms]
            }
        }

    def join_room(self, room_id, user):
        room = self.find_room(room_id)
        return room.join_user(user)

    def start_game(self, room_id):
        room = self.find_room(room_id)
        response = room.start_game()

        room.users[-1].send(json.dumps(response))
        for index, user in enumerate(room.users[:4]):
            response["Data"]["turn"] = index
            user.send(json.dumps(response))

    def find_room(self, id):
        return [room for room in self.rooms if room.id == id][0]

    def check_room_is_exist(self, id):
        return True if [0 for room in self.rooms if room.id == id] else False


class Room(object):
    LIMIT = 5
    entrance_response_template = {
        "msgType": "rspEntranceRoom",
        "Data": {
            "reqResult": True,
            "msg": ""
        }
    }
    start_response_template = {
        "msgType": "rspStartGame",
        "Data": {
            "reqResult": True,
            "msg": "Start game.",
            "roomId": "",
            "turn": -1,
            "keyword": "",
            "tagger": ""
        }
    }

    def __init__(self, name, user, desc):
        self.name = name
        self.id = hash(name)
        self.users = [user]
        self.count = len(self.users)
        self.tagger = None
        self.desc = desc

        print("Room created:", self.id)

    @property
    def dictionaly(self):
        return {
            "id": self.id,
            "waiterCnt": self.count,
            "watierNames": [user.name for user in self.users],
            "content": self.desc
        }

    def join_user(self, user):
        response = self.entrance_response_template

        if self.count < self.LIMIT:
            self.users.append(user)
            self.count = len(self.users)

            print("{0} joined into {1} room.\n{1} room count is {2}.".format(
                user.name, self.id, self.count))

            response["Data"]["reqResult"] = True
        else:
            response["Data"]["reqResult"] = False
            response["Data"]["msg"] = "Already this room is full."

        return response

    def start_game(self):
        response = self.start_response_template

        random.shuffle(self.users)
        tagger = self.users[4]

        response["Data"]["msg"] = "Start Game"
        response["Data"]["tagger"] = tagger.name
        response["Data"]["roomId"] = self.id
        response["Data"]["keyword"] = get_keyword()

        print("{0} room start game.".format(self.id))

        return response

    def is_full(self):
        return self.LIMIT <= self.count
