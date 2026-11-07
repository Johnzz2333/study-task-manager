import json
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


TASKS_FILE = Path(__file__).resolve().with_name("tasks.json")


def save_tasks(tasks):
    """将任务保存为 UTF-8 编码的 JSON 文件。"""
    # 先写入同一磁盘上的临时文件，写完再替换，避免写到一半破坏原文件。
    file = NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=TASKS_FILE.parent, delete=False
    )
    temporary_file = Path(file.name)
    try:
        with file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_file.replace(TASKS_FILE)
    finally:
        temporary_file.unlink(missing_ok=True)


def load_tasks():
    """读取并检查已保存的任务，首次运行时初始化空列表。"""
    try:
        with TASKS_FILE.open(encoding="utf-8") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
        save_tasks(tasks)

    # JSON 能解析也可能结构不对，进入菜单前逐项检查。
    if not isinstance(tasks, list):
        raise ValueError("任务文件应包含一个列表。")
    for task in tasks:
        if (
            not isinstance(task, dict)
            or not isinstance(task.get("title"), str)
            or not task["title"].strip()
            or not isinstance(task.get("done"), bool)
        ):
            raise ValueError("每条任务都应包含非空标题和布尔类型的完成状态。")
    return tasks


def show_tasks(tasks):
    if not tasks:
        print("暂无学习任务。")
        return

    for number, task in enumerate(tasks, start=1):
        status = "已完成" if task["done"] else "未完成"
        print(f"{number}. [{status}] {task['title']}")


def choose_task(tasks, action):
    """显示任务并读取编号，输入无效时返回 None。"""
    show_tasks(tasks)
    if not tasks:
        return None

    try:
        number = int(input(f"请输入要{action}的任务编号："))
    except ValueError:
        print("任务编号必须是整数。")
        return None

    if not 1 <= number <= len(tasks):
        print(f"任务编号必须在 1 到 {len(tasks)} 之间。")
        return None

    # 显示编号从 1 开始，Python 列表索引从 0 开始。
    return number - 1


def add_task(tasks):
    title = input("请输入任务标题：").strip()
    if not title:
        print("任务标题不能为空。")
        return

    tasks.append({"title": title, "done": False})
    save_tasks(tasks)
    print("已添加任务。")


def complete_task(tasks):
    index = choose_task(tasks, "标记完成")
    if index is None:
        return
    if tasks[index]["done"]:
        print("这条任务已经完成。")
        return

    tasks[index]["done"] = True
    save_tasks(tasks)
    print("已标记完成。")


def delete_task(tasks):
    index = choose_task(tasks, "删除")
    if index is None:
        return

    del tasks[index]
    save_tasks(tasks)
    print("已删除任务。")


def run_menu(tasks):
    """反复显示菜单，直到用户选择退出。"""
    while True:
        print("\n学习任务管理器")
        print("1. 添加任务\n2. 查看所有任务\n3. 标记任务完成\n4. 删除任务\n0. 退出")
        choice = input("请选择操作：").strip()

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            show_tasks(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "0":
            return
        else:
            print("请选择菜单中显示的数字。")


def main():
    try:
        run_menu(load_tasks())
    except ValueError as error:
        print(f"任务文件内容无效，已保留原文件。{error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"无法读取或保存任务文件。{error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\n已退出。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
