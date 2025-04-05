import threading
import sys
import os
from tkinter import filedialog
from tkinter import ttk
from litemapy import Schematic, BlockState
from PIL import Image, ImageTk


sys.path.extend(os.path.dirname(__file__)+"..")


import LitRender, easygui
try:
    from script.LitRender import OpenGLView, main_render_loop
    from script.Litmatool import *
    from script.Structure import *
    from script.liteVersonFix import *
except:
    from LitRender import OpenGLView, main_render_loop
    from Litmatool import *
    from Structure import *
    from liteVersonFix import *
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import importlib, webbrowser, codecs, atexit


import traceback

data = json.load(open(grs(os.path.join('lang', 'data.json')), 'r', encoding='utf-8'))
color_map = data["Color_map"][data["Save"]["ui"]["ColorMap"]]
DefaultFont = data["Save"]["ui"]["Font"]
DefaultFontSize = data["Save"]["ui"]["FontSize"]

def handle_exception(exc_type, exc_value, exc_traceback):
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open("error.log", "w") as f:
        f.write(error_msg)
    sys.exit(1)

sys.excepthook = handle_exception


your_module = importlib.import_module('litemapy')
YourClass = getattr(your_module, 'Region')
plt.rcParams['font.sans-serif'] = [DefaultFont]  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

APP_VERSION = '0.6.4'
schematic : Schematic = None
file_path = ""
file_name = "litematica"
#log_path = "../"
Block : dict[str:int] = {} #{id:num,...}
Block_pos : list[tuple[tuple,str,list]] = [] #[(pos,id,prop),...]
Cla_Block = {"实体": [], "羊毛": [], "陶瓦": [], "混凝土": [], "玻璃": [], "木制": [], "石质": [],
                     "其他岩石": [], "石英": [], "矿类": [], "自然类": [], "末地类": [], "地狱类": [], "海晶类": [],
                     "粘土类": [], "红石":[], "铁类":[], "容器":[], "液体":[], "其他": []}
images = {}


def on_exit():
    with open(grs('log.txt'), "w") as file:
        fw = ""
        for logvar in LogVar:
            fw += str(globals()[logvar].get())
        print(f"Log Rewrite:{fw}")
        file.write(fw)
atexit.register(on_exit)

def ConAly():
    try:
        from script.LitContainer import LitConImport
    except:
        from LitContainer import LitConImport
    threading.Thread(target=LitConImport, daemon=True).start()

def CS_trans_dict(inp:str) -> dict:
    d1 = inp.strip("\n").split(",")

    d2 = {}
    print(d1, d2)
    for i,s in enumerate(d1):
        init, final =tuple(s.split("-"))
        print(init,final)
        init = "minecraft:"+str(cn_translate(init,False))
        final = "minecraft:"+str(cn_translate(final,False))
        d2[init] = final

    return d2

def import_file():
    global file_path, file_name
    file_path = filedialog.askopenfilename(filetypes=[("Litematic File","*.litematic"),("All File","*.")])
    file_path = file_path.replace("\\", "/")
    file_name = file_path.split("/")[-1]
    label_middle.config(text=f"{file_name}")
    print(f"Imported file: {file_path}")

def hide(root , vari , prop = None):
    if not prop: prop = lambda: root.pack(side=tk.LEFT, fill=tk.Y)
    if not vari.get():
        root.pack_forget()
    else:
        prop()
        litem.update_idletasks()

