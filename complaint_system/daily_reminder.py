#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日客诉提醒脚本 - 由定时任务调用"""
import json, os, sys
from datetime import date, datetime, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_FILE = os.path.join(os.path.dirname(__file__), "complaints.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"complaints": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def daily_reminder():
    data = load_data()
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    tomorrow_str = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    active = [c for c in data["complaints"] if c["status"] not in ("已解决", "已关闭")]
    overdue = [c for c in active if c["deadline"] < today_str]
    due_today = [c for c in active if c["deadline"] == today_str]
    due_tomorrow = [c for c in active if c["deadline"] == tomorrow_str]

    print(f"\n{'='*50}")
    print(f"  客诉每日提醒 - {today_str}")
    print(f"{'='*50}")
    print(f"  活跃客诉总数: {len(active)}")
    print(f"  [!] 已逾期:   {len(overdue)} 条")
    print(f"  [今] 今日到期: {len(due_today)} 条")
    print(f"  [明] 明日到期: {len(due_tomorrow)} 条")
    print()

    if overdue:
        print("【逾期未解决】")
        for c in overdue:
            days = (today - date.fromisoformat(c["deadline"])).days
            print(f"  #{c['id']} {c['customer']} | {c['problem_type']} | {c['severity']} | 跟进:{c['follower']} | 逾期{days}天")
        print()

    if due_today:
        print("【今日到期】")
        for c in due_today:
            print(f"  #{c['id']} {c['customer']} | {c['problem_type']} | {c['severity']} | 跟进:{c['follower']}")
        print()

    if due_tomorrow:
        print("【明日到期】")
        for c in due_tomorrow:
            print(f"  #{c['id']} {c['customer']} | {c['problem_type']} | {c['severity']} | 跟进:{c['follower']}")
        print()

    if not overdue and not due_today and not due_tomorrow:
        print("  今日无紧急客诉需要跟进，继续保持！")

    # 按跟进人分组汇总
    follower_map = {}
    for c in active:
        follower_map.setdefault(c["follower"], []).append(c)
    if follower_map:
        print("【各跟进人待处理数量】")
        for person, items in sorted(follower_map.items()):
            urgent = sum(1 for i in items if i["deadline"] <= tomorrow_str)
            print(f"  {person}: 共{len(items)}条 (近期紧急:{urgent}条)")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    daily_reminder()
