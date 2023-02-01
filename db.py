import json

def read_users():
    with open('db/user.json', 'r') as f:
        user = json.load(f)
    return user

def write_users(user):
    with open('db/user.json', 'w') as f:
        json.dump(user, f)