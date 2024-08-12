import json

def save_data(areas):
    with open('data.json', "w") as f:
        json.dump(areas, f)
def recover_data():
    with open('data.json') as f:
        return json.load(f)
