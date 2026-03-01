from collections import deque


class WsReplayBuffer:
    def __init__(self, maxlen: int = 1000) -> None:
        self.seq = 0
        self.events: deque[dict] = deque(maxlen=maxlen)

    def publish(self, channel: str, payload: dict) -> dict:
        self.seq += 1
        event = {"seq": self.seq, "channel": channel, "payload": payload}
        self.events.append(event)
        return event

    def replay_from(self, seq: int) -> list[dict]:
        return [e for e in self.events if e["seq"] > seq]
