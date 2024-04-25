import uuid


def generate_random_digits(count: int) -> str:
    return str(uuid.uuid4().int)[:count]
