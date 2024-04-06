#from pyuac import main_requires_admin




def convert_hex(hex_list:list) -> list:
    return [eval(char) for char in hex_list]

def pressed(key,log=False) -> bool:
    if keyboard.is_pressed(key):
        if log:
            logging.debug(f"'{key}' pressed")
        return True
    return False

def timer(addr, time, changed_value, default_value, thread_id) -> None:
    global threads
    divs = time//5
    while threads[thread_id]["loop"]:
        s(0.05)
        if threads[thread_id]["activated"]:
            for _ in range(divs+1):
                pm.write_float(addr,changed_value)
                s(5)
            pm.write_float(addr, default_value)
            threads[thread_id]["activated"]=False
    return

#@main_requires_admin
def main(config):
    global threads
    types = [i for i in list(config.keys()) if config[i]["addr"] is not None] # types of punishments #list(config.keys())
    logging.debug("types="+str(types))

    for valid_module in types:
        threads[valid_module]={
            "loop":True,
            "activated":False,
            "thread":Thread(target=timer,args=(
                config[valid_module]["addr"],
                config[valid_module]["timer"],
                config[valid_module]["changed"],
                config[valid_module]["default"],
                valid_module))}
        threads[valid_module]["thread"].start()
        #threads[i]["thread"].join()
    
    keybinds = [config[i]["keybind"] for i in types]
    logging.debug("keybinds="+str(keybinds))

    print(f'Loaded in {round((ti()-start)*1000)}ms')
    while True:
        s(0.05)
        for index in range(len(keybinds)):
            if pressed(keybinds[index]):
                print(f"Pressed {keybinds[index]}: {types[index]}")
                logging.debug("changed="+str(config[types[index]]["changed"]))
                logging.debug("timer="+str(config[types[index]]["timer"]))
                logging.debug("default="+str(config[types[index]]["default"]))
                #pm.write_float(ptrAddrs[index],config[types[index]]["changed"])
                threads[types[index]]["activated"]=True
        if pressed("l"): #L to exit
            print("Took an L")
            logging.debug("Took an L")
            for thread_id in list(threads.keys()):
                threads[thread_id]["loop"]=False
                threads[thread_id]["thread"].join()
            break
    input("Press ENTER to close")



if __name__ == "__main__":
    import logging
    import keyboard
    #from pymem import *
    import pymem
    from pymem.process import module_from_name
    from time import sleep as s
    from time import time as ti
    from threading import Thread
    from json import load,dump
    from pathlib import Path
    from requests import get
    from pathlib import Path
    import utils
    from checksumdir import dirhash

    debug = False
    writing = False
    if debug:
        files = ["data\\config.json","utils.py"]
        if writing:
            with open("data/config.json","w") as f:
                dump(utils.json,f,indent=4)
        for file_hash in files:
            print(f"File hash for {file_hash}: {utils.gen_hash(file_hash)}")

        exit()
        
    logging.basicConfig(level=logging.DEBUG,filename="log.log",filemode="w")
    print("Escape the Backrooms Twitch-redemption mod by Gacaes\n")

    hashes = {
        "data\\config" : "21b325f4c06fbcf986f7ef5f95a0dc81"
    }
    modules = [
        "data/fov.14.sqlite",
        "data/config.json",
        "data/Gamma.10.sqlite",
        "data/LOD.11.sqlite",
        "data/MVol.10.sqlite",
        "data/Sens.13.sqlite",
        "data/stam.10.sqlite"
    ]

    VERSION = "1.2"
    print(f"Current version: {VERSION}")

    try:
        print("\nLoading...")
        start = ti()
        
        threads = {}
        
        check_version = utils.check_version(VERSION)
        if not bool(check_version):
            print(f"A new version is avaliable: {str(check_version)}")
            # DL the new installer and run it
            utils.attempt_download(f"dist/EtB_Installer_v.{str(check_version)}.exe")
            #utils.fresh_install(modules) #DL the modules and process the sqlite files into json
        if not Path("data").exists():
            if not utils.fresh_install(modules):
                print("Could not install required files.")
                exit()
        #config = utils.validate_config(hashes["data\\config"])
        

        try:
            pm = pymem.Pymem("Backrooms-Win64-Shipping.exe")
        except pymem.exception.ProcessNotFound:
            print("Try opening the game first, dummy")
            input("Press ENTER to close")
            exit()
        except pymem.exception.CouldNotOpenProcess:
            print("Try opening this mod in Admin")
            input("Press ENTER to close")
            exit()
        module = module_from_name(pm.process_handle, "Backrooms-Win64-Shipping.exe").lpBaseOfDll
        logging.debug(f'module:{str(hex(module))}')
        config = utils.get_config(modules, pm, module)
        print(f"{i}:{config[i]}" for i in list(config.keys()))
        kill

        main(config)
    except Exception as ex:
        logging.exception(ex)
        print(f"\n**FATAL ERROR**: {ex}\nMore details found in log.log\n\n")
        input("Press ENTER to exit")