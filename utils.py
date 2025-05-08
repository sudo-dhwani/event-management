import random 
from datetime import datetime, timedelta

def random_date(offset=30):
    return datetime.utcnow() + timedelta(days=random.randint(1, offset))
