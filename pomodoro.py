import time
import json
from datetime import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import font_manager
from collections import defaultdict

# 配置中文字体
# 如果是 Windows 系统，通常使用 SimHei 或 Microsoft YaHei
# 如果是 Mac，可以使用 STHeiti 或 PingFang
font_path = "/System/Library/Fonts/STHeiti Light.ttc"  # macOS 示例
# font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Ubuntu 示例
# font_path = "C:/Windows/Fonts/simhei.ttf"  # Windows 示例
prop = font_manager.FontProperties(fname=font_path)

# 定义 JSON 文件名
DATA_FILE = "pomodoro_data_with_tags.json"
BACKUP_FILE = "pomodoro_data_backup.json"

# 定义多语言支持
LANGUAGES = {
    "zh": {
        "menu": ["开始一个番茄时钟", "查看统计数据", "查看统计图表", "退出", "切换语言"],
        "tags": ["英文", "书籍", "Python", "Web", "冥想", "其他"],
        "prompt": "请选择: ",
        "task_prompt": "请选择任务标签：",
        "enter_tag": "请输入新标签: ",
        "duration_prompt": "请输入番茄时钟的时长（分钟，默认为25）: ",
        "timer_start": "开始一个 {minutes} 分钟的番茄时钟（标签：{tag}）...",
        "time_remaining": "剩余时间: {minutes:02}:{seconds:02}",
        "timer_complete": "\n番茄时钟完成！",
        "interrupt": "\n计时被中断。",
        "completed_msg": "Pomodoro session complete!",
        "invalid_choice": "无效的选项，请重新选择。",
        "statistics_title": "每日完成的番茄时钟个数（按标签分类）：",
        "chart_title": "番茄时钟每日统计（按标签）",
        "x_label": "日期",
        "y_label": "计数",
        "tags_title": "标签",
        "goodbye": "再见！",
        "no_data": "暂无统计数据。",
    },
    "en": {
        "menu": ["Start a Pomodoro Timer", "View Statistics", "View Statistics Chart", "Exit", "Switch language"],
        "tags": ["English", "Books", "Python", "Web", "Meditation", "Others"],
        "prompt": "Choose: ",
        "task_prompt": "Select a task tag:",
        "enter_tag": "Enter new tag: ",
        "duration_prompt": "Enter timer duration (minutes, default 25): ",
        "timer_start": "Starting a {minutes}-minute Pomodoro Timer (Tag: {tag})...",
        "time_remaining": "Time remaining: {minutes:02}:{seconds:02}",
        "timer_complete": "\nPomodoro Timer complete!",
        "interrupt": "\nTimer was interrupted.",
        "completed_msg": "Pomodoro session complete!",
        "invalid_choice": "Invalid choice, please try again.",
        "statistics_title": "Daily Pomodoro Timer Counts (by Tag):",
        "chart_title": "Pomodoro Timer Daily Statistics (by Tag)",
        "x_label": "Date",
        "y_label": "Count",
        "tags_title": "Tags",
        "goodbye": "Goodbye!",
        "no_data": "No data available.",
    }
}

# 设置默认语言
current_language = "en"

# 加载或初始化数据
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 保存数据到 JSON 文件
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 备份数据
def backup_data(data):
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 增加当天的番茄时钟计数
def add_pomodoro(tag):
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()
    if today not in data:
        data[today] = {}
    if tag in data[today]:
        data[today][tag] += 1
    else:
        data[today][tag] = 1
    save_data(data)
    backup_data(data)

# 显示统计数据
def show_statistics():
    data = load_data()
    if not data:
        print(LANGUAGES[current_language]["no_data"])
        return
    print(LANGUAGES[current_language]["statistics_title"])
    for date, tags in sorted(data.items()):
        print(f"\n{date}:")
        for tag, count in tags.items():
            print(f"  {tag}: {count} 个" if current_language == "zh" else f"  {tag}: {count}")

