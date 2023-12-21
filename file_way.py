import time
import os
import shutil
import multiprocessing
import subprocess
skip = 0
letter = "E:" #the disk letter
sector_size = subprocess.check_output(f"fsutil fsinfo sectorInfo {letter}", shell=True)
sector_size = sector_size.decode(errors="ignore")
sector_size = sector_size.split("\r\n")
sector_size = dict([[i.split(":")[0],i.split(":")[1].split(" ")[-1]] for i in sector_size if ":" in i])
sector_size = int(sector_size["LogicalBytesPerSector"])
disk_size = shutil.disk_usage(letter).total
letter = "\\\\.\\"+letter

def copy(src, dst):
    """copy a file"""
    if os.path.isdir(src):return
    try:
        shutil.copy(src, dst)
    except Exception as e:
        print(f"[-] Error copying {src} to {dst}: {e}", " "*20)
        return

# def getSpeed():
#     """get the cd read speed in bytes/sec"""
#     global sector_size
#     t1 = time.time()
#     num_of_sectors = 1000#the higher the more accurate but slower
#     for i in range(num_of_sectors):
#         with open("\\\\.\\E:", "rb") as f:
#             f.read(sector_size)
#     t2 = time.time()
#     return sector_size * num_of_sectors / (t2 - t1)#return bytes/sec

def main():
    """main function"""
    output = "./output"
    if not os.path.exists(output):
        os.mkdir(output)
    t1 = time.time()
    # print("[*] Getting disk speed", end="\r")
    # diskSpeedAvg = getSpeed()
    # print(f"[i] Disk speed is {round(diskSpeedAvg/1024**2,2)} MB/sec")
    index = 0
    for file in os.listdir("E:\\Didiier_Nishuone_MP3_192kbps"):
        if index < skip:
            index += 1
            continue
        print(f"[*] Copying {file}", " "*20, end="\r")
        t = multiprocessing.Process(target=copy, args=(f"E:\\input\{file}", output))
        t.start()
        # timeout = os.path.getsize(f"E:\\input\{file}") / diskSpeedAvg
        timeout = 20
        # timeout *= 2# 2 times the time it should take, just to be sure
        print(f"[*] Timeout set to {round(timeout,2)} seconds", " "*20)
        t.join(timeout)
        if t.is_alive():
            print(f"[-] Timeout at file {file}", " "*20)
            try:
                t.terminate() 
            except Exception as e:
                print(f"[-] Error stopping thread: {e}", " "*20)
            continue
        avg = (index + 1) / (time.time() - t1)
        print(f"[+] Copied {file} at {round(avg,2)} files/sec", " "*20)
        index += 1

if __name__ == "__main__":
    main()
