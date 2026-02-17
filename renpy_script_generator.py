import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import json
import os
import re

# 变量名校验正则：仅允许字母、数字、下划线，不能以数字开头，无中文
VAR_NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

class ConfigWindow(tk.Toplevel):
    """角色配置文件编辑窗口"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("角色配置文件编辑")
        self.geometry("550x600")
        self.minsize(550, 600)
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")
        self.parent = parent
        
        self.config_characters = []
        
        self.base_font = font.Font(family="Microsoft YaHei", size=11)
        self.title_font = font.Font(family="Microsoft YaHei", size=12, weight="bold")
        
        self._init_ui()
    
    def _init_ui(self):
        lbl_title = ttk.Label(self, text="角色配置管理", font=self.title_font)
        lbl_title.pack(pady=10)
        
        frame_list = ttk.LabelFrame(self, text="角色列表", padding=(10, 8))
        frame_list.pack(fill="both", padx=15, pady=5, expand=True)
        
        self.lb_config_chars = tk.Listbox(
            frame_list,
            font=self.base_font,
            width=50,
            height=15,
            bd=1,
            relief="solid",
            selectbackground="#4a90e2",
            selectforeground="white"
        )
        self.lb_config_chars.pack(side="left", fill="both", padx=5, pady=5, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.lb_config_chars.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb_config_chars.config(yscrollcommand=scrollbar.set)
        
        frame_input = ttk.LabelFrame(self, text="角色信息编辑", padding=(10, 8))
        frame_input.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(frame_input, text="角色变量名（预定义值，仅字母/数字/下划线）：", font=self.base_font).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_var_name = ttk.Entry(frame_input, font=self.base_font, width=25)
        self.entry_var_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_input, text="角色显示名称（可中文）：", font=self.base_font).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_display_name = ttk.Entry(frame_input, font=self.base_font, width=25)
        self.entry_display_name.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        frame_input.columnconfigure(1, weight=1)
        
        frame_ops = ttk.Frame(self, padding=(10, 8))
        frame_ops.pack(fill="x", padx=15, pady=5)
        
        btn_style = ttk.Style()
        btn_style.configure("Config.TButton", font=self.base_font, padding=(8, 4))
        
        btn_add = ttk.Button(frame_ops, text="添加角色", command=self.add_character, style="Config.TButton")
        btn_add.grid(row=0, column=0, padx=10, pady=5)
        
        btn_del = ttk.Button(frame_ops, text="删除选中角色", command=self.delete_character, style="Config.TButton")
        btn_del.grid(row=0, column=1, padx=10, pady=5)
        
        btn_save_config = ttk.Button(frame_ops, text="保存配置文件", command=self.save_config, style="Config.TButton")
        btn_save_config.grid(row=1, column=0, padx=10, pady=5)
        
        btn_import_to_editor = ttk.Button(frame_ops, text="导入到编辑界面", command=self.import_to_editor, style="Config.TButton")
        btn_import_to_editor.grid(row=1, column=1, padx=10, pady=5)
        
        frame_ops.columnconfigure(0, weight=1)
        frame_ops.columnconfigure(1, weight=1)
    
    def add_character(self):
        var_name = self.entry_var_name.get().strip()
        display_name = self.entry_display_name.get().strip()
        
        if not var_name:
            messagebox.showwarning("警告", "角色变量名不能为空！", parent=self)
            return
        if not VAR_NAME_PATTERN.match(var_name):
            messagebox.showwarning("警告", "变量名仅允许字母、数字、下划线，且不能以数字开头，禁止中文！", parent=self)
            return
        for char in self.config_characters:
            if char["var_name"] == var_name:
                messagebox.showinfo("提示", f"变量名「{var_name}」已存在！", parent=self)
                return
        
        if not display_name:
            display_name = var_name
        
        self.config_characters.append({
            "var_name": var_name,
            "display_name": display_name
        })
        display_text = f"{var_name} - {display_name}"
        self.lb_config_chars.insert(tk.END, display_text)
        
        self.entry_var_name.delete(0, tk.END)
        self.entry_display_name.delete(0, tk.END)
    
    def delete_character(self):
        selected_index = self.lb_config_chars.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请先选中要删除的角色！", parent=self)
            return
        
        selected_index = selected_index[0]
        char_info = self.config_characters[selected_index]
        if messagebox.askyesno("确认", f"是否删除角色「{char_info['var_name']} - {char_info['display_name']}」？", parent=self):
            del self.config_characters[selected_index]
            self.lb_config_chars.delete(selected_index)
    
    def save_config(self):
        if not self.config_characters:
            messagebox.showwarning("警告", "请先添加至少一个角色！", parent=self)
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("角色配置文件", "*.json"), ("所有文件", "*.*")],
            title="保存角色配置文件",
            parent=self
        )
        if not file_path:
            return
        
        config_data = {"characters": self.config_characters}
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", f"配置文件已保存到：\n{file_path}", parent=self)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}", parent=self)
    
    def import_to_editor(self):
        if not self.config_characters:
            messagebox.showwarning("警告", "请先添加至少一个角色！", parent=self)
            return
        
        self.parent.characters.clear()
        self.parent.lb_characters.delete(0, tk.END)
        
        for char in self.config_characters:
            self.parent.characters.append(char)
            display_text = f"{char['var_name']} - {char['display_name']}"
            self.parent.lb_characters.insert(tk.END, display_text)
        
        self.parent.update_character_combobox()
        messagebox.showinfo("成功", f"已导入{len(self.config_characters)}个角色到编辑界面！", parent=self)
        self.destroy()

class StartWindow(tk.Toplevel):
    """开始界面窗口"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ren'Py脚本生成工具 - 开始界面")
        self.geometry("500x400")
        self.minsize(500, 400)
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        self.parent = parent
        
        parent.withdraw()
        
        self.base_font = font.Font(family="Microsoft YaHei", size=12)
        self.title_font = font.Font(family="Microsoft YaHei", size=16, weight="bold")
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self._init_ui()
    
    def _init_ui(self):
        lbl_title = ttk.Label(self, text="Ren'Py 对话脚本生成工具", font=self.title_font)
        lbl_title.pack(pady=50)
        
        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(pady=20)
        
        btn_style = ttk.Style()
        btn_style.configure("Start.TButton", font=self.base_font, padding=(15, 10), width=22)
        
        btn_new_file = ttk.Button(frame_buttons, text="新建脚本文件", command=self.new_script_file, style="Start.TButton")
        btn_new_file.pack(pady=10)
        
        btn_open_file = ttk.Button(frame_buttons, text="打开临时脚本文件", command=self.open_script_file, style="Start.TButton")
        btn_open_file.pack(pady=10)
        
        btn_new_config = ttk.Button(frame_buttons, text="新建角色配置文件", command=self.new_config_file, style="Start.TButton")
        btn_new_config.pack(pady=10)
    
    def new_script_file(self):
        self.parent.reset_editor()
        self.parent.deiconify()
        self.destroy()
    
    def open_script_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("临时脚本文件", "*.json"), ("所有文件", "*.*")],
            title="打开临时脚本文件",
            parent=self
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                temp_data = json.load(f)
            
            required_keys = ["characters", "current_label", "dialogues"]
            if not all(key in temp_data for key in required_keys):
                messagebox.showerror("错误", "文件格式错误，不是有效的临时脚本文件！", parent=self)
                return
            
            self.parent.load_temp_data(temp_data)
            self.parent.deiconify()
            self.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("错误", "文件损坏，无法解析！", parent=self)
        except Exception as e:
            messagebox.showerror("错误", f"打开失败：{str(e)}", parent=self)
    
    def new_config_file(self):
        config_win = ConfigWindow(self.parent)
        config_win.grab_set()
    
    def on_close(self):
        self.parent.destroy()
        self.destroy()

class RenPyScriptGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ren'Py 对话脚本生成工具 - 编辑界面")
        self.geometry("950x780")
        self.minsize(900, 700)
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")
        
        self.drag_item = None
        self.drag_index = -1
        
        self.characters = []
        self.dialogues = []
        self.current_label = tk.StringVar(value="start")
        
        self.init_fonts()
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self._init_ui()
        self.start_window = StartWindow(self)
    
    def init_fonts(self):
        self.base_font = font.Font(family="Microsoft YaHei", size=11)
        self.title_font = font.Font(family="Microsoft YaHei", size=12, weight="bold")
        self.btn_font = font.Font(family="Microsoft YaHei", size=11)
        
        tk.TkDefaultFont = self.base_font
        ttk.Style().configure('.', font=self.base_font)
    
    def _init_ui(self):
        """初始化编辑界面布局（按钮移至上方+文本框新增滚动条）"""
        # ========== 顶部：场景设置区 ==========
        frame_label = ttk.LabelFrame(self, text="场景设置（Label标签）", style="Title.TLabelframe")
        frame_label.pack(fill="x", padx=15, pady=8)
        frame_label.configure(padding=(10, 8))
        
        lbl_label = ttk.Label(frame_label, text="场景名称：", font=self.base_font)
        lbl_label.grid(row=0, column=0, padx=8, pady=8)
        
        entry_label = ttk.Entry(frame_label, textvariable=self.current_label, font=self.base_font)
        entry_label.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        entry_label.configure(width=50)
        frame_label.columnconfigure(1, weight=1)
        
        # ========== 顶部：操作按钮区（移至此处） ==========
        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(fill="x", padx=15, pady=8)
        
        btn_style = ttk.Style()
        btn_style.configure("Custom.TButton", font=self.btn_font, padding=(8, 4))
        
        btn_new = ttk.Button(
            frame_buttons, 
            text="新建脚本", 
            command=self.new_script,
            style="Custom.TButton"
        )
        btn_new.grid(row=0, column=0, padx=8, pady=5)
        
        btn_save_temp = ttk.Button(
            frame_buttons, 
            text="保存临时文件", 
            command=self.save_temp_file,
            style="Custom.TButton"
        )
        btn_save_temp.grid(row=0, column=1, padx=8, pady=5)
        
        btn_open_temp = ttk.Button(
            frame_buttons, 
            text="打开临时文件", 
            command=self.open_temp_file,
            style="Custom.TButton"
        )
        btn_open_temp.grid(row=0, column=2, padx=8, pady=5)
        
        btn_generate = ttk.Button(
            frame_buttons, 
            text="生成Ren'Py脚本", 
            command=self.generate_script,
            style="Custom.TButton"
        )
        btn_generate.grid(row=0, column=3, padx=8, pady=5)
        
        btn_save = ttk.Button(
            frame_buttons, 
            text="保存脚本文件", 
            command=self.save_script,
            style="Custom.TButton"
        )
        btn_save.grid(row=0, column=4, padx=8, pady=5)
        
        # ========== 主体容器 ==========
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", padx=15, pady=8, expand=True)
        
        # ========== 左侧：角色管理区 ==========
        frame_char = ttk.LabelFrame(main_frame, text="角色管理", style="Title.TLabelframe")
        frame_char.pack(side="left", fill="y", padx=(0, 10), pady=0, ipady=8)
        frame_char.configure(width=260, padding=(10, 8))
        
        self.lb_characters = tk.Listbox(
            frame_char, 
            font=self.base_font,
            width=30, 
            height=15,
            bd=1,
            relief="solid",
            selectbackground="#4a90e2",
            selectforeground="white"
        )
        self.lb_characters.pack(padx=8, pady=8)
        
        frame_char_input = ttk.LabelFrame(frame_char, text="新增角色", padding=(8, 6))
        frame_char_input.pack(padx=8, pady=5, fill="x")
        
        ttk.Label(frame_char_input, text="变量名（预定义值）：", font=self.base_font).pack(padx=5, pady=3, fill="x")
        self.entry_var_name = ttk.Entry(frame_char_input, font=self.base_font, width=25)
        self.entry_var_name.pack(padx=5, pady=3, fill="x")
        
        ttk.Label(frame_char_input, text="显示名称：", font=self.base_font).pack(padx=5, pady=3, fill="x")
        self.entry_display_name = ttk.Entry(frame_char_input, font=self.base_font, width=25)
        self.entry_display_name.pack(padx=5, pady=3, fill="x")
        
        frame_char_btns = ttk.Frame(frame_char)
        frame_char_btns.pack(padx=8, pady=5, fill="x")
        
        btn_add_char = ttk.Button(
            frame_char_btns, 
            text="添加角色", 
            command=self.add_character,
            style="Custom.TButton"
        )
        btn_add_char.pack(padx=5, pady=3, fill="x")
        
        btn_del_char = ttk.Button(
            frame_char_btns, 
            text="删除选中角色", 
            command=self.delete_character,
            style="Custom.TButton"
        )
        btn_del_char.pack(padx=5, pady=3, fill="x")
        
        btn_import_config = ttk.Button(
            frame_char_btns,
            text="从配置文件导入角色",
            command=self.import_from_config,
            style="Custom.TButton"
        )
        btn_import_config.pack(padx=5, pady=3, fill="x")
        
        # ========== 右侧：内容编辑+列表区 ==========
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # ========== 右侧上半：内容编辑区（文本框新增滚动条） ==========
        frame_content_edit = ttk.LabelFrame(right_frame, text="内容编辑", style="Title.TLabelframe")
        frame_content_edit.pack(fill="x", padx=0, pady=0)
        frame_content_edit.configure(padding=(10, 8))
        
        # 角色对话子区域（文本框新增滚动条）
        frame_character_dialog = ttk.LabelFrame(frame_content_edit, text="角色对话", style="Sub.TLabelframe")
        frame_character_dialog.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame_character_dialog, text="选择角色：", font=self.base_font).grid(row=0, column=0, padx=8, pady=8)
        
        self.cb_character = ttk.Combobox(
            frame_character_dialog, 
            state="readonly",
            font=self.base_font,
            width=35
        )
        self.cb_character.grid(row=0, column=1, columnspan=2, padx=8, pady=8, sticky="ew")
        
        ttk.Label(frame_character_dialog, text="对话内容：", font=self.base_font).grid(row=1, column=0, padx=8, pady=8, sticky="n")
        
        # 角色对话文本框+滚动条容器
        frame_char_dialog_text = ttk.Frame(frame_character_dialog)
        frame_char_dialog_text.grid(row=1, column=1, columnspan=2, padx=8, pady=8, sticky="nsew")
        
        self.txt_character_dialog = tk.Text(
            frame_char_dialog_text, 
            font=self.base_font,
            height=4,
            width=50,
            bd=1,
            relief="solid"
        )
        self.txt_character_dialog.pack(side="left", fill="both", expand=True)
        
        # 新增角色对话滚动条
        scrollbar_char_dialog = ttk.Scrollbar(frame_char_dialog_text, orient="vertical", command=self.txt_character_dialog.yview)
        scrollbar_char_dialog.pack(side="right", fill="y")
        self.txt_character_dialog.config(yscrollcommand=scrollbar_char_dialog.set)
        
        btn_add_character_dialog = ttk.Button(
            frame_character_dialog, 
            text="添加角色对话", 
            command=self.add_character_dialogue,
            style="Custom.TButton"
        )
        btn_add_character_dialog.grid(row=2, column=0, columnspan=3, pady=8)
        
        frame_character_dialog.columnconfigure(1, weight=1)
        
        # 旁白子区域（文本框新增滚动条）
        frame_narration = ttk.LabelFrame(frame_content_edit, text="旁白内容", style="Sub.TLabelframe")
        frame_narration.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(frame_narration, text="旁白文本：", font=self.base_font).grid(row=0, column=0, padx=8, pady=8, sticky="n")
        
        # 旁白文本框+滚动条容器
        frame_narration_text = ttk.Frame(frame_narration)
        frame_narration_text.grid(row=0, column=1, columnspan=2, padx=8, pady=8, sticky="nsew")
        
        self.txt_narration = tk.Text(
            frame_narration_text, 
            font=self.base_font,
            height=4,
            width=50,
            bd=1,
            relief="solid"
        )
        self.txt_narration.pack(side="left", fill="both", expand=True)
        
        # 新增旁白滚动条
        scrollbar_narration = ttk.Scrollbar(frame_narration_text, orient="vertical", command=self.txt_narration.yview)
        scrollbar_narration.pack(side="right", fill="y")
        self.txt_narration.config(yscrollcommand=scrollbar_narration.set)
        
        btn_add_narration = ttk.Button(
            frame_narration, 
            text="添加旁白", 
            command=self.add_narration,
            style="Custom.TButton"
        )
        btn_add_narration.grid(row=1, column=0, columnspan=3, pady=8)
        
        frame_narration.columnconfigure(1, weight=1)
        
        # ========== 右侧下半：内容列表+排序按钮 ==========
        frame_dialog_list = ttk.LabelFrame(right_frame, text="内容列表（可拖动排序）", style="Title.TLabelframe")
        frame_dialog_list.pack(fill="both", padx=0, pady=8, expand=True)
        frame_dialog_list.configure(padding=(10, 8))
        
        frame_sort_btns = ttk.Frame(frame_dialog_list)
        frame_sort_btns.pack(fill="x", padx=5, pady=5)
        
        btn_move_up = ttk.Button(
            frame_sort_btns, 
            text="上移选中项", 
            command=self.move_item_up,
            style="Custom.TButton"
        )
        btn_move_up.pack(side="left", padx=5, pady=2)
        
        btn_move_down = ttk.Button(
            frame_sort_btns, 
            text="下移选中项", 
            command=self.move_item_down,
            style="Custom.TButton"
        )
        btn_move_down.pack(side="left", padx=5, pady=2)
        
        btn_del_dialog = ttk.Button(
            frame_sort_btns, 
            text="删除选中内容", 
            command=self.delete_content,
            style="Custom.TButton"
        )
        btn_del_dialog.pack(side="left", padx=5, pady=2)
        
        self.lb_contents = tk.Listbox(
            frame_dialog_list,
            font=self.base_font,
            width=65,
            height=15,
            bd=1,
            relief="solid",
            selectbackground="#4a90e2",
            selectforeground="white"
        )
        self.lb_contents.pack(side="left", fill="both", padx=5, pady=5, expand=True)
        
        scrollbar = ttk.Scrollbar(
            frame_dialog_list, 
            orient="vertical", 
            command=self.lb_contents.yview
        )
        scrollbar.pack(side="right", fill="y", padx=0, pady=5)
        self.lb_contents.config(yscrollcommand=scrollbar.set)
        
        self.lb_contents.bind("<ButtonPress-1>", self.on_drag_start)
        self.lb_contents.bind("<B1-Motion>", self.on_drag_motion)
        self.lb_contents.bind("<ButtonRelease-1>", self.on_drag_end)
        
        self._init_styles()
    
    def _init_styles(self):
        style = ttk.Style()
        
        style.configure(".", background="#f0f0f0", font=self.base_font)
        
        style.configure(
            "Title.TLabelframe",
            font=self.title_font,
            padding=(10, 8),
            background="#f0f0f0"
        )
        style.configure(
            "Title.TLabelframe.Label",
            font=self.title_font,
            background="#f0f0f0"
        )
        
        style.configure(
            "Sub.TLabelframe",
            font=self.base_font,
            padding=(8, 6),
            background="#f0f0f0"
        )
        style.configure(
            "Sub.TLabelframe.Label",
            font=self.base_font,
            background="#f0f0f0"
        )
        
        style.configure(
            "Custom.TButton",
            font=self.btn_font,
            padding=(8, 4),
            relief="flat",
            background="#4a90e2",
            foreground="white"
        )
        style.map(
            "Custom.TButton",
            background=[("active", "#357abd"), ("pressed", "#28598f")]
        )
    
    def update_character_combobox(self):
        char_options = [f"{c['var_name']} - {c['display_name']}" for c in self.characters]
        self.cb_character['values'] = char_options
        if char_options:
            self.cb_character.current(0)
        else:
            self.cb_character.set("")
    
    def reset_editor(self):
        self.characters.clear()
        self.dialogues.clear()
        self.current_label.set("start")
        self.lb_characters.delete(0, tk.END)
        self.lb_contents.delete(0, tk.END)
        self.entry_var_name.delete(0, tk.END)
        self.entry_display_name.delete(0, tk.END)
        self.txt_character_dialog.delete("1.0", tk.END)
        self.txt_narration.delete("1.0", tk.END)
        self.update_character_combobox()
    
    def load_temp_data(self, temp_data):
        self.reset_editor()
        
        self.characters = temp_data["characters"]
        for char in self.characters:
            display_text = f"{char['var_name']} - {char['display_name']}"
            self.lb_characters.insert(tk.END, display_text)
        
        self.current_label.set(temp_data["current_label"])
        
        self.dialogues = temp_data["dialogues"]
        for content_type, char_var, content in self.dialogues:
            if content_type == "character":
                char_display = char_var
                for char in self.characters:
                    if char["var_name"] == char_var:
                        char_display = char["display_name"]
                        break
                display_text = f"[角色] {char_display}: {content}"
            else:
                display_text = f"[旁白] {content}"
            self.lb_contents.insert(tk.END, display_text)
        
        self.update_character_combobox()
    
    def add_character(self):
        var_name = self.entry_var_name.get().strip()
        display_name = self.entry_display_name.get().strip()
        
        if not var_name:
            messagebox.showwarning("警告", "角色变量名不能为空！")
            return
        if not VAR_NAME_PATTERN.match(var_name):
            messagebox.showwarning("警告", "变量名仅允许字母、数字、下划线，且不能以数字开头，禁止中文！")
            return
        for char in self.characters:
            if char["var_name"] == var_name:
                messagebox.showinfo("提示", f"变量名「{var_name}」已存在！")
                return
        
        if not display_name:
            display_name = var_name
        
        self.characters.append({
            "var_name": var_name,
            "display_name": display_name
        })
        display_text = f"{var_name} - {display_name}"
        self.lb_characters.insert(tk.END, display_text)
        
        self.entry_var_name.delete(0, tk.END)
        self.entry_display_name.delete(0, tk.END)
        
        self.update_character_combobox()
        messagebox.showinfo("成功", f"角色「{var_name} - {display_name}」添加完成！")
    
    def delete_character(self):
        selected_index = self.lb_characters.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请先选中要删除的角色！")
            return
        
        selected_index = selected_index[0]
        char_info = self.characters[selected_index]
        if messagebox.askyesno("确认", f"是否删除角色「{char_info['var_name']} - {char_info['display_name']}」？"):
            del self.characters[selected_index]
            self.lb_characters.delete(selected_index)
            self.update_character_combobox()
            messagebox.showinfo("成功", f"角色已删除！")
    
    def import_from_config(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("角色配置文件", "*.json"), ("所有文件", "*.*")],
            title="打开角色配置文件"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            if "characters" not in config_data:
                messagebox.showerror("错误", "配置文件格式错误，缺少角色数据！")
                return
            
            config_chars = config_data["characters"]
            if not config_chars:
                messagebox.showwarning("警告", "配置文件中无角色数据！")
                return
            
            self.characters.clear()
            self.lb_characters.delete(0, tk.END)
            
            for char in config_chars:
                self.characters.append(char)
                display_text = f"{char['var_name']} - {char['display_name']}"
                self.lb_characters.insert(tk.END, display_text)
            
            self.update_character_combobox()
            messagebox.showinfo("成功", f"已从配置文件导入{len(config_chars)}个角色！")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "配置文件损坏，无法解析！")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
    
    def add_character_dialogue(self):
        selected_char_text = self.cb_character.get()
        dialog_content = self.txt_character_dialog.get("1.0", tk.END).strip()
        
        if not selected_char_text:
            messagebox.showwarning("警告", "请先选择一个角色！")
            return
        if not dialog_content:
            messagebox.showwarning("警告", "角色对话内容不能为空！")
            return
        
        char_var = selected_char_text.split(" - ")[0]
        char_display = selected_char_text.split(" - ")[1] if len(selected_char_text.split(" - "))>1 else char_var
        
        self.dialogues.append(("character", char_var, dialog_content))
        display_text = f"[角色] {char_display}: {dialog_content}"
        self.lb_contents.insert(tk.END, display_text)
        self.txt_character_dialog.delete("1.0", tk.END)
    
    def add_narration(self):
        narration_content = self.txt_narration.get("1.0", tk.END).strip()
        
        if not narration_content:
            messagebox.showwarning("警告", "旁白内容不能为空！")
            return
        
        self.dialogues.append(("narration", "", narration_content))
        display_text = f"[旁白] {narration_content}"
        self.lb_contents.insert(tk.END, display_text)
        self.txt_narration.delete("1.0", tk.END)
    
    def on_drag_start(self, event):
        self.drag_index = self.lb_contents.nearest(event.y)
        if self.drag_index >= 0:
            self.drag_item = self.lb_contents.get(self.drag_index)
            self.lb_contents.selection_clear(0, tk.END)
            self.lb_contents.selection_set(self.drag_index)
    
    def on_drag_motion(self, event):
        if self.drag_item is None:
            return
        current_index = self.lb_contents.nearest(event.y)
        if current_index != self.drag_index and current_index >= 0:
            self.lb_contents.selection_clear(0, tk.END)
            self.lb_contents.selection_set(current_index)
    
    def on_drag_end(self, event):
        if self.drag_item is None or self.drag_index < 0:
            self.drag_item = None
            self.drag_index = -1
            return
        
        drop_index = self.lb_contents.nearest(event.y)
        if drop_index < 0 or drop_index == self.drag_index:
            self.drag_item = None
            self.drag_index = -1
            return
        
        item_data = self.dialogues.pop(self.drag_index)
        self.dialogues.insert(drop_index, item_data)
        
        self.lb_contents.delete(0, tk.END)
        for content_type, char_var, content in self.dialogues:
            if content_type == "character":
                char_display = char_var
                for char in self.characters:
                    if char["var_name"] == char_var:
                        char_display = char["display_name"]
                        break
                display_text = f"[角色] {char_display}: {content}"
            else:
                display_text = f"[旁白] {content}"
            self.lb_contents.insert(tk.END, display_text)
        
        self.lb_contents.selection_clear(0, tk.END)
        self.lb_contents.selection_set(drop_index)
        self.drag_item = None
        self.drag_index = -1
    
    def move_item_up(self):
        selected_index = self.lb_contents.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请先选中要上移的内容！")
            return
        
        selected_index = selected_index[0]
        if selected_index == 0:
            messagebox.showinfo("提示", "已到最顶部，无法上移！")
            return
        
        self.dialogues[selected_index], self.dialogues[selected_index-1] = \
            self.dialogues[selected_index-1], self.dialogues[selected_index]
        
        self.lb_contents.delete(0, tk.END)
        for content_type, char_var, content in self.dialogues:
            if content_type == "character":
                char_display = char_var
                for char in self.characters:
                    if char["var_name"] == char_var:
                        char_display = char["display_name"]
                        break
                display_text = f"[角色] {char_display}: {content}"
            else:
                display_text = f"[旁白] {content}"
            self.lb_contents.insert(tk.END, display_text)
        
        self.lb_contents.selection_clear(0, tk.END)
        self.lb_contents.selection_set(selected_index-1)
    
    def move_item_down(self):
        selected_index = self.lb_contents.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请先选中要下移的内容！")
            return
        
        selected_index = selected_index[0]
        if selected_index == len(self.dialogues)-1:
            messagebox.showinfo("提示", "已到最底部，无法下移！")
            return
        
        self.dialogues[selected_index], self.dialogues[selected_index+1] = \
            self.dialogues[selected_index+1], self.dialogues[selected_index]
        
        self.lb_contents.delete(0, tk.END)
        for content_type, char_var, content in self.dialogues:
            if content_type == "character":
                char_display = char_var
                for char in self.characters:
                    if char["var_name"] == char_var:
                        char_display = char["display_name"]
                        break
                display_text = f"[角色] {char_display}: {content}"
            else:
                display_text = f"[旁白] {content}"
            self.lb_contents.insert(tk.END, display_text)
        
        self.lb_contents.selection_clear(0, tk.END)
        self.lb_contents.selection_set(selected_index+1)
    
    def delete_content(self):
        selected_index = self.lb_contents.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "请先选中要删除的内容！")
            return
        
        if messagebox.askyesno("确认", "是否删除选中的内容？"):
            del self.dialogues[selected_index[0]]
            self.lb_contents.delete(selected_index)
            messagebox.showinfo("成功", "选中的内容已删除！")
    
    def new_script(self):
        if messagebox.askyesno("确认", "是否新建脚本？当前未保存的内容将丢失！"):
            self.reset_editor()
            messagebox.showinfo("提示", "已新建空白脚本！")
    
    def generate_script(self):
        if not self.dialogues:
            messagebox.showwarning("警告", "请先添加至少一条角色对话或旁白！")
            return
        
        label_name = self.current_label.get().strip().replace(" ", "_")
        if not label_name:
            label_name = "start"
        
        script_lines = []
        has_character_dialog = any([d[0] == "character" for d in self.dialogues])
        
        if has_character_dialog and self.characters:
            script_lines.append("# 角色定义（变量名=预定义值，禁止中文）")
            for char in self.characters:
                script_lines.append(f'define {char["var_name"]} = Character("{char["display_name"]}")')
            script_lines.append("")
        
        script_lines.append(f"label {label_name}:")
        for content_type, char_var, content in self.dialogues:
            escaped_content = content.replace('"', '\\"')
            if content_type == "character":
                script_lines.append(f"    {char_var} \"{escaped_content}\"")
            elif content_type == "narration":
                script_lines.append(f"    \"{escaped_content}\"")
        
        self.generated_script = "\n".join(script_lines)
        
        script_window = tk.Toplevel(self)
        script_window.title("生成的Ren'Py脚本")
        script_window.geometry("750x550")
        script_window.minsize(700, 500)
        script_window.configure(bg="#f0f0f0")
        
        txt_script = tk.Text(script_window, font=self.base_font, bd=1, relief="solid")
        txt_script.pack(fill="both", padx=15, pady=15, expand=True)
        txt_script.insert("1.0", self.generated_script)
        txt_script.config(state="readonly")
        
        ttk.Button(
            script_window, 
            text="关闭", 
            command=script_window.destroy,
            style="Custom.TButton"
        ).pack(pady=10)
    
    def save_script(self):
        if not hasattr(self, 'generated_script') or not self.generated_script:
            messagebox.showwarning("警告", "请先点击「生成Ren'Py脚本」按钮！")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".rpy",
            filetypes=[("Ren'Py脚本文件", "*.rpy"), ("所有文件", "*.*")],
            title="保存Ren'Py脚本"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.generated_script)
            messagebox.showinfo("成功", f"脚本已保存到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
    
    def save_temp_file(self):
        temp_data = {
            "characters": self.characters,
            "current_label": self.current_label.get(),
            "dialogues": self.dialogues
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("临时配置文件", "*.json"), ("所有文件", "*.*")],
            title="保存临时文件"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", f"临时文件已保存到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"临时文件保存失败：{str(e)}")
    
    def open_temp_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("临时配置文件", "*.json"), ("所有文件", "*.*")],
            title="打开临时文件"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                temp_data = json.load(f)
            
            required_keys = ["characters", "current_label", "dialogues"]
            if not all(key in temp_data for key in required_keys):
                messagebox.showerror("错误", "临时文件格式错误，缺少必要数据！")
                return
            
            self.load_temp_data(temp_data)
            messagebox.showinfo("成功", f"已从临时文件恢复数据：\n{file_path}")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "临时文件损坏，无法解析！")
        except Exception as e:
            messagebox.showerror("错误", f"打开临时文件失败：{str(e)}")
    
    def on_window_close(self):
        close_confirm = messagebox.askyesno("确认关闭", "是否确定关闭Ren'Py脚本生成工具？")
        if not close_confirm:
            return
        
        backup_confirm = messagebox.askyesno("备份文档", "是否需要备份当前编辑的内容为临时脚本文件？")
        if backup_confirm:
            self.save_temp_file_on_close()
        
        self.destroy()
    
    def save_temp_file_on_close(self):
        temp_data = {
            "characters": self.characters,
            "current_label": self.current_label.get(),
            "dialogues": self.dialogues
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("临时配置文件", "*.json"), ("所有文件", "*.*")],
            title="备份临时脚本文件"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(temp_data, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("备份成功", f"当前内容已备份到：\n{file_path}")
        except Exception as e:
            messagebox.showerror("备份失败", f"临时文件备份失败：{str(e)}")

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = RenPyScriptGenerator()
    app.mainloop()