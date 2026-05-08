#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, os
from datetime import datetime, date, timedelta

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "complaints.json")

SEVERITY_LEVELS = ["低", "中", "高", "紧急"]
PROBLEM_TYPES = ["产品质量", "服务态度", "交付延迟", "账单问题", "技术故障", "其他"]
STATUS_OPTIONS = ["待处理", "处理中", "已解决", "已关闭"]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"complaints": [], "next_id": 1}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_stats(complaints):
    today = date.today().strftime("%Y-%m-%d")
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    active = [c for c in complaints if c["status"] not in ("已解决", "已关闭")]
    return {
        "total": len(complaints),
        "active": len(active),
        "overdue": sum(1 for c in active if c["deadline"] < today),
        "due_today": sum(1 for c in active if c["deadline"] == today),
        "due_tomorrow": sum(1 for c in active if c["deadline"] == tomorrow),
        "resolved": sum(1 for c in complaints if c["status"] in ("已解决", "已关闭")),
    }

@app.route("/")
def index():
    data = load_data()
    stats = get_stats(data["complaints"])
    today = date.today().strftime("%Y-%m-%d")
    urgent = [c for c in data["complaints"]
              if c["status"] not in ("已解决", "已关闭") and c["deadline"] <= today]
    return render_template("index.html", stats=stats, urgent=urgent)

@app.route("/list")
def complaint_list():
    data = load_data()
    status_f = request.args.get("status", "")
    follower_f = request.args.get("follower", "")
    items = data["complaints"]
    if status_f:
        items = [c for c in items if c["status"] == status_f]
    if follower_f:
        items = [c for c in items if c["follower"] == follower_f]
    today = date.today().strftime("%Y-%m-%d")
    followers = sorted(set(c["follower"] for c in data["complaints"] if c["follower"]))
    return render_template("list.html", items=items, today=today,
                           status_f=status_f, follower_f=follower_f,
                           status_options=STATUS_OPTIONS, followers=followers)

@app.route("/add", methods=["GET", "POST"])
def add_complaint():
    if request.method == "POST":
        data = load_data()
        deadline = request.form.get("deadline", "")
        if not deadline:
            deadline = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        complaint = {
            "id": data["next_id"],
            "customer": request.form.get("customer", "").strip(),
            "problem_type": request.form.get("problem_type", "其他"),
            "severity": request.form.get("severity", "中"),
            "follower": request.form.get("follower", "").strip(),
            "deadline": deadline,
            "description": request.form.get("description", "").strip(),
            "status": "待处理",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "notes": []
        }
        data["complaints"].append(complaint)
        data["next_id"] += 1
        save_data(data)
        return redirect(url_for("complaint_list"))
    return render_template("add.html", problem_types=PROBLEM_TYPES,
                           severity_levels=SEVERITY_LEVELS,
                           default_deadline=(date.today() + timedelta(days=7)).strftime("%Y-%m-%d"))

@app.route("/detail/<int:cid>", methods=["GET", "POST"])
def detail(cid):
    data = load_data()
    complaint = next((c for c in data["complaints"] if c["id"] == cid), None)
    if not complaint:
        return redirect(url_for("complaint_list"))
    if request.method == "POST":
        new_status = request.form.get("status")
        note = request.form.get("note", "").strip()
        if new_status in STATUS_OPTIONS:
            complaint["status"] = new_status
        if note:
            complaint["notes"].append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note})
        complaint["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_data(data)
        return redirect(url_for("detail", cid=cid))
    return render_template("detail.html", c=complaint, status_options=STATUS_OPTIONS)

@app.route("/api/stats")
def api_stats():
    data = load_data()
    return jsonify(get_stats(data["complaints"]))

if __name__ == "__main__":
    import threading, webbrowser
    def open_browser():
        import time; time.sleep(1)
        webbrowser.open("http://localhost:5000")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, host="0.0.0.0", port=5000)
