from amulet_nbt import load, NamedTag, IntTag, StringTag, ByteTag
import tkinter as tk
import json, os
from tkinter import filedialog, ttk
from Litmatool import cn_translate, id_tran_name, grs
from tkinter import messagebox
#from LitematicaViewer import file_path

data = json.load(open(grs(os.path.join('lang', 'data.json')), 'r', encoding='utf-8'))
color_map = data["Color_map"]

path : str = ""
def cn_id(id):
    cd = cn_translate(id_tran_name(id))
    if cd == id_tran_name(id):
        return cn_translate(id_tran_name(id), types="Items")
    return cd

def LitConImport():
    global path
    path = filedialog.askopenfilename(filetypes=[("Litematic File", "*.litematic"), ("All File", "*.*")], title="选择 Litematic 文件")
    if not path: return
    print("Selected file path:", path)
    LitContainer()

def LitContainer() -> None:
    global path
    global cmd_table
    print(path)
    l = 1
    cmd_table.delete("1.0", tk.END)
    nbt_file: NamedTag = load(path, compressed=True)
    container = list(nbt_file.tag['Regions'].values())[0]
    if not len(container['TileEntities']):
        cmd_table.insert("1.0" , "Litematic file has no Container")
        return
    container = container['TileEntities']
    for nt in container:
        x = int(IntTag(nt['x']))
        y = int(IntTag(nt['y']))
        z = int(IntTag(nt['z']))
        try:
            id = str(nt['id'])
        except KeyError:
            print(f"ERROR: 发现缺失'id'的TileEntity，位置:({x},{y},{z})")
            messagebox.showerror("解析错误", f"发现缺失'id'的TileEntity，位置:({x},{y},{z})")
            return
        if 'item' in nt:
            item = nt['item']
            cmd_table.insert(f"{l}.0" ,f"{cn_id(id)} Pos:{(x,y,z)}\n")
            cmd_table.insert(f"{l+1}.0", f"----{cn_id(str(StringTag(item['id'])))} X{int(IntTag(item['count']))}\n")
            l+=2
        elif 'Items' in nt:
            item = nt['Items']
            if len(item) == 0:
                continue
            it : list = []
            asc = 97
            cmd_table.insert(f"{l}.0", f"{cn_id(id)} Pos:{(x, y, z)}\n")
            l += 1
            for i in item:
                cd = cn_id(str(StringTag(i['id'])))
                nm = int(IntTag(i['count']))
                st = int(ByteTag(i['Slot']))
                cmd_table.insert(f"{l}.0" , f"----{cd} X{nm}|位置:{st}    UI:{chr(asc)}\n")
                it.append((cd,st))
                l+=1
                asc += 1

            if "chest" in id or "minecraft:barrel" == id or "box" in id:
                mode=[['_'] * 9 for _ in range(3)]
                asc = 97
                for _,d in it:
                    mode[d//9][d%9] = chr(asc)
                    asc+=1

                for ix in mode:
                    item_out = "|"
                    for iy in ix:
                        item_out += f"{iy}|"
                    item_out += "\n"
                    cmd_table.insert(f"{l}.0", item_out)
                    l+=1
            elif "furnace" in id or "smoker" in id:
                mode=['_' for _ in range(3)]
                asc = 97
                for _,d in it:
                    mode[d] = chr(asc)
                    asc += 1
                cmd_table.insert(f"{l}.0", f"进口:{mode[0]}|出口:{mode[2]}|燃料:{mode[1]}\n")
                l += 1
            elif "minecraft:brewing_stand" == id:
                mode = ['_' for _ in range(4)]
                asc = 97
                for _,d in it:
                    mode[d] = chr(asc)
                    asc += 1
                cmd_table.insert(f"{l}.0", f"|{mode[0]} {mode[1]} {mode[2]}|燃料:{mode[3]}\n")
                l += 1
            elif "minecraft:chiseled_bookshelf" == id:
                mode = ['_' for _ in range(6)]
                asc = 97
                for _,d in it:
                    print(d)
                    mode[d] = chr(asc)
                    asc += 1
                cmd_table.insert(f"{l}.0", f"|{mode[0]}|{mode[1]}|{mode[2]}|\n")
                cmd_table.insert(f"{l+1}.0", f"|{mode[3]}|{mode[4]}|{mode[5]}|\n")
                l += 2
                print(mode)
        else:
            continue
        cmd_table.insert(f"{l}.0" , "=================\n")
        l+=1
        rootc.update_idletasks()

rootc = tk.Tk()
rootc.title("Containers")
rootc.iconbitmap(grs("icon.ico"))
rootc.geometry("500x800")
rootc.configure(bg=color_map[0]["MC"])

Clable = tk.Label(rootc,text="容器探测", font=("Arial", 14, "bold"), bg=color_map[0]["MC"], fg=color_map[0]["TT"])
Clable.pack()
CBP = tk.Frame(rootc)
CBP.pack()
Cbutton = tk.Button(CBP,text="Analysis",command=LitContainer, font=("Arial", 10), bg=color_map[0]["PC"], fg=color_map[0]["BG"])
Cbutton.grid(row=0,column = 0)
Cbutton = tk.Button(CBP,text="ChooseFile",command=lambda :LitConImport(), font=("Arial", 10), bg=color_map[0]["PC"], fg=color_map[0]["BG"])
Cbutton.grid(row=0,column = 1)
Csroll = tk.Scrollbar(rootc, orient="vertical")
Csroll.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
cmd_table = tk.Text(rootc, bg=color_map[0]["BG"], fg=color_map[0]["TT"], font=("Arial", 12), yscrollcommand=Csroll)
Csroll.config(command=cmd_table.yview)
cmd_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=10)

rootc.mainloop()

