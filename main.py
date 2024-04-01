#from pyuac import main_requires_admin




def convert_hex(hex_list:list) -> list:
    return [eval(char) for char in hex_list]

def pressed(key,log=False) -> bool:
    if keyboard.is_pressed(key):
        if log:
            logging.debug(f"'{key}' pressed")
        return True
    return False

def getPtrAddr(mem, base, offsets):
    addr = mem.read_longlong(base)
    logging.debug(f'getPtrAddr:Base addr: {str(hex(addr))}')
    for offset in offsets[:-1]:
        logging.debug(f'getPtrAddr:Adding {hex(offset)}')
        addr = mem.read_longlong(addr + offset)
        logging.debug(f'getPtrAddr:New addr{str(hex(addr))}')
    logging.debug(f'getPtrAddr:Adding {hex(offsets[-1])}')
    addr += offsets[-1]
    logging.debug(str(hex(addr)))
    return addr

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
    types = [] # types of punishments #list(config.keys())
    logging.debug("types="+str(types))

    ptrAddrs = []
    for i in list(config.keys()):
        logging.debug("Getting ptr for "+str(i))
        print(f"Getting ptr for {i}")
        try:
            ptrAddrs.append(getPtrAddr(pm, module+config[i]["base_offset"], config[i]["offsets"]))
            types.append(i)
            threads[i]={
                "loop":True,
                "activated":False,
                "thread":Thread(target=timer,args=(
                    ptrAddrs[-1],
                    config[types[-1]]["timer"],
                    config[types[-1]]["changed"],
                    config[types[-1]]["default"],
                    i))}
            threads[i]["thread"].start()
            #threads[i]["thread"].join()
        except pymem.exception.MemoryReadError:
            logging.warning("Invalid ptr for {i}")
            print(f"**WARNING**: Failed to get ptr for {i}")
        except Exception as ex:
            logging.exception(str(ex))
            print(f"**EXCEPTION**: {ex}")
    
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
        

    print("Escape the Backrooms Twitch-redemption mod by Gacaes\n")
    logging.basicConfig(level=logging.DEBUG,filename="log.log",filemode="w")

    hashes = {
        "data\\config" : "21b325f4c06fbcf986f7ef5f95a0dc81"
    }

    VERSION = "1.1"
    print(f"Current version: {VERSION}")

    try:
        print("Loading...")
        start = ti()
        
        threads = {}
        
        check_version = utils.check_version(VERSION)
        if not check_version:
            print(f"A new version is avaliable: {check_version.version}")
            # DL the new installer and run it
            print("WIP")
        config = utils.validate_config(hashes["config"])
        #input("close")
        #exit()
        

        try:
            pm = pymem.Pymem("Backrooms-Win64-Shipping.exe")
        except pymem.exception.ProcessNotFound:
            print("Try opening the game first, dummy")
            input("Press ENTER to close")
        except pymem.exception.CouldNotOpenProcess:
            print("Try opening this mod in Admin")
            input("Press ENTER to close")
        module = module_from_name(pm.process_handle, "Backrooms-Win64-Shipping.exe").lpBaseOfDll
        logging.debug(f'module:{str(hex(module))}')

        main(config)
    except Exception as ex:
        logging.exception(ex)
        print("\n\n**FATAL ERROR**\nMore details found in log.log\n\n")
        print(ex)
        input("Press ENTER to exit")