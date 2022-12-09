import os
import psutil
import time
import json
import re


db = R"Tortuga.json"
apps = []

def dump():
    with open(db, "w") as file:
        json.dump(apps, file)

def load():
    with open(db, "r") as file:
        global apps 
        apps = json.load(file)

def append(path):
    global apps
    result = re.search(r'.+\\(?P<name>.+).exe', path)
    if result:
        apps.append({'title': result.group('name'), 'path': path, 'total_time': {"hours": 0,"minutes": 0.0}})
    else:
        print("Illegal path!")
        exit(0)

def menu():
    try:
        print("Select game to launch:")
        for i, item in enumerate(apps):
            print(i+1, item['title'])  
        i = int(input("Input>"))
        if i-1 <= len(apps):
            return i-1
        else:
            return None
    except KeyboardInterrupt:
        exit(0)


def main():
    os.system("cls")
    
    load()
    # for item in apps:
    #     if item['path'] == app:
    #         print("Item already exists")
    #         return 0
    # append(app)
    # dump()
    # return 0
    if len(apps) == 1:
        i = 0
    else:
        i = menu()
    
    now = time.time()
    if os.path.exists(apps[i]['path']):
        proc = psutil.Popen(apps[i]['path'])
        name = proc.name()
        proc.wait()
        for proc2 in psutil.process_iter():
            if proc2.name() == name:
                print("cringe!")
                proc2.wait()
    session_time = time.time() - now

    print("Session time in seconds: ", session_time)

    hours = apps[i]['total_time']['hours']
    minutes = apps[i]['total_time']['minutes']
    minutes += session_time // 60
    if minutes >= 60:
        hours = minutes // 60
        minutes %= 60

    apps[i]['total_time']['hours'] = hours
    apps[i]['total_time']['minutes'] = minutes
    dump()

if __name__ == "__main__":
    main()
