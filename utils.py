from hashlib import md5
from pathlib import Path
from os import getcwd
from requests import get
from json import load,dump
from sqlite3 import connect

json = {
    "gammaDOWN" : {
        "base_offset" : 0x0463B7F0,
        "offsets" : [0x0, 0x40, 0xA8, 0x520, 0x180, 0x20, 0x904],
        "changed" : 0.1,
        "default" : 2.2,
        "keybind" : "u",
        "timer" : 300
    },
    "sensitivityUP" : {
        "base_offset" : 0x0463A8C0,
        "offsets" : [0xD60, 0x1A0, 0x20, 0x360, 0x2B0, 0x20, 0x810],
        "changed" : 90.0,
        "default" : 1.0,
        "keybind" : "o",
        "timer" : 300
    },
    "fps" : {
        "base_offset" : 0x04C62E40,
        "offsets" : [0x58, 0x58, 0x598],
        "changed" : 10.0,
        "default" : 90.0,
        "keybind" : "p",
        "timer" : 300
    }
}

def gen_hash(filename):
    path = Path(f"{getcwd()}\\{filename}")
    file = open(path)
    file = file.read().encode('utf-8')
    return md5(file).hexdigest()

class check_version():
    def __init__(self, current_version):
        self.url = "https://raw.githubusercontent.com/Gacaes/EtB-mod/main/version"
        self.status = 404
        self.current = current_version
        self.version = self.retry()
    
    def __str__(self):
        return self.version
    
    def __bool__(self):
        return self.version == self.current

    def retry(self):
        for _ in range(3):
            version = get(self.url)
            self.status = version.status_code
            print(f"Version status code: {self.status}")
            if self.status == 200:
                return version.text.strip()
        raise Exception("Could not get 200 status code from remote version")

def validate_config(hash) -> dict:
    try:
        if gen_hash("data\\config.json") == hash:
            # import and return the config
            return load(open("data\\config.json",'r'))
    except FileNotFoundError:
        pass
    # DL it
    #logging.warning("config.json not found! Attempting to download.")
    print("config.json not found! Attempting to download.")
    for _ in range(3):
        file = get("https://raw.githubusercontent.com/Gacaes/EtB-mod/main/config.json")
        status = file.status_code
        print(f"Config.json status code:{status}")
        if status == 200:
            with open("data\\config.json","w") as f:
                f.write(file.text)
            return load(open("data\\config.json",'r'))
        #else:
            #logging.warning(f"config.json online file status code:{file.status_code}")
    raise Exception("Could not validate config.json")

def gen_PTRs_from_sql(module):
    modules = {"fov" : "data\\fov.14.sqlite"}
    con = connect(modules[module])
    cur = con.cursor()
    temp = cur.execute("""SELECT * FROM results""").fetchall()
    listing = [[hex(num) for num in i if num is not None] for i in temp]
    new_obj = {}
    for entry in listing:
        a_offsets = entry[5:]
        a_offsets.reverse()
        new_obj[entry[1]] = {
            "base_offset" : entry[4],
            "offsets" : [eval(offset) for offset in a_offsets]}
    with open(f"{module}.json",'w') as f:
        dump(new_obj,f,indent=4)
    con.close()

#gen_PTRs_from_sql("fov")