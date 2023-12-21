import time
import threading
import subprocess
import shutil
letter = "E:" #the disk letter
sector_size = subprocess.check_output(f"fsutil fsinfo sectorInfo {letter}", shell=True)
sector_size = sector_size.decode(errors="ignore")
sector_size = sector_size.split("\r\n")
sector_size = dict([[i.split(":")[0],i.split(":")[1].split(" ")[-1]] for i in sector_size if ":" in i])
sector_size = int(sector_size["LogicalBytesPerSector"])
disk_size = shutil.disk_usage(letter).total
letter = "\\\\.\\"+letter
num_of_sector = disk_size // sector_size
skip = 0#skip the first n sectors
num_of_sector -= skip
skippingC, skipSave, skipLast = 0, 0, 0#don't touch
print(f"Disk size is {disk_size} bytes, {disk_size / 1024 / 1024} MB")
print(f"Number of sectors: {num_of_sector}")
if skip != 0:print(f"Skipping {skip} sectors")
#it'll read the disk sector by sector, and write each sector to a single file : new_disk.bin
class Sector:
    def __init__(self, number:int, data:bytes):
        self.number = number
        self.data = data

    def __repr__(self):
        return f"<Sector {self.number}>"

    def __str__(self):
        return f"<Sector {self.number}>"

    def __bytes__(self):
        return self.data

current_sector_data = None  #global variable to store the current sector data

def modified_read(f, sector_size):
    """read a sector from the disk"""
    global current_sector_data
    try:
        current_sector_data = f.read(sector_size)
    except Exception as e:
        print(e)
        current_sector_data = False

def instant_save(text:str,fname:str="skipped_sectors.txt"):
    """save a string to a file"""
    with open(fname, "a") as f:
        f.write(text)
        f.close()

def read_disk_raw():
    """generator of disk sectors in raw format"""
    global current_sector_data, skippingC, skipSave, skipLast
    with open(letter, "rb") as f:
        if skip != 0:f.seek(skip * sector_size)#skip sectors
        for i in range(skip, num_of_sector):
            if skippingC != 0:
                skippingC -= 1
                print(f"Skipping sector n°{i}, {skippingC} sectors left")
                instant_save(str(i)+"\n")
                yield i, b"\x00" * sector_size
                continue
            if skipLast != 0 and skipSave > 256:
                    skippingC, skipSave, skipLast = 0, 0, 0
            if i - skipLast > 100:
                skippingC, skipSave, skipLast = 0, 0, 0
            t = threading.Thread(target=modified_read, args=(f, sector_size))
            t.start()
            t.join(timeout=2)
            if t.is_alive():
                print(f"[-] Timeout at sector {i}", " "*20)
                if skipSave == 0:skipSave = 1
                else:skipSave *= 2#incremental skip, in case there are a lot of bad sectors, sorry for everyone who wants 100% accurate cd / dvd backup
                skippingC = skipSave
                skipLast = i
                instant_save(str(i)+"\n", "bad_sectors.txt")
                yield i, b"\x00" * sector_size
            else:
                if current_sector_data is False:
                    if skipSave == 0:skipSave = 1
                    else:skipSave *= 2
                    skippingC = skipSave
                    skipLast = i
                    instant_save(str(i)+"\n", "bad_sectors.txt")
                    current_sector_data = b"\x00" * sector_size
                yield i, current_sector_data

def read_disk():
    """generator of disk sectors in Sector class"""
    for i, sector in read_disk_raw():
        yield Sector(i, sector)

def duplicate_disk():
    """duplicate the disk to a new disk"""
    t1 = time.time()
    mode = "wb" if skip == 0 else "ab"
    with open("new_disk.bin", mode) as f:
        for sector in read_disk():
            f.write(bytes(sector))
            avg = (sector.number + 1) / (time.time() - t1)
            avg_str = f"Average time: {round(avg, 2)} sectors/s"
            print(f"Writing sector {sector.number}, {round(sector.number / num_of_sector * 100, 2)}%, "+avg_str, end="\r")
    t2 = time.time()
    print(f"Time used: {round(t2 - t1,2)}s")

def read_sector(number:int):
    """read a sector from the disk"""
    with open(letter, "rb") as f:
        f.seek(number * sector_size)
        return f.read(sector_size)
    
if __name__ == "__main__":
    duplicate_disk()
    print("[+] Done")
    print("[i] Notice: In some cases you can open the bin file with a zip extractor and extract the files from it, (like 7zip)")
    #print(read_sector(0))  #read the first sector exemple