def load_image(block_name):
    try:
        img_path = grs(os.path.join('block', f"{block_name}.png"))
        img = Image.open(img_path)
        img = img.resize((20, 20), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        images[block_name] = img
        return img
    except:
        img_path = grs(os.path.join('block', 'info_update.png'))
        img = Image.open(img_path)
        img = img.resize((20, 20), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)
        images[block_name] = img
        return img

def insert_table(block_state, count, simple_type):
    if isinstance(block_state, BlockState):
        block_id = block_state._BlockState__block_id
        properties = block_state._BlockState__properties
        block_name = block_id.split(":")[-1]
        if properties:
            properties_str = ", ".join([f"{k}={v}" for k, v in properties.items()])  # 格式化属性
        else:
            properties_str = ""
    else:
        block_id = block_state
        block_name = block_id.split(":")[-1]
        properties_str = block_name
    block_id_display = cn_translate(block_name) if simple_type else block_id
    img = load_image(block_name)
    count_table.insert('', 'end', image=img, values=(block_id_display, str(count), convert_units(count), properties_str))
    litem.update_idletasks()

def output_data(classification : bool = False):
    global Block
    output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"),
                                                                                            ("CSV Chart files",
                                                                                            "*.csv")],
                                                           title="Litematica Analysis Data Save As",
                                                           initialfile=f'''{file_name.split(".")[0]}.txt''')
    if not output_file_path:
        return
    with codecs.open(output_file_path, 'w', encoding='utf-8-sig') as f:
        Block = dict(sorted(Block.items(), key=lambda x: x[1], reverse=True))  # Block = list
        if not classification:
            for val in Block:
                num = Block[val]
                id = val.split("[")[0].split(":")[-1]
                extension = os.path.splitext(output_file_path)[1].lower()
                if extension == ".csv":
                    f.write(f"{cn_translate(id)},{id},{num},{convert_units(num)}\n")
                else:
                    f.write(f"{num}[{convert_units(num)}] | {cn_translate(id)} [{id}]\n")
        else:
            for catigory in Cla_Block:
                if Cla_Block[catigory]:
                    f.write(f"\n{catigory}\n" + "-" * 20 + "\n")
                for val in Cla_Block[catigory]:
                    num = val[0]
                    id = str(val[1]).split("[")[0].split(":")[-1]
                    extension = os.path.splitext(output_file_path)[1].lower()
                    if extension == ".csv":
                        f.write(f"{cn_translate(id)},{id},{num},{convert_units(num)}\n")
                    else:
                        f.write(f"{num}[{convert_units(num)}] | {cn_translate(id)}[{id}]\n")
    os.startfile(output_file_path)

