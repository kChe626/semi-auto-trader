from uuid import uuid4


def create_trade_id() -> str:
    return str(uuid4())