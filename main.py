import json
import requests
import tkinter as tk
from tkinter import messagebox
import os

mod_list_url = "https://raw.gitmirror.com/LibraHp/ModManager/refs/heads/master/mod_info.json"
try:
    mod_info_json = requests.get(mod_list_url)
    mod_info_data = json.loads(mod_info_json.text)
except Exception as e:
    with open('mod_info.json', 'r', encoding='utf-8') as json_file:
        mod_info_data = json.load(json_file)

# 根据mod_info.json生成mod_status.json
mod_status_data = {}
for mod in mod_info_data["mods"]:
    mod_name = mod["mod_name"]
    mod_status_data[mod_name] = {"installed": False, "version": "1.0.0"}

# 如果mod_status.json不存在,创建一个新的文件
if not os.path.exists('mod_status.json'):
    with open('mod_status.json', 'w', encoding='utf-8') as json_file:
        json.dump(mod_status_data, json_file, ensure_ascii=False, indent=4)

with open('mod_status.json', 'r', encoding='utf-8') as json_file:
    mod_status_data = json.load(json_file)

root = tk.Tk()
root.title("融合版mod管理器")
root.geometry("600x400")

left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

listbox1 = tk.Listbox(left_frame, width=30)
listbox1.pack(fill=tk.BOTH, expand=True)

info_frame = tk.Frame(right_frame)
info_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(info_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_info = tk.Text(info_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
text_info.pack(fill=tk.BOTH, expand=True)

scrollbar.config(command=text_info.yview)

button_frame = tk.Frame(right_frame)
button_frame.pack(side=tk.BOTTOM, fill=tk.X)
def download_file(url, save_path):
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")
    with open(save_path, 'wb') as f:
        f.write(response.content)

def handleClick(event):
    index = listbox1.curselection()[0]
    mod_info = mod_info_data["mods"][index]
    info_msg = f"名称：{mod_info['mod_name']}\n版本：{mod_info['mod_version']}\n作者：{mod_info['mod_author']}\n食用教程：{mod_info['mod_description']}\n下载链接：{mod_info['mod_download_url']}"
    text_info.delete(1.0, tk.END)
    text_info.insert(tk.END, info_msg)

def downloadMod():
    index = listbox1.curselection()[0]
    mod_name = mod_info_data["mods"][index]['mod_name']
    if mod_status_data[mod_name]["installed"]:
        messagebox.showinfo("下载 Mod", f"{mod_name} 已经安装。")
        return

    mod_download_url = mod_info_data["mods"][index]['mod_download_url']
    mod_path = mod_info_data["mods"][index]['mod_install_location']
    try:
        download_file(mod_download_url, mod_path + "/" + mod_name + ".dll")
        messagebox.showinfo(f"{mod_name}.","安装成功！")
        mod_status_data[mod_name]["installed"] = True
        saveModStatus()
    except Exception as e:
        print(e)
        messagebox.showinfo(f"{mod_name}.","下载失败！")
    

def uninstallMod():
    index = listbox1.curselection()[0]
    mod_name = mod_info_data["mods"][index]['mod_name']
    if not mod_status_data[mod_name]["installed"]:
        messagebox.showinfo("卸载 Mod", f"{mod_name} 未安装。")
        return
    mod_status_data[mod_name]["installed"] = False
    saveModStatus()
    messagebox.showinfo("卸载 Mod", f"开始卸载 {mod_name}.")


def saveModStatus():
    with open('mod_status.json', 'w', encoding='utf-8') as json_file:
        json.dump(mod_status_data, json_file, ensure_ascii=False, indent=4)
    for i, mod in enumerate(mod_info_data["mods"]):
        mod_name = mod["mod_name"]
        is_installed = mod_status_data[mod_name]["installed"] if mod_name in mod_status_data else False
        color = "green" if is_installed else "red"
        listbox1.itemconfig(i, {'fg': color})


listbox1.bind('<<ListboxSelect>>', handleClick)

download_button = tk.Button(button_frame, text="下载 Mod", command=downloadMod)
download_button.pack(side=tk.LEFT, padx=5, pady=5)

uninstall_button = tk.Button(button_frame, text="卸载 Mod", command=uninstallMod)
uninstall_button.pack(side=tk.RIGHT, padx=5, pady=5)

for i, mod in enumerate(mod_info_data["mods"]):
    mod_name = mod["mod_name"]
    mod_version = mod["mod_version"]
    mod_author = mod["mod_author"]
    is_installed = mod_status_data[mod_name]["installed"] if mod_name in mod_status_data else False

    color = "green" if is_installed else "red"

    listbox1.insert(tk.END, f"{mod_name}-{mod_author}-V {mod_version}")
    listbox1.itemconfig(i, {'fg': color})

root.mainloop()
