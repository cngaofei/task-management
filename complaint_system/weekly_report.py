#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""周报生成脚本 - 每周五自动运行"""
import json, os, sys
from datetime import date, datetime, timedelta

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATA_FILE = os.path.join(os.path.dirname(__file__), "complaints.json")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"complaints": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_week_range():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday

def generate_weekly_report():
    data = load_data()
    monday, sunday = get_week_range()
    mon_str = monday.strftime("%Y-%m-%d")
    sun_str = sunday.strftime("%Y-%m-%d")
    today_str = date.today().strftime("%Y-%m-%d")

    # 本周新增
    new_this_week = [c for c in data["complaints"]
                     if mon_str <= c["created_at"][:10] <= sun_str]
    # 本周解决
    resolved_this_week = [c for c in data["complaints"]
                          if c["status"] in ("已解决","已关闭")
                          and mon_str <= c["updated_at"][:10] <= sun_str]
    # 当前活跃
    active = [c for c in data["complaints"] if c["status"] not in ("已解决","已关闭")]
    overdue = [c for c in active if c["deadline"] < today_str]

    lines = []
    lines.append(f"客诉周报 {mon_str} ~ {sun_str}")
    lines.append("=" * 50)
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("【本周概况】")
    lines.append(f"  本周新增客诉: {len(new_this_week)} 条")
    lines.append(f"  本周解决客诉: {len(resolved_this_week)} 条")
    lines.append(f"  当前待处理:   {len(active)} 条")
    lines.append(f"  当前逾期未解: {len(overdue)} 条")
    lines.append("")

    if new_this_week:
        lines.append("【本周新增客诉】")
        for c in new_this_week:
            lines.append(f"  #{c['id']} [{c['severity']}] {c['customer']} - {c['problem_type']} (跟进:{c['follower']}, 期限:{c['deadline']})")
        lines.append("")

    if resolved_this_week:
        lines.append("【本周已解决】")
        for c in resolved_this_week:
            lines.append(f"  #{c['id']} {c['customer']} - {c['problem_type']} ({c['status']})")
        lines.append("")

    if overdue:
        lines.append("【逾期未解决（需重点关注）】")
        for c in overdue:
            days = (date.today() - date.fromisoformat(c["deadline"])).days
            lines.append(f"  #{c['id']} {c['customer']} - {c['problem_type']} | 逾期{days}天 | 跟进:{c['follower']}")
        lines.append("")

    # 按问题类型统计
    type_count = {}
    for c in data["complaints"]:
        type_count[c["problem_type"]] = type_count.get(c["problem_type"], 0) + 1
    lines.append("【历史客诉类型分布】")
    for t, cnt in sorted(type_count.items(), key=lambda x: -x[1]):
        lines.append(f"  {t}: {cnt} 条")
    lines.append("")
    lines.append("=" * 50)

    report_text = "\n".join(lines)
    print(report_text)

    os.makedirs(REPORT_DIR, exist_ok=True)
    filename = f"weekly_report_{mon_str}.txt"
    filepath = os.path.join(REPORT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n✓ 周报已保存至: {filepath}")

if __name__ == "__main__":
    generate_weekly_report()