# 显示统计图表
def show_statistics_line_chart():
    data = load_data()
    if not data:
        print(LANGUAGES[current_language]["no_data"])
        return

    # 准备统计数据
    dates = list(data.keys())
    tags = set()  # 所有标签
    for date in dates:
        tags.update(data[date].keys())
    tags = sorted(tags)  # 按字母排序标签

    # 统计每个标签每天的计数
    tag_daily_counts = defaultdict(list)
    for date in dates:
        for tag in tags:
            count = data[date].get(tag, 0)  # 如果当天没有该标签，则为 0
            tag_daily_counts[tag].append(count)

    # 绘制折线图
    plt.figure(figsize=(10, 6))
    cmap = cm.get_cmap("tab10", len(tags))  # 不同颜色
    for i, tag in enumerate(tags):
        plt.plot(dates, tag_daily_counts[tag], marker='o', label=tag, color=cmap(i))

    # 设置图表标题和标签
    plt.title(LANGUAGES[current_language]["chart_title"], fontsize=16, fontproperties=prop)
    plt.xlabel(LANGUAGES[current_language]["x_label"], fontsize=12, fontproperties=prop)
    plt.ylabel(LANGUAGES[current_language]["y_label"], fontsize=12, fontproperties=prop)
    plt.xticks(rotation=45)
    plt.legend(title=LANGUAGES[current_language]["tags_title"], fontsize=10, title_fontsize=12, prop=prop)
    plt.grid(True, linestyle='--', alpha=0.7)

    # 调整布局并显示
    plt.tight_layout()
    plt.show()

# 切换语言
def switch_language():
    global current_language
    new_language = input("Enter language (en/zh): ").strip().lower()
    if new_language in LANGUAGES:
        current_language = new_language
        print(LANGUAGES[current_language]["goodbye"])
    else:
        print("Invalid language!")

# 番茄时钟计时器
def pomodoro_timer(minutes=25, tag="默认", language="zh"):
    # 获取当前语言的字符串模板
    lang = LANGUAGES[language]

    print(lang["timer_start"].format(minutes=minutes, tag=tag))

    try:
        for remaining in range(minutes * 60, 0, -1):
            minutes_left = remaining // 60
            seconds_left = remaining % 60
            print(lang["time_remaining"].format(minutes=minutes_left, seconds=seconds_left), end="\r")
            time.sleep(1)

        print(lang["timer_complete"])
        add_pomodoro(tag)
        os.system(f'say "{lang["completed_msg"]}"')  # macOS 系统语音
        # import winsound
        # winsound.Beep(440, 1000)  # 播放 440Hz 的提示音，持续 1 秒
    except KeyboardInterrupt:
        print(lang["interrupt"])


# 主程序
def main():
    global current_language
    tags = LANGUAGES[current_language]["tags"]

    while True:
        menu = LANGUAGES[current_language]["menu"]
        print("\n" + "\n".join([f"{i+1}. {option}" for i, option in enumerate(menu)]))
        choice = input(LANGUAGES[current_language]["prompt"])
        if choice == "1":
            try:
                print(LANGUAGES[current_language]["task_prompt"])
                for i, tag in enumerate(tags, start=1):
                    print(f"{i}. {tag}")
                tag_choice = int(input(">>> "))
                if 1 <= tag_choice <= len(tags):
                    tag = tags[tag_choice - 1]
                else:
                    tag = "Default" if current_language == "en" else "默认"
                duration = int(input(LANGUAGES[current_language]["duration_prompt"]) or 25)
                pomodoro_timer(duration, tag, current_language)
            except ValueError:
                print(LANGUAGES[current_language]["invalid_choice"])
        elif choice == "2":
            show_statistics()
        elif choice == "3":
            show_statistics_line_chart()
        elif choice == "4":
            print(LANGUAGES[current_language]["goodbye"])
            break
        elif choice == "5":
            switch_language()

if __name__ == "__main__":
    main()
