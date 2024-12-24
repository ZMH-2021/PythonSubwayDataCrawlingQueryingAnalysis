import sqlite3
import tkinter as tk
from tkinter import scrolledtext
import tkinter.messagebox as messagebox

# 存储查询到的结果
information = []

def create_gui():
    root = tk.Tk()
    root.title("地铁信息查询系统")
    root.geometry("800x600")

    # 整体布局框架
    main_frame = tk.Frame(root, bg="#F0F0F0")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 线路查询部分
    line_frame = tk.Frame(main_frame, bg="#E0E0E0")
    line_frame.pack(pady=20)
    line_label = tk.Label(line_frame, text="查询线路（格式：城市,线路）", font=("Arial", 14))
    line_label.pack(side=tk.LEFT)
    line_search_text = tk.StringVar()
    line_entry = tk.Entry(line_frame, font=("Arial", 14), textvariable=line_search_text)
    line_entry.pack(side=tk.LEFT, padx=10)
    line_button = tk.Button(line_frame, text="查询", font=("Arial", 14), command=lambda: search_line(line_search_text.get()))
    line_button.pack(side=tk.LEFT)

    # 站点查询部分
    station_frame = tk.Frame(main_frame, bg="#E0E0E0")
    station_frame.pack(pady=20)
    station_label = tk.Label(station_frame, text="查询站点", font=("Arial", 14))
    station_label.pack(side=tk.LEFT)
    station_search_text = tk.StringVar()
    station_entry = tk.Entry(station_frame, font=("Arial", 14), textvariable=station_search_text)
    station_entry.pack(side=tk.LEFT, padx=10)
    station_button = tk.Button(station_frame, text="查询", font=("Arial", 14), command=lambda: search_station(station_search_text.get()))
    station_button.pack(side=tk.LEFT)

    # 结果展示区域
    result_frame = tk.Frame(main_frame, bg="#E0E0E0")
    result_frame.pack(pady=20, fill=tk.BOTH, expand=True)
    result_text = scrolledtext.ScrolledText(result_frame, width=62, height=20, font=("Arial", 12))
    result_text.pack(fill=tk.BOTH, expand=True)

    return root, result_text


def search_line(sstr):
    global information
    result = sstr.split(",")
    result = [r.strip() for r in result]
    if len(result)!= 2:
        messagebox.showwarning("输入错误", "请按照 '城市,线路' 的格式输入")
        return
    try:
        sql = "select city,line,name from info where city=? and line=?"
        conn = sqlite3.connect('../data/city_lines.db', check_same_thread=False)
        cur = conn.cursor()
        s = cur.execute(sql, (result[0], result[1]))
        information = [f"{i[0]}  {i[1]}  {i[2]}" for i in s]
        display_result(result_text, information)
        information = []
    except sqlite3.Error as e:
        messagebox.showerror("查询错误", f"数据库查询线路时出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def search_station(sstr):
    global information
    sstr = sstr.strip()
    if not sstr:
        messagebox.showwarning("输入错误", "请输入要查询的站点名称")
        return
    try:
        sql = "select city,line,name from info where name=?"
        conn = sqlite3.connect('../data/city_lines.db', check_same_thread=False)
        cur = conn.cursor()
        s = cur.execute(sql, (sstr,))
        information = [f"{i[0]}  {i[1]}  {i[2]}" for i in s]
        display_result(result_text, information)
        information = []
    except sqlite3.Error as e:
        messagebox.showerror("查询错误", f"数据库查询站点时出错: {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def display_result(result_text, data):
    result_text.delete('1.0', tk.END)
    if len(data) == 0:
        result_text.insert(tk.END, "未找到相关信息")
    else:
        for item in data:
            result_text.insert(tk.END, item + "\n")


if __name__ == '__main__':
    root, result_text = create_gui()
    root.mainloop()