import tkinter as tk
from tkinter import filedialog, ttk
from litemapy import Schematic, Region, BlockState
from PIL import Image, ImageTk
import importlib, webbrowser, json, os, subprocess
your_module = importlib.import_module('litemapy')
YourClass = getattr(your_module, 'Region')

APP_VERSION = '0.3.2'
file_path = ""
file_name = "litematica"
Block = {}
images = {}
color_map = [
    '#3399ff',  # 主色 浅蓝
    '#0066cc',  # 副色 深蓝
    '#f8f9fa',  # 背景
    '#343a40',  # 文字
]
json_data = json.load(open('lang/zh_cn.json', 'r', encoding='utf-8'))

def manual_install_pk():
    try:
        result = subprocess.run(['install.bat'], check=True, capture_output=True, text=True)
        print("Packages install successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.stderr)

def convert_units(number):
    units = {'箱': 54 * 27 * 64, '盒': 27 * 64, '组': 64, '个': 1}
    result = ""
    for unit, value in units.items():
        result += str(number // value) + unit
        number %= value
    return result

def import_file():
    global file_path, file_name
    file_path = filedialog.askopenfilename()
    file_path = file_path.replace("\\", "/")
    file_name = file_path.split("/")[-1]
    label_middle.config(text=f"{file_name}")
    print(f"Imported file: {file_path}")

def cn_translate(id):
    return json_data.get(id, id)

def load_image(block_name):
    try:
        img_path = f"block/{block_name}.png"
        img = Image.open(img_path)
        img = img.resize((20, 20), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        images[block_name] = img
        return img
    except:
        img_path = f"block/info_update.png"
        img = Image.open(img_path)
        img = img.resize((20, 20), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        images[block_name] = img
        return img

def insert_table(block_state, count, simple_type):
    block_name = str(block_state).split(":")[-1].split("[")[0]
    block_id = cn_translate(block_name) if simple_type else block_state._BlockState__block_id
    try:
        properties = str(block_state._BlockState__properties).replace("'", "") if not simple_type else block_name
    except:
        properties = ""

    img = load_image(block_name)
    count_table.insert('', 'end', image=img, values=(str(block_id), str(count), convert_units(count), properties))

def output_data():
    output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text files", "*.txt"), ("All files", "*.*")],title="Litematica Analysis Data Save As",initialfile=f"{file_name.split(".")[0]}.txt")
    if not output_file_path:
        return
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{file_name}\n======================\n")
        for key in Block:
            f.write(f"{str(Block[key]).rjust(6,"0")} | {key.split("[")[0].split(":")[-1]}\n")
    os.startfile(output_file_path)

def start_analysis(simple_type=False):
    count_table.delete(*count_table.get_children())
    Block.clear()
    if not file_path:
        print("Please import a file first.")
        return

    try:
        schematic = Schematic.load(file_path)
        print(f"Schematic loaded: {schematic}")
        for region_index, region in enumerate(schematic.regions.values()):
            print(f"Analyzing region {region_index + 1}")
            size_x = region.maxx() - region.minx() + 1
            size_y = region.maxy() - region.miny() + 1
            size_z = region.maxz() - region.minz() + 1
            num = 0
            for x in range(size_x):
                for y in range(size_y):
                    for z in range(size_z):
                        block_state = region._Region__palette[region._Region__blocks[x, y, z]]
                        block_id = block_state._BlockState__block_id
                        if block_id not in ["minecraft:air", "minecraft:cave_air", "minecraft:void_air"]:
                            num += 1
                            if block_id not in ["minecraft:piston_head", "minecraft:bubble_column",
                                                "minecraft:nether_portal", "minecraft:moving_piston",
                                                "minecraft:bedrock"]:
                                output = block_id if simple_type else block_state
                                if output not in Block:
                                    Block[output] = 1
                                else:
                                    Block[output] += 1
            if DoEntity.get():
                for entity in region._Region__entities:
                    entity_type = "E/" + str(entity.id)
                    if entity_type not in ["E/minecraft:item", "E/minecraft:bat", "E/minecraft:experience_orb",
                                           "E/minecraft:shulker_bullet"]:
                        if entity_type not in Block:
                            Block[entity_type] = 1
                        else:
                            Block[entity_type] += 1
            time = 1 if entry_times.get() == "" else int(entry_times.get())
            label_bottom.config(
                text=f"Size体积: {size_x}x{size_y}x{size_z} | Number数量: {num} | Density密度: {num / (size_x * size_y * size_z) * 100:.2f}% | Times倍数: {time} | Types种类: {len(Block)}")
    except Exception as e:
        print(f"Error during analysis: {e}")
        return

    sorted_block = sorted(Block.items(), key=lambda x: x[1], reverse=True)
    for index, (block_state, count) in enumerate(sorted_block):
        try:
            count = count * int(entry_times.get())
        except:
            count = count * 1
        insert_table(block_state, count, simple_type)

# Tkinter Setting
litem = tk.Tk()
litem.title(f"Litematica Viewer投影查看器 v{APP_VERSION}")
litem.geometry("1280x720")
litem.iconbitmap("icon.ico")
litem.configure(bg=color_map[2])
litem.attributes("-alpha", 0.9)
# MENU
menu = tk.Menu(litem)
DoEntity = tk.IntVar(value=1)

menu_analysis = tk.Menu(menu, tearoff=0)
menu_analysis.add_command(label="Import导入", command=import_file, font=("Arial", 10))
menu_analysis.add_command(label="Output导出", command=output_data, font=("Arial", 10))
menu_analysis.add_command(label="SimpleAnalysis简洁分析", command=start_analysis, font=("Arial", 10))
menu_analysis.add_command(label="FullAnalysis全面分析", command=lambda:start_analysis(True), font=("Arial", 10))
menu.add_cascade(label="DataAnalysis数据分析", menu=menu_analysis, font=("Arial", 20))
menu_AnaSet = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Setting分析设置",menu=menu_AnaSet, font=("Arial", 20))
menu_AnaSet.add_checkbutton(label="DoAnalysisEntity是否分析实体",variable=DoEntity, font=("Arial", 10))
menu_Help = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Help帮助",menu=menu_Help, font=("Arial", 20))
menu_Help.add_command(label="About关于", command=lambda:webbrowser.open("https://github.com/albertchen857/LitematicaViewer"), font=("Arial", 10))
menu_Help.add_command(label="AboutCreater关于作者", command=lambda:webbrowser.open("https://space.bilibili.com/3494373232741268"), font=("Arial", 10))
menu_Help.add_command(label="ManualInstallPackages手动更新软件库", command=manual_install_pk, font=("Arial", 10))


litem.config(menu=menu, padx=10, pady=10)
# 上容器
frame_top = tk.Frame(litem)
frame_top.configure(bg=color_map[1], bd=5)
frame_top.pack(side=tk.TOP, fill=tk.X)

btn_import = tk.Button(frame_top, text="Import导入", command=import_file, font=("Arial", 10))
btn_import.configure(bg=color_map[0],fg=color_map[3],relief='ridge')
btn_import.pack(side=tk.LEFT, padx=5, pady=5)
btn_simstart = tk.Button(frame_top, text="SIMPLE Analysis简洁分析", command=lambda:start_analysis(True), font=("Arial", 10))
btn_simstart.configure(bg=color_map[0],fg=color_map[3],relief='ridge')
btn_simstart.pack(side=tk.LEFT, padx=5, pady=5)
btn_start = tk.Button(frame_top, text="FULL Analysis全面分析", command=start_analysis, font=("Arial", 10))
btn_start.configure(bg=color_map[0],fg=color_map[3],relief='ridge')
btn_start.pack(side=tk.LEFT, padx=5, pady=5)

btn_github = tk.Button(frame_top, text="GitHub", command=lambda:webbrowser.open("https://github.com/albertchen857/LitematicaViewer"), font=("Arial", 10))
btn_github.configure(bg="black",fg=color_map[2],relief='groove')
btn_github.pack(side=tk.RIGHT, padx=5, pady=5)
btn_bilibili = tk.Button(frame_top, text="Bilibili", command=lambda:webbrowser.open("https://space.bilibili.com/3494373232741268"), font=("Arial", 10))
btn_bilibili.configure(bg="#FF6699", fg=color_map[2],relief='groove')
btn_bilibili.pack(side=tk.RIGHT, padx=5, pady=5)
# STYLE
table_sty = ttk.Style()
table_sty.configure("Treeview", font=("Arial", 12), rowheight=25, background=color_map[1], foreground=color_map[2])
table_sty.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background=color_map[1], foreground=color_map[3])
table_sty.map('Treeview', background=[('selected', color_map[0])])
# 中容器
frame_middle = tk.Frame(litem, bg=color_map[0])
frame_middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
# - 中容器顶部
frame_middle_top = tk.Frame(frame_middle, bg=color_map[0])
frame_middle_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

label_middle = tk.Label(frame_middle_top, text="LitematicaViewer投影查看器", font=("Helvetica", 30, 'bold'))
label_middle.configure(bg=color_map[0], fg=color_map[3], bd=5)
label_middle.pack(fill=tk.Y)

label_bottom = tk.Label(frame_middle_top, text="Size体积 | Number数量 | Density密度 | Times倍数 | Types种类", font=("Helvetica", 14, "bold"))
label_bottom.configure(bg=color_map[0], fg=color_map[2], bd=5)
label_bottom.pack(side=tk.LEFT, fill=tk.X, padx=20, pady=10)

frame_right = tk.Frame(frame_middle_top, bg=color_map[0])
frame_right.pack(side=tk.RIGHT, fill=tk.Y, padx=40)

label_times = tk.Label(frame_right, text="Times倍数", font=("microsoft yahei ui", 16, "bold"))
label_times.configure(bg=color_map[0], fg=color_map[3])
label_times.pack(side=tk.LEFT, padx=5)

entry_times = tk.Entry(frame_right, width=10, bg=color_map[2], fg=color_map[1], font=("Helvetica", 10))
entry_times.pack(side=tk.RIGHT, padx=5)
# - 中容器DEC
#frame_middle_dec = tk.Frame(frame_middle)
#frame_middle_dec.pack()
underscore1 = tk.Frame(frame_middle, bg=color_map[2])
underscore1.pack( padx=40, pady=10)

# - 中容器表格
frame_chart = tk.Frame(frame_middle, bg=color_map[3])
frame_chart.configure(background=color_map[0])
frame_chart.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

sroll = tk.Scrollbar(frame_chart, orient="vertical")
sroll.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
count_table = ttk.Treeview(frame_chart, column=('blockID', 'num', 'unit', 'properties'), height=7, yscrollcommand=sroll.set)
count_table.heading('blockID', text='ID/名字', anchor="center")
count_table.heading('num', text='Num数量', anchor="center")
count_table.heading('unit', text='Unit单位数', anchor="center")
count_table.heading('properties', text='Prop属性', anchor="center")
count_table.column("#0", width=2, anchor="e")
count_table.column("blockID", width=2)
count_table.column("num", width=2)
count_table.column("unit", width=2)
count_table.column("properties", width=300)
count_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=10)



litem.mainloop()