def Draw_Chart():
    ax1.clear()
    ax2.clear()

    sorted_block = sorted(Block.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_block[:5]
    other_count = sum(count for _, count in sorted_block[5:])
    labels1 = [cn_translate(block_id.split(":")[-1]) for block_id, _ in top_5]
    sizes1 = [count for _, count in top_5]
    if other_count > 0:
        labels1.append("其他")
        sizes1.append(other_count)
    ax1.pie(sizes1, labels=labels1, autopct='%1.1f%%', startangle=90)
    ax1.set_title("方块统计")

    cla_bl = {}
    for category, blocks in Cla_Block.items():
        if blocks:
            total = sum(count for count, _ in blocks)
            cla_bl[category] = total

    # 处理“其他”类别
    if "其他" in cla_bl:
        cat_other = cla_bl.pop("其他")
    else:
        cat_other = 0

    sorted_block = sorted(cla_bl.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_block[:5]
    other_count = sum(count for _, count in sorted_block[5:]) + cat_other
    labels2 = [cate for cate, _ in top_5]
    sizes2 = [count for _, count in top_5]
    if other_count > 0:
        labels2.append("其他")
        sizes2.append(other_count)
    ax2.pie(sizes2, labels=labels2, autopct='%1.1f%%', startangle=90)
    ax2.set_title("分类统计")

    canvas1.draw()
    canvas2.draw()
    return sorted_block[:1]


def start_analysis(simple_type):
    global schematic, Cla_Block, Block_pos, gl_view
    print(file_path)
    if not file_path:
        import_file()
    Cla_Block = {"实体": [], "羊毛": [], "陶瓦": [], "混凝土": [], "玻璃": [], "木制": [], "石质": [],
                 "其他岩石": [], "石英": [], "矿类": [], "自然类": [], "末地类": [], "地狱类": [], "海晶类": [],
                 "粘土类": [], "红石": [], "铁类": [], "容器": [], "液体": [], "其他": []}
    Block_pos = []
    Block.clear()
    count_table.delete(*count_table.get_children())
    schematic = Schematic.load(file_path)
    num = 0
    print(f"Schematic loaded: {schematic}")
    for region_index, region in enumerate(schematic.regions.values()):
        print(f"Analyzing region {region_index + 1}")
        size_x = region.maxx() - region.minx() + 1
        size_y = region.maxy() - region.miny() + 1
        size_z = region.maxz() - region.minz() + 1
        for x in range(size_x):
            for y in range(size_y):
                for z in range(size_z):
                    block_state = region._Region__palette[region._Region__blocks[x, y, z]]
                    block_id = block_state._BlockState__block_id
                    if block_id not in ["minecraft:air", "minecraft:cave_air", "minecraft:void_air"]:
                        Block_pos.append(((x, y, z), str(block_id)))
                        num += 1
                        if block_id not in ["minecraft:piston_head",
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
        for val in Block:
            id = val.split("[")[0].split(":")[-1]
            type = Category_Tran(id)
            if val.split("/")[0]=="E":
                Cla_Block["实体"].append((Block[val], val))
            elif type != "":
                Cla_Block[type].append((Block[val], val))
            else:
                Cla_Block["其他"].append((Block[val], val))
        print(f"{Cla_Block}")
        label_bottom.config(
            text=f"Size体积: {size_x}x{size_y}x{size_z} | Number数量: {num} | Times倍数: {time} | Types种类: {len(Block)}")

    top1 = Draw_Chart()
    sorted_block = sorted(Block.items(), key=lambda x: x[1], reverse=True)
    numbers = [item[1] for item in list(Block.items())]
    stat=statistics(numbers)
    if not stat: return
    a_s1.config(text="{:.1f}".format(stat[1]))
    a_s2.config(text="{:.1f}".format(stat[0]))
    a_s3.config(text=f"{num / (size_x * size_y * size_z) * 100:.1f}%")
    redly = (sum(n for n, _ in Cla_Block["红石"])+sum(n for n, _ in Cla_Block["容器"])) / (num-sorted_block[0][1] if len(Block)>5 else num)
    if num > 10:
        if redly>0.5:
            me_type = "红石机器"
        elif redly>=0.3:
            me_type = "生电红石"
        elif redly>=0.1:
            me_type = "生电机器"
        elif redly>=0.01:
            me_type = "结构性机器"
        elif redly<0.01:
            me_type = top1[0][0]+"建筑"
    else:
        me_type = "方块太少"
    a_m1.config(text=f"{redly*100:.1f}%")
    a_m2.config(text=f"{me_type}")
    fluid = sum(n for n, _ in Cla_Block["液体"])
    a_m3.config(text=f"{fluid / num * 100:.1f}%\n{fluid}")
    for index, (block_state, count) in enumerate(sorted_block):
        try:
            count = count * int(entry_times.get())
        except:
            count = count * 1
        insert_table(block_state, count, simple_type)

    if Do3d.get():
        if Pn3d.get():
            gl_view.destroy()
            if Li3d.get() and num>1000:
                if num>5000:
                    check = easygui.boolbox("Block Number over 5000, keep rendering?\n方块数量超过5千,是否继续渲染,可能会崩溃\n继续渲染将关闭旋转模式 Keep rendering will shut spinning mode",default_choice="是/Y 会变一次性",cancel_choice="取消/N 明智的选择")
                    if not check: return
                    threading.Thread(target=LitRender.main_render_loop(Block_pos,bool(False)), daemon=True).start()
                    return
                gl_view = OpenGLView(frame_3d, Block_pos, False, width=100, height=100, bg=color_map["PC"])
            else:
                gl_view = OpenGLView(frame_3d, Block_pos, bool(Sp3d.get()), width=100, height=100, bg=color_map["PC"])
            gl_view.pack(fill=tk.BOTH, expand=True)
            gl_view.after(1000, gl_view.redraw)
        else:
            if Li3d.get() and num>1000:
                if num>5000:
                    check = easygui.boolbox("Block Number over 5000, keep rendering?\n方块数量超过5千,是否继续渲染,可能会崩溃\n继续渲染将关闭旋转模式 Keep rendering will shut spinning mode",default_choice="是/Y 会变一次性",cancel_choice="取消/N 明智的选择")
                    if not check: return
                threading.Thread(target=LitRender.main_render_loop(Block_pos,bool(False)), daemon=True).start()
            else:
                threading.Thread(target=LitRender.main_render_loop(Block_pos,bool(Sp3d.get())), daemon=True).start()
    litem.update_idletasks()

if __name__ == "__main__":
    # 创建主窗口
    litem = tk.Tk()
    litem.title(f"Litematica Viewer投影查看器 v{APP_VERSION}")
    litem.iconbitmap(grs("icon.ico"))
    litem.geometry("1220x860")
    litem.configure(bg=color_map["MC"])

    LogVar = ["DoEntity", "DoLifr", "DoStat", "DoAnal", "Do3d", "Pn3d", "Li3d", "Sp3d"]
    menu = tk.Menu(litem)
    DoEntity = tk.IntVar()
    DoLifr = tk.IntVar()
    DoStat = tk.IntVar()
    DoAnal = tk.IntVar()
    Do3d = tk.IntVar()
    Pn3d = tk.IntVar()
    Li3d = tk.IntVar()
    Sp3d = tk.IntVar()
    if not os.path.exists(grs("log.txt")):
        with open(grs("log.txt"), "w") as file:
            file.write("11111111")  # d1:Entity, d2-4:Frame, d5-8:3D
            for logvar in LogVar:
                globals()[logvar] = tk.IntVar(value=1)
    else:
        with open(grs("log.txt"), "r") as file:
            fr = file.read()
            try:
                logvan = 0
                for logvar in LogVar:
                    globals()[logvar] = tk.IntVar(value=int(fr[logvan]))
                    logvan+=1

            except:
                for logvar in LogVar:
                    globals()[logvar] = tk.IntVar(value=1)

    menu_analysis = tk.Menu(menu, tearoff=0)
    menu_analysis.add_command(label="Import导入", command=import_file, font=(DefaultFont, 10))
    menu_analysis.add_command(label="Output导出", command=lambda:output_data(False), font=(DefaultFont, 10))
    menu_analysis.add_command(label="ClassifiedOutput分类导出", command=lambda:output_data(True), font=(DefaultFont, 10))
    menu_analysis.add_command(label="SimpleAnalysis简洁分析", command=lambda:threading.Thread(target=start_analysis(True), daemon=True).start(), font=(DefaultFont, 10))
    #menu_analysis.add_command(label="FullAnalysis全面分析", command=lambda:threading.Thread(target=start_analysis(True), daemon=False).start(), font=(DefaultFont, 10))
    menu_analysis.add_command(label="SpawnRegularShape生成图形投影", command=lambda : create_structure(entry_spawn.get(),f"minecraft:{cn_translate(entry_id.get(),False)}",
                                                            (entry_x.get(),entry_y.get(),entry_z.get()),
                                                            (entry_length.get(),entry_width.get(),entry_height.get()), False, 0, [False,False,False,False,False,False]
                                                            ), font=(DefaultFont, 10))
    menu_analysis.add_command(label="FillSpecificBlock替换特定方块", command=lambda : change_Schematic(schematic, text_change.get("1.0", tk.END), ((entry_min_x.get(),entry_max_x.get()),(entry_min_y.get(),entry_max_y.get()),(entry_min_z.get(),entry_max_z.get())), entry_spawn2.get() if entry_spawn2.get() else file_name.split(".")[0]+"_Modified"), font=(DefaultFont, 10))
    menu.add_cascade(label="DataAnalysis数据分析", menu=menu_analysis, font=(DefaultFont, 20))
    menu_AnaSet = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Setting设置",menu=menu_AnaSet, font=(DefaultFont, 20))
    menu_AnaSet.add_checkbutton(label="DoAnalysisEntity是否分析实体",variable=DoEntity, font=(DefaultFont, 10))
    menu_AnaSet.add_separator()
    menu_AnaSet.add_checkbutton(label="ShowLithemPannel是否显示投影面板",variable=DoLifr,command=lambda:hide(frame_spawn,DoLifr), font=(DefaultFont, 10))
    menu_AnaSet.add_checkbutton(label="ShowStatisticsPannel是否显示统计面板",variable=DoStat,command=lambda:hide(frame_data,DoStat), font=(DefaultFont, 10))
    menu_AnaSet.add_checkbutton(label="ShowAnalysisPannel是否显示分析面板", variable=DoAnal,command=lambda: hide(frame_middle,DoAnal), font=(DefaultFont, 10))
    menu_AnaSet.add_separator()
    menu_AnaSet.add_checkbutton(label="Allow3DRander是否3D渲染", variable=Do3d, font=(DefaultFont, 10))
    menu_AnaSet.add_checkbutton(label="Rander3DEmbeddedDisplay3D面板集中显示", variable=Pn3d, font=(DefaultFont, 10))
    menu_AnaSet.add_checkbutton(label="3DRanderLimit3D渲染限制|num>1000", variable=Li3d, font=(DefaultFont, 10))
    menu_AnaSet.add_checkbutton(label="Rotate3DRander3D渲染是否旋转", variable=Sp3d, font=(DefaultFont, 10))
    menu_Func = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Function功能",menu=menu_Func, font=(DefaultFont, 20))
    menu_Func.add_command(label="HeptaVersual跨版本 1.17+", command=lambda:litVerFix(7), font=(DefaultFont, 10))
    menu_Func.add_command(label="PentaVersual跨版本 1.15+", command=lambda:litVerFix(5), font=(DefaultFont, 10))
    menu_Func.add_command(label="TriVersual跨版本 1.13+", command=lambda:litVerFix(4), font=(DefaultFont, 10))
    menu_Func.add_separator()
    menu_Func.add_command(label="ContainerAnalysis容器分析", command=lambda:ConAly(), font=(DefaultFont, 10))
    menu_Func.add_command(label="3DRender手动3D渲染", command=lambda: threading.Thread(target=LitRender.main_render_loop(Block_pos,bool(False)), daemon=True).start(), font=(DefaultFont, 10))
    menu_Help = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Help帮助",menu=menu_Help, font=(DefaultFont, 20))
    menu_Help.add_command(label="About关于", command=lambda:webbrowser.open("https://github.com/albertchen857/LitematicaViewer"), font=(DefaultFont, 10))
    menu_Help.add_command(label="AboutCreater关于作者", command=lambda:webbrowser.open("https://space.bilibili.com/3494373232741268"), font=(DefaultFont, 10))
    menu_Help.add_command(label="ManualInstallPackages手动更新软件库", command=manual_install_pk, font=(DefaultFont, 10))

    litem.config(menu=menu, padx=10, pady=10)
    # 上容器
    frame_top = tk.Frame(litem)
    frame_top.configure(bg=color_map["PC"], bd=5)
    frame_top.pack(side=tk.TOP, fill=tk.X)

    btn_import = tk.Button(frame_top, text="Import导入", command=import_file, font=(DefaultFont, 10))
    btn_import.configure(bg=color_map["MC"],fg=color_map["TT"],relief='ridge')
    btn_import.pack(side=tk.LEFT, padx=5, pady=5)
    btn_simstart = tk.Button(frame_top, text="SIMPLE Analysis简洁分析", command=lambda:threading.Thread(target=start_analysis(True), daemon=True).start(), font=(DefaultFont, 10))
    btn_simstart.configure(bg=color_map["MC"],fg=color_map["TT"],relief='ridge')
    btn_simstart.pack(side=tk.LEFT, padx=5, pady=5)

    btn_github = tk.Button(frame_top, text="GitHub", command=lambda:webbrowser.open("https://github.com/albertchen857/LitematicaViewer"), font=(DefaultFont, 10))
    btn_github.configure(bg="black",fg=color_map["BG"],relief='groove')
    btn_github.pack(side=tk.RIGHT, padx=5, pady=5)
    btn_bilibili = tk.Button(frame_top, text="Bilibili", command=lambda:webbrowser.open("https://space.bilibili.com/3494373232741268"), font=(DefaultFont, 10))
    btn_bilibili.configure(bg="#FF6699", fg=color_map["BG"],relief='groove')
    btn_bilibili.pack(side=tk.RIGHT, padx=5, pady=5)


    # 创建 PanedWindow
    paned_windowh = ttk.PanedWindow(litem, orient=tk.HORIZONTAL)
    paned_windowh.pack(fill="both", expand=True)

    # 调整样式
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TFrame", background=color_map["BG"])
    style.configure("TPanedwindow", background=color_map["BG"])
    style.configure("TPanedwindow.Sash", background=color_map["MC"])


    # lith容器
    frame_spawn = tk.Frame(paned_windowh, bg=color_map["PC"])
    paned_windowh.add(frame_spawn, weight=1)
    hide(frame_spawn, DoLifr)
    # - 右容器上部：frame_spawn_new
    frame_spawn_new = tk.Frame(frame_spawn, bg=color_map["MC"])
    frame_spawn_new.pack(side=tk.TOP, fill=tk.X,  padx=20)
    frame_new_title = tk.Label(frame_spawn_new, text="生成图形投影", font=(DefaultFont, 18), bg=color_map["MC"], fg=color_map["TT"])
    frame_new_title.grid(row=0, column=0, padx=5, pady=5, columnspan=4)
    # -- ID 输入框
    label_id = tk.Label(frame_spawn_new, text="方块ID", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_id.grid(row=1, column=0, padx=5, pady=5)
    entry_id = tk.Entry(frame_spawn_new, width=20, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_id.grid(row=1, column=1, padx=5, pady=5, columnspan=3)
    # -- XYZ 长宽高输入框
    label_xyz = tk.Label(frame_spawn_new, text="原点XYZ", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_xyz.grid(row=2, column=0, padx=5, pady=5)
    label_lwh = tk.Label(frame_spawn_new, text="宽高长Size", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_lwh.grid(row=3, column=0, padx=5, pady=5)
    entry_x = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_x.grid(row=2, column=1, padx=2, pady=5)
    entry_y = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_y.grid(row=2, column=2, padx=2, pady=5)
    entry_z = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_z.grid(row=2, column=3, padx=2, pady=5)
    entry_length = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_length.grid(row=3, column=3, padx=2, pady=5)
    entry_width = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_width.grid(row=3, column=2, padx=2, pady=5)
    entry_height = tk.Entry(frame_spawn_new, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_height.grid(row=3, column=1, padx=2, pady=5)
    # -- Hollow 单选框和 Thickness 输入框
    '''chollow = tk.IntVar()
    lable_thickness = tk.Label(frame_spawn_new, text="厚度\nThickness", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    lable_thickness.grid(row=4, column=0, padx=5, pady=5)
    entry_thickness = tk.Entry(frame_spawn_new, width=13, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_thickness.grid(row=4, column=1, padx=5, pady=5, columnspan=2)
    check_hollow = tk.Checkbutton(frame_spawn_new, text="空心Hollow", variable=chollow, bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10))
    check_hollow.grid(row=5, column=0, padx=5, pady=5)
    # -- 上下左右前后复选框
    cu = tk.IntVar(value=1)
    cd = tk.IntVar(value=1)
    cl = tk.IntVar(value=1)
    cr = tk.IntVar(value=1)
    cf = tk.IntVar(value=1)
    cb = tk.IntVar(value=1)
    check_up = tk.Checkbutton(frame_spawn_new, text="上U", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cu)
    check_up.grid(row=5, column=1, padx=2, pady=2)
    check_down = tk.Checkbutton(frame_spawn_new, text="下D", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cd)
    check_down.grid(row=5, column=2, padx=2, pady=2)
    check_left = tk.Checkbutton(frame_spawn_new, text="左L", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cl)
    check_left.grid(row=5, column=3, padx=2, pady=2)
    check_right = tk.Checkbutton(frame_spawn_new, text="右R", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cr)
    check_right.grid(row=6, column=1, padx=2, pady=2)
    check_front = tk.Checkbutton(frame_spawn_new, text="前F", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cf)
    check_front.grid(row=6, column=2, padx=2, pady=2)
    check_back = tk.Checkbutton(frame_spawn_new, text="后B", bg=color_map["MC"], fg=color_map["TT"], font=(DefaultFont, 10), variable=cb)
    check_back.grid(row=6, column=3, padx=2, pady=2)'''

    label_spawn = tk.Label(frame_spawn_new, text="文件名File", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_spawn.grid(row=7, column=0, padx=5, pady=5)
    entry_spawn = tk.Entry(frame_spawn_new, width=20, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_spawn.grid(row=7, column=1, columnspan=3,padx=2, pady=2)

    btn_spawn = tk.Button(frame_spawn_new, text="Spawn生成", font=(DefaultFont, 10, "bold"),
                          command=lambda : create_structure(entry_spawn.get(),f"minecraft:{cn_translate(entry_id.get(),False)}",
                                                            (entry_x.get(),entry_y.get(),entry_z.get()),
                                                            (entry_length.get(),entry_width.get(),entry_height.get()), False, 0, [False,False,False,False,False,False]
                                                            )) # bool(chollow), int(entry_thickness.get() if entry_thickness.get() else 0),[cu.get(),cd.get(),cl.get(),cr.get(),cf.get(),cb.get()]
    btn_spawn.configure(bg=color_map["BG"], fg=color_map["MC"], relief='ridge')
    btn_spawn.grid(row=8, column=0, padx=2, pady=2, columnspan=4)
    '''label_warn = tk.Label(frame_spawn_new, text="Hollow Not Usable", font=(DefaultFont, 10), bg=color_map["TT"], fg=color_map["Red"])
    label_warn.grid(row=8, column=2, padx=5, pady=5, columnspan=2)'''
    label_tip = tk.Label(frame_spawn_new, text="ID输入可以为纯英文或中文名", font=(DefaultFont, 10, "bold"), bg=color_map["MC"], fg=color_map["Red"])
    label_tip.grid(row=9, column=0, padx=5, pady=5, columnspan=4)
    # - 右容器下部：frame_spawn_change
    frame_spawn_change = tk.Frame(frame_spawn, bg=color_map["MC"])
    frame_spawn_change.pack(side=tk.TOP, fill=tk.X, pady=10, padx=20)
    frame_change_title = tk.Label(frame_spawn_change, text="替换特定方块", font=(DefaultFont, 18), bg=color_map["MC"],fg=color_map["TT"])
    frame_change_title.grid(row=0, column=0, padx=5, pady=20, columnspan=4)

    # -- Limit 标签和 XYZ 输入框
    label_min = tk.Label(frame_spawn_change, text="最小限制\nMinimize\nLimit XYZ", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_min.grid(row=1, column=0, padx=5, pady=5)
    entry_min_x = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_min_x.grid(row=1, column=1, padx=2, pady=5)
    entry_min_y = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_min_y.grid(row=1, column=2, padx=2, pady=5)
    entry_min_z = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_min_z.grid(row=1, column=3, padx=2, pady=5)
    label_max = tk.Label(frame_spawn_change, text="最大限制\nMaximize\nLimit XYZ", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_max.grid(row=2, column=0, padx=5, pady=5)
    entry_max_x = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_max_x.grid(row=2, column=1, padx=2, pady=5)
    entry_max_y = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_max_y.grid(row=2, column=2, padx=2, pady=5)
    entry_max_z = tk.Entry(frame_spawn_change, width=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_max_z.grid(row=2, column=3, padx=2, pady=5)

    # -- Change 标签和多行输入框
    label_change = tk.Label(frame_spawn_change, text="替换表\nChange", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_change.grid(row=3, column=0, padx=5, pady=5)
    text_change = tk.Text(frame_spawn_change,width=20, height=5, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    text_change.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

    label_spawn2 = tk.Label(frame_spawn_change, text="文件名File", font=(DefaultFont, 12), bg=color_map["MC"], fg=color_map["TT"])
    label_spawn2.grid(row=4, column=0, padx=5, pady=5)
    entry_spawn2 = tk.Entry(frame_spawn_change, width=20, bg=color_map["BG"], fg=color_map["PC"], font=(DefaultFont, 10))
    entry_spawn2.grid(row=4, column=1, columnspan=3,padx=2, pady=2)

    btn_spawn2 = tk.Button(frame_spawn_change, text="Spawn生成", font=(DefaultFont, 10, "bold"), command=lambda : change_Schematic(schematic, CS_trans_dict(text_change.get("1.0", tk.END)), ((entry_min_x.get(),entry_max_x.get()),(entry_min_y.get(),entry_max_y.get()),(entry_min_z.get(),entry_max_z.get())), entry_spawn2.get() if entry_spawn2.get() else file_name.split(".")[0]+"_Modified"))
    btn_spawn2.configure(bg=color_map["BG"], fg=color_map["MC"], relief='ridge')
    btn_spawn2.grid(row=5, column=0, padx=2, pady=2, columnspan=4)
    '''label_warn2 = tk.Label(frame_spawn_change, text="Nothing", font=(DefaultFont, 10), bg=color_map["TT"], fg=color_map["Red"])
    label_warn2.grid(row=5, column=2, padx=5, pady=5, columnspan=2)'''
    label_tip2 = tk.Label(frame_spawn_change, text="替换表= 旧方块-新方块,...", font=(DefaultFont, 10, "bold"), bg=color_map["MC"], fg=color_map["Red"])
    label_tip2.grid(row=6, column=0, padx=5, pady=5, columnspan=4)


    # 中容器
    frame_middle = tk.Frame(paned_windowh, bg=color_map["MC"])
    paned_windowh.add(frame_middle, weight=1)
    hide(frame_middle,DoAnal,lambda :frame_middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True))
    # - 中容器顶部
    frame_middle_top = tk.Frame(frame_middle, bg=color_map["MC"])
    frame_middle_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    label_middle = tk.Label(frame_middle_top, text="LitematicaViewer投影查看器", font=("Helvetica", 30, 'bold'))
    label_middle.configure(bg=color_map["MC"], fg=color_map["TT"], bd=5)
    label_middle.pack(fill=tk.Y)

    label_bottom = tk.Label(frame_middle_top, text="Size体积 | Number数量 | Times倍数 | Types种类", font=("Helvetica", 14, "bold"))
    label_bottom.configure(bg=color_map["MC"], fg=color_map["BG"], bd=5)
    label_bottom.pack(side=tk.LEFT, fill=tk.X, padx=20, pady=10)

    frame_Times = tk.Frame(frame_middle_top, bg=color_map["MC"])
    frame_Times.pack(side=tk.RIGHT, fill=tk.Y, padx=40)

    label_times = tk.Label(frame_Times, text="Times倍数", font=("microsoft yahei ui", 16, "bold"))
    label_times.configure(bg=color_map["MC"], fg=color_map["TT"])
    label_times.pack(side=tk.LEFT, padx=5)

    entry_times = tk.Entry(frame_Times, width=10, bg=color_map["BG"], fg=color_map["PC"], font=("Helvetica", 10))
    entry_times.pack(side=tk.RIGHT, padx=5)

    underscore1 = tk.Frame(frame_middle, bg=color_map["BG"])
    underscore1.pack( padx=40, pady=10)

    table_sty = ttk.Style()
    table_sty.configure("Treeview", font=(DefaultFont, 12), rowheight=25, background=color_map["PC"], foreground=color_map["BG"])
    table_sty.configure("Treeview.Heading", font=("Helvetica", 14, "bold"), background=color_map["PC"], foreground=color_map["TT"])
    table_sty.map('Treeview', background=[('selected', color_map["MC"])])
    # 中容器表格
    frame_chart = tk.Frame(frame_middle, bg=color_map["TT"], background=color_map["MC"])
    frame_chart.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    sroll = tk.Scrollbar(frame_chart, orient="vertical")
    sroll.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
    count_table = ttk.Treeview(frame_chart, column=('blockID', 'num', 'unit', 'properties'), height=7, yscrollcommand=sroll.set)
    sroll.config(command=count_table.yview)
    count_table.heading('blockID', text='ID/名字', anchor="center")
    count_table.heading('num', text='Num数量', anchor="center")
    count_table.heading('unit', text='Unit单位数', anchor="center")
    count_table.heading('properties', text='Prop属性', anchor="center")
    count_table.column("#0", width=2, anchor="e")
    count_table.column("blockID", width=150)
    count_table.column("num", width=50)
    count_table.column("unit", width=50)
    count_table.column("properties", width=200)
    count_table.config(height=20)
    count_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=10)

    #统计容器
    frame_data = tk.Frame(frame_chart, bg=color_map["PC"])
    hide(frame_data, DoStat, lambda: frame_data.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True))

    frame_3d = tk.Frame(frame_data, bg=color_map["PC"])
    frame_3d.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
    frame_pie1 = tk.Frame(frame_data, bg=color_map["PC"])
    frame_pie1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2.5, pady=5)
    frame_pie2 = tk.Frame(frame_data, bg=color_map["PC"])
    frame_pie2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2.5, pady=5)
    frame_stati = tk.Frame(frame_data, bg=color_map["PC"])
    frame_stati.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

    gl_view = OpenGLView(frame_3d, [((0, 0, 0), 'minecraft:dirt')], False, width=100, height=100, bg=color_map["PC"])
    gl_view.pack(fill=tk.BOTH, expand=True)
    gl_view.after(1000, gl_view.redraw)

    fig1 = Figure(figsize=(4, 3), dpi=60)
    ax1 = fig1.add_subplot(111)
    canvas1 = FigureCanvasTkAgg(fig1, master=frame_pie1)
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    fig2 = Figure(figsize=(4, 3), dpi=60)
    ax2 = fig2.add_subplot(111)
    canvas2 = FigureCanvasTkAgg(fig2, master=frame_pie2)
    canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    l_st = tk.Label(frame_stati, text="数据统计", font=(DefaultFont, 16, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_st.grid(row=0, column=0, padx=2, pady=5, columnspan=6)
    l_s1 = tk.Label(frame_stati, text="中位数", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_s1.grid(row=2, column=0, padx=2, pady=5)
    l_s2 = tk.Label(frame_stati, text="四分位距", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_s2.grid(row=2, column=2, padx=2, pady=5)
    l_s3 = tk.Label(frame_stati, text="密度", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_s3.grid(row=3, column=0, padx=2, pady=5)
    l_m1 = tk.Label(frame_stati, text="红石偏度", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_m1.grid(row=1, column=2, padx=2, pady=5)
    l_m2 = tk.Label(frame_stati, text="材质", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_m2.grid(row=1, column=0, padx=2, pady=5)
    l_m3 = tk.Label(frame_stati, text="液体偏度", font=(DefaultFont, 12, "bold"), bg=color_map["MC"], fg=color_map["TT"])
    l_m3.grid(row=3, column=2, padx=2, pady=5)

    a_s1 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_s1.grid(row=2, column=1, padx=5, pady=5)
    a_s2 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_s2.grid(row=2, column=3, padx=5, pady=5)
    a_s3 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_s3.grid(row=3, column=1, padx=5, pady=5)
    a_m1 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_m1.grid(row=1, column=3, padx=5, pady=5)
    a_m2 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_m2.grid(row=1, column=1, padx=5, pady=5)
    a_m3 = tk.Label(frame_stati, text="0", font=(DefaultFont, 12), bg=color_map["PC"], fg=color_map["BG"])
    a_m3.grid(row=3, column=3, padx=5, pady=5)

    litem.mainloop()



