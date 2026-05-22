import json

with open("../dataset/users.json", "r") as f:
    USERS = json.load(f)

with open("../dataset/access_policies.json", "r") as f:
    ACCESS_POLICIES = json.load(f)


def get_user_role(username):
    for user in USERS:
        if user["username"] == username:
            return user["role"]
    return None


def check_access(username, source):
    role = get_user_role(username)

    allowed_roles = ACCESS_POLICIES.get(source, [])

    return role in allowed_roles