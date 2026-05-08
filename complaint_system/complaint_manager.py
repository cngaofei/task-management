#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""客诉管理系统 - 主管理脚本"""
import json, sys, os
from datetime import datetime, date

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_FILE = os.path.join(os.path.dirname(__file__), "complaints.json")

SEVERITY_LEVELS = {"1": "低", "2": "中", "3": "高", "4": "紧急"}
PROBLEM_TYPES = {
    "1": "产品质量", "2": "服务态度", "3": "交付延迟",
    "4": "账单问题", "5": "技术故障", "6": "其他"
}
STATUS_OPTIONS = {"1": "待处理", "2": "处理中", "3": "已解决", "4": "已关闭"}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"complaints": [], "next_id": 1}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_complaint():
    data = load_data()
    print("\n=== 新增客诉 ===")
    name = input("客户名称: ").strip()
    if not name:
        print("客户名称不能为空"); return

    print("问题类型: " + " | ".join(f"{k}.{v}" for k, v in PROBLEM_TYPES.items()))
    ptype_key = input("选择(1-6): ").strip()
    ptype = PROBLEM_TYPES.get(ptype_key, "其他")

    print("严重程度: " + " | ".join(f"{k}.{v}" for k, v in SEVERITY_LEVELS.items()))
    sev_key = input("选择(1-4): ").strip()
    severity = SEVERITY_LEVELS.get(sev_key, "中")

    follower = input("跟进人: ").strip()
    deadline = input("解决期限(YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        print("日期格式错误，使用今天+7天")
        from datetime import timedelta
        deadline = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    description = input("问题描述(可选): ").strip()

    complaint = {
        "id": data["next_id"],
        "customer": name,
        "problem_type": ptype,
        "severity": severity,
        "follower": follower,
        "deadline": deadline,
        "description": description,
        "status": "待处理",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "notes": []
    }
    data["complaints"].append(complaint)
    data["next_id"] += 1
    save_data(data)
    print(f"\n✓ 客诉 #{complaint['id']} 已创建")

def list_complaints(filter_status=None, filter_follower=None):
    data = load_data()
    items = data["complaints"]
    if filter_status:
        items = [c for c in items if c["status"] == filter_status]
    if filter_follower:
        items = [c for c in items if c["follower"] == filter_follower]
    if not items:
        print("暂无客诉记录"); return
    print(f"\n{'ID':<4} {'客户':<10} {'类型':<8} {'严重':<4} {'跟进人':<8} {'期限':<12} {'状态':<6} {'描述'}")
    print("-" * 80)
    today = date.today().strftime("%Y-%m-%d")
    for c in items:
        flag = "⚠" if c["deadline"] < today and c["status"] not in ("已解决","已关闭") else " "
        print(f"{flag}{c['id']:<4} {c['customer']:<10} {c['problem_type']:<8} {c['severity']:<4} {c['follower']:<8} {c['deadline']:<12} {c['status']:<6} {c['description'][:20]}")

def update_status():
    data = load_data()
    cid = input("输入客诉ID: ").strip()
    complaint = next((c for c in data["complaints"] if str(c["id"]) == cid), None)
    if not complaint:
        print("未找到该客诉"); return
    print(f"当前状态: {complaint['status']}")
    print("新状态: " + " | ".join(f"{k}.{v}" for k, v in STATUS_OPTIONS.items()))
    key = input("选择: ").strip()
    if key in STATUS_OPTIONS:
        complaint["status"] = STATUS_OPTIONS[key]
        note = input("备注(可选): ").strip()
        if note:
            complaint["notes"].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note})
        complaint["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_data(data)
        print(f"✓ 状态已更新为: {complaint['status']}")

def main():
    cmds = {"1": "新增客诉", "2": "查看所有", "3": "查看待处理", "4": "更新状态", "5": "退出"}
    while True:
        print("\n=== 客诉管理系统 ===")
        for k, v in cmds.items():
            print(f"  {k}. {v}")
        choice = input("选择操作: ").strip()
        if choice == "1": add_complaint()
        elif choice == "2": list_complaints()
        elif choice == "3": list_complaints(filter_status="待处理")
        elif choice == "4": update_status()
        elif choice == "5": break
        else: print("无效选项")

if __name__ == "__main__":
    main()
