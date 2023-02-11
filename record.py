from typing import NamedTuple, Optional

from user import UserInfo

class RecordInfo(NamedTuple):
    match_type: str
    challenger: UserInfo
    challenged: UserInfo
    result: str
    delta: float
    problem: int
    time: int
    start_datetime: str
    query: str
    timeout: int
    rated: bool

class RecordTable(object):
    head_to_head: dict[tuple[str, str], list[RecordInfo]]
    record_dict: dict[str, list[RecordInfo]]

    def __init__(self):
        self.head_to_head = {}
        self.record_dict = {}

    def new_record(self, match_type: str, challenger: UserInfo, challenged: UserInfo, result: str, delta: float, problem: int, time: int, start_datetime: str, query: str, timeout: int, rated: bool) -> RecordInfo:
        return RecordInfo(
            match_type = match_type,
            challenger = challenger,
            challenged = challenged,
            result = result,
            delta = delta,
            problem = problem,
            time = time,
            start_datetime = start_datetime,
            query = query,
            timeout = timeout,
            rated = rated
        )

    def add_record(self, match_type: str, challenger: UserInfo, challenged: UserInfo, result: str, delta: float, problem: int, time: int, start_datetime: str, query: str, timeout: int, rated: bool) -> None:
        record = self.new_record(match_type, challenger, challenged, result, delta, problem, time, start_datetime, query, timeout, rated)
        if (challenger.boj_id, challenged.boj_id) not in self.head_to_head:
            self.head_to_head[(challenger.boj_id, challenged.boj_id)] = []
        if (challenged.boj_id, challenger.boj_id) not in self.head_to_head:
            self.head_to_head[(challenged.boj_id, challenger.boj_id)] = []
        self.head_to_head[(challenger.boj_id, challenged.boj_id)].append(record)
        self.head_to_head[(challenged.boj_id, challenger.boj_id)].append(record)
        if challenger.boj_id not in self.record_dict:
            self.record_dict[challenger.boj_id] = []
        if challenged.boj_id not in self.record_dict:
            self.record_dict[challenged.boj_id] = []
        self.record_dict[challenger.boj_id].append(record)
        self.record_dict[challenged.boj_id].append(record)

    def get_head_to_head_record(self, player1: str, player2: str) -> Optional[list[RecordInfo]]:
        if (player1, player2) not in self.head_to_head:
            return None
        return self.head_to_head[(player1, player2)]

    def get_record(self, player: str) -> Optional[list[RecordInfo]]:
        if player not in self.record_dict:
            return None
        return self.record_dict[player]
Record = RecordTable()
