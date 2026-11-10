"""Local-only bag scheduler dashboard. No TGTG network or payment operations.

Run: python pi_dashboard.py
Visit http://127.0.0.1:8765
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock, Thread
from zoneinfo import ZoneInfo

from monitoring import SimulatedAvailability
from purchase_limits import dollars_to_cents
from simulated_checkout import (
    recover_simulated_reservations,
    simulate_checkout,
)

DB = Path(os.environ.get("TGTG_DASHBOARD_DB", "bag-dashboard.sqlite3"))
TZ = ZoneInfo(os.environ.get("TGTG_TIMEZONE", "America/New_York"))
LOCK = RLock()
HTML = """<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bag Watchlist</title><style>
body{font:16px system-ui;max-width:680px;margin:30px auto;padding:0 14px;background:#f7f8fa;color:#18202a}
h1{font-size:26px}.item{display:flex;align-items:center;gap:12px;background:white;border:1px solid #ddd;border-radius:12px;padding:14px;margin:10px 0}
.handle{cursor:grab;touch-action:none;font-size:24px;color:#777;user-select:none;min-width:32px;text-align:center}.details{flex:1;min-width:0}
small{display:block;color:#666;margin-top:5px}input,button{font:inherit}input[type=time]{max-width:110px}
button{border:1px solid #ccc;border-radius:8px;background:white;padding:8px;cursor:pointer}
form{display:flex;gap:8px;flex-wrap:wrap} .schedule{display:flex;gap:6px;align-items:center;flex-wrap:wrap} .schedule input{width:64px}form input{padding:8px;min-width:0}
</style><h1>Bag Watchlist</h1><p>Drag to prioritize. Bags turn off after a completed session.</p>
<form id="add"><input name="name" placeholder="Bag name" required><input name="time" type="time" required><input name="price" type="number" min="0" step="0.01" placeholder="Bag price $" required><input name="duration" type="number" min="1" max="120" value="5" title="Window minutes"><button>Add</button></form>
<section><h2>Daily purchase limits</h2><p>Leave either blank for no limit. Applies to all bags combined.</p>
<label>Max spend ($) <input id="maxDollars" type="number" min="0" step="0.01" placeholder="No limit"></label>
<label>Max bags <input id="maxBags" type="number" min="0" step="1" placeholder="No limit"></label>
<button type="button" id="saveLimits">Save limits</button><p id="limitStatus" role="status"></p><p id="purchaseSummary"></p></section>
<div id="items"></div><p id="message" role="status"></p>
<script>
let bags=[],dragged=null;
const root=document.querySelector('#items'),msg=document.querySelector('#message');
async function api(path,method='GET',body){const r=await fetch(path,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});if(!r.ok)throw Error((await r.json()).error);return r.json()}
async function refresh(){bags=await api('/api/bags');render()}
function node(tag,cls,content){const el=document.createElement(tag);if(cls)el.className=cls;if(content!==undefined)el.textContent=content;return el}
async function update(id,data){try{await api('/api/bags/'+id,'PATCH',data);await refresh()}catch(e){msg.textContent=e.message}}
function render(){root.replaceChildren();bags.forEach((b,i)=>{
 const row=node('div','item');row.draggable=true;row.dataset.id=b.id;
 const handle=node('span','handle','⠿');handle.setAttribute('aria-label','Drag to reorder');
 let touchStart=null;
 handle.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse')return;touchStart={id:b.id,y:e.clientY};handle.setPointerCapture(e.pointerId);});
 handle.addEventListener('pointerup',async e=>{if(!touchStart)return;const start=touchStart;touchStart=null;
 const rows=[...root.querySelectorAll('.item')];const dy=e.clientY-start.y;
 const rowHeight=row.getBoundingClientRect().height+10;
 const steps=Math.round(dy/rowHeight);
 if(steps!==0)await move(i,Math.max(0,Math.min(bags.length-1,i+steps)));
 });
 handle.addEventListener('pointercancel',()=>{touchStart=null});
 const details=node('div','details');details.append(node('strong','',b.name),node('small','',b.status+' · '+(b.arm_date||'not armed')+' · $'+(b.price_cents===null?'?':(b.price_cents/100).toFixed(2))+' · Priority '+(i+1)));
 const time=node('input');time.type='time';time.value=b.drop_time;time.title='Daily drop time';time.onchange=()=>update(b.id,{drop_time:time.value});
 const duration=node('input');duration.type='number';duration.min=1;duration.max=120;duration.value=b.window_minutes;duration.title='Monitoring window (minutes)';duration.onchange=()=>update(b.id,{window_minutes:Number(duration.value)});
 const days=node('select');days.title='Schedule';for(const [v,t] of [['all','Every day'],['weekdays','Weekdays'],['weekends','Weekends']]){const o=node('option','',t);o.value=v;days.append(o)}days.value=b.days;days.onchange=()=>update(b.id,{days:days.value});
 const price=node('input');price.type='number';price.min=0;price.step='0.01';price.value=b.price_cents===null?'':(b.price_cents/100).toFixed(2);price.title='Bag price';price.onchange=()=>update(b.id,{price:price.value});
 const toggle=node('input');toggle.type='checkbox';toggle.checked=b.enabled;toggle.setAttribute('aria-label','Enable '+b.name);toggle.onchange=()=>update(b.id,{enabled:toggle.checked});
 const up=node('button','', '↑');up.title='Move up';up.onclick=()=>move(i,i-1);
 const down=node('button','','↓');down.title='Move down';down.onclick=()=>move(i,i+1);
 row.append(handle,details,time,duration,days,price,toggle,up,down);
 row.addEventListener('dragstart',e=>{dragged=b.id;e.dataTransfer.effectAllowed='move'});
 row.addEventListener('dragover',e=>e.preventDefault());
 row.addEventListener('drop',async e=>{e.preventDefault();const from=bags.findIndex(x=>x.id===dragged);await move(from,i)});
 root.append(row);
 })}
async function move(from,to){if(from<0||to<0||to>=bags.length||from===to)return;const next=[...bags];next.splice(to,0,next.splice(from,1)[0]);try{await api('/api/order','PUT',{ids:next.map(x=>x.id)});await refresh()}catch(e){msg.textContent=e.message}}
document.querySelector('#add').onsubmit=async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));try{await api('/api/bags','POST',data);e.target.reset();await refresh()}catch(err){msg.textContent=err.message}};
async function loadLimits(){const limits=await api('/api/limits');document.querySelector('#maxDollars').value=limits.max_cents===null?'':(limits.max_cents/100).toFixed(2);document.querySelector('#maxBags').value=limits.max_bags??''}
document.querySelector('#saveLimits').onclick=async()=>{try{const dollars=document.querySelector('#maxDollars').value;const bags=document.querySelector('#maxBags').value;await api('/api/limits','PUT',{max_dollars:dollars===''?null:dollars,max_bags:bags===''?null:Number(bags)});document.querySelector('#limitStatus').textContent='Saved'}catch(e){document.querySelector('#limitStatus').textContent=e.message}};
async function loadSummary(){try{const s=await api('/api/purchase-summary');document.querySelector('#purchaseSummary').textContent='Today reserved/simulated: $'+(s.cents/100).toFixed(2)+' · '+s.bags+' bags · Remaining: '+(s.remaining_cents===null?'Unlimited dollars':'$'+(s.remaining_cents/100).toFixed(2))+' / '+(s.remaining_bags===null?'Unlimited bags':s.remaining_bags+' bags')}catch(e){msg.textContent=e.message}}
refresh().catch(e=>msg.textContent=e.message);loadLimits().catch(e=>msg.textContent=e.message);loadSummary();
</script></html>"""


def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS bags (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, drop_time TEXT NOT NULL,
            priority INTEGER NOT NULL, enabled INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'disabled', last_session TEXT,
            window_minutes INTEGER NOT NULL DEFAULT 5,
            days TEXT NOT NULL DEFAULT 'all', arm_date TEXT, price_cents INTEGER)""")
        cols = {row[1] for row in db.execute("PRAGMA table_info(bags)")}
        if "window_minutes" not in cols:
            db.execute("ALTER TABLE bags ADD COLUMN window_minutes INTEGER NOT NULL DEFAULT 5")
        if "arm_date" not in cols:
            db.execute("ALTER TABLE bags ADD COLUMN arm_date TEXT")
        db.execute("UPDATE bags SET enabled=0,status='disabled' WHERE enabled=1 AND arm_date IS NULL")
        if "price_cents" not in cols:
            db.execute("ALTER TABLE bags ADD COLUMN price_cents INTEGER")
        db.execute("""CREATE TABLE IF NOT EXISTS purchase_limits (
            id INTEGER PRIMARY KEY CHECK(id=1),
            max_cents INTEGER, max_bags INTEGER)""")
        db.execute("INSERT OR IGNORE INTO purchase_limits(id,max_cents,max_bags) VALUES(1,NULL,NULL)")
        db.execute("""CREATE TABLE IF NOT EXISTS purchase_reservations (
            id INTEGER PRIMARY KEY, bag_id INTEGER NOT NULL,
            purchase_day TEXT NOT NULL, price_cents INTEGER NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('pending','confirmed','cancelled')),
            UNIQUE(bag_id,purchase_day))""")
        if "days" not in cols:
            db.execute("ALTER TABLE bags ADD COLUMN days TEXT NOT NULL DEFAULT 'all'")
        db.execute("""CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY, bag_id INTEGER NOT NULL,
            arm_date TEXT NOT NULL, observed_at TEXT NOT NULL,
            available INTEGER NOT NULL,
            UNIQUE(bag_id, arm_date, available))""")


def list_bags(db):
    return [dict(row) | {"enabled": bool(row["enabled"])}
            for row in db.execute("SELECT * FROM bags ORDER BY priority,id")]


def next_arm_date(bag, now):
    hh, mm = map(int, bag["drop_time"].split(":"))
    for offset in range(8):
        day = (now + timedelta(days=offset)).date()
        start = datetime(day.year, day.month, day.day, hh, mm, tzinfo=TZ)
        end = start + timedelta(minutes=bag["window_minutes"])
        allowed = bag["days"] == "all" or (bag["days"] == "weekdays" and day.weekday() < 5) or (bag["days"] == "weekends" and day.weekday() >= 5)
        if allowed and now < end:
            return day.isoformat()
    raise ValueError("No eligible monitoring day")


def expire_sessions(db, now=None):
    """Run only explicitly armed occurrences; never automatically rearm."""
    now = now or datetime.now(TZ)
    for bag in list_bags(db):
        if not bag["enabled"] or not bag["arm_date"]:
            continue
        hh, mm = map(int, bag["drop_time"].split(":"))
        day = datetime.strptime(bag["arm_date"], "%Y-%m-%d").date()
        start = datetime(day.year, day.month, day.day, hh, mm, tzinfo=TZ)
        end = start + timedelta(minutes=bag["window_minutes"])
        if now >= end:
            db.execute("UPDATE bags SET enabled=0,status='timed_out',last_session=? WHERE id=?", (bag["arm_date"], bag["id"]))
        elif now >= start and bag["status"] == "armed":
            db.execute("UPDATE bags SET status='watching',last_session=? WHERE id=?", (bag["arm_date"], bag["id"]))


def observe_simulated(db, source, now=None):
    """Persist each availability transition, emitting at most one available alert per session."""
    now = now or datetime.now(TZ)
    events = []
    for bag in list_bags(db):
        if not bag["enabled"] or bag["status"] != "watching" or not bag["arm_date"]:
            continue
        result = source.check(bag["id"])
        previous = db.execute(
            "SELECT id,available FROM observations WHERE bag_id=? AND arm_date=? ORDER BY id DESC LIMIT 1",
            (bag["id"], bag["arm_date"]),
        ).fetchone()
        if previous is not None and bool(previous["available"]) == bool(result.available):
            continue
        if previous is None:
            db.execute(
                "INSERT INTO observations(bag_id,arm_date,observed_at,available) VALUES(?,?,?,?)",
                (bag["id"], bag["arm_date"], now.isoformat(), int(result.available)),
            )
        else:
            # The legacy schema uniquely indexes (bag, day, available).
            # Remove prior state before inserting the latest transition.
            db.execute(
                "DELETE FROM observations WHERE bag_id=? AND arm_date=?",
                (bag["id"], bag["arm_date"]),
            )
            db.execute(
                "INSERT INTO observations(bag_id,arm_date,observed_at,available) "
                "VALUES(?,?,?,?)",
                (bag["id"], bag["arm_date"], now.isoformat(), int(result.available)),
            )
        if result.available:
            events.append({"bag_id": bag["id"], "arm_date": bag["arm_date"],
                           "event": "available_simulated"})
    return events


def scheduler_loop(interval_seconds=0.25, source=None):
    """Tick session state frequently without relying on browser refreshes.

    Database transactions are committed per tick; failures are logged and
    retried on the next tick rather than terminating the web server.
    """
    while True:
        try:
            with LOCK, connect() as db:
                expire_sessions(db)
                if source is not None:
                    for event in observe_simulated(db, source):
                        print(f"SIMULATION {event}", flush=True)
                    if os.environ.get("TGTG_SIMULATE_CHECKOUT") == "1":
                        for bag_id in simulate_checkout(db, datetime.now(TZ)):
                            print(f"SIMULATED PURCHASE bag={bag_id}; NO PAYMENT", flush=True)
        except (OSError, sqlite3.Error, ValueError) as exc:
            print(f"Scheduler tick failed: {exc}", flush=True)
        time.sleep(interval_seconds)


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, data, content_type="application/json"):
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 8192:
            raise ValueError("Request too large")
        return json.loads(self.rfile.read(size))

    def do_GET(self):
        if self.path == "/":
            return self.respond(200, HTML, "text/html; charset=utf-8")
        if self.path == "/api/purchase-history":
            with LOCK, connect() as db:
                rows = db.execute(
                    "SELECT r.bag_id,b.name,r.purchase_day,r.price_cents,r.state "
                    "FROM purchase_reservations r LEFT JOIN bags b ON b.id=r.bag_id "
                    "ORDER BY r.purchase_day DESC,r.id DESC LIMIT 100"
                ).fetchall()
                return self.respond(200, [dict(row) for row in rows])
        if self.path == "/api/purchase-summary":
            day = datetime.now(TZ).date().isoformat()
            with LOCK, connect() as db:
                totals = db.execute(
                    "SELECT COALESCE(SUM(price_cents),0) AS cents,COUNT(*) AS bags "
                    "FROM purchase_reservations WHERE purchase_day=? "
                    "AND state IN ('pending','confirmed')", (day,)
                ).fetchone()
                caps = db.execute("SELECT max_cents,max_bags FROM purchase_limits WHERE id=1").fetchone()
                return self.respond(200, dict(totals) | {
                    "day": day, "simulated": True,
                    "max_cents": caps["max_cents"], "max_bags": caps["max_bags"],
                    "remaining_cents": None if caps["max_cents"] is None else max(0, caps["max_cents"] - totals["cents"]),
                    "remaining_bags": None if caps["max_bags"] is None else max(0, caps["max_bags"] - totals["bags"]),
                })
        if self.path == "/api/limits":
            with LOCK, connect() as db:
                return self.respond(200, dict(db.execute(
                    "SELECT max_cents,max_bags FROM purchase_limits WHERE id=1").fetchone()))
        if self.path == "/api/observations":
            with LOCK, connect() as db:
                rows = db.execute(
                    "SELECT bag_id,arm_date,observed_at,available FROM observations "
                    "ORDER BY id DESC LIMIT 100"
                ).fetchall()
                return self.respond(200, [dict(row) for row in rows])
        if self.path == "/api/bags":
            with LOCK, connect() as db:
                expire_sessions(db)
                return self.respond(200, list_bags(db))
        self.respond(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/bags":
            return self.respond(404, {"error": "Not found"})
        try:
            body = self.read_json()
            name = str(body["name"]).strip()
            time = str(body["time"])
            duration = int(body.get("duration", 5))
            price_cents = dollars_to_cents(body["price"])
            if not 1 <= duration <= 120:
                raise ValueError("Window must be 1-120 minutes")
            datetime.strptime(time, "%H:%M")
            if not name or len(name) > 120:
                raise ValueError("Invalid name")
            with LOCK, connect() as db:
                priority = db.execute("SELECT COALESCE(MAX(priority),0)+1 FROM bags").fetchone()[0]
                db.execute("INSERT INTO bags(name,drop_time,priority,window_minutes,price_cents,enabled,status) VALUES(?,?,?,?,?,0,'disabled')",
                           (name, time, priority, duration, price_cents))
            self.respond(201, {"ok": True})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.respond(400, {"error": str(e)})

    def do_PATCH(self):
        if not self.path.startswith("/api/bags/"):
            return self.respond(404, {"error": "Not found"})
        try:
            bag_id = int(self.path.rsplit("/", 1)[-1])
            body = self.read_json()
            if set(body) - {"enabled", "drop_time", "window_minutes", "days", "price"} or not body:
                raise ValueError("Unsupported fields")
            if "enabled" in body and not isinstance(body["enabled"], bool):
                raise ValueError("enabled must be boolean")
            if "drop_time" in body:
                datetime.strptime(body["drop_time"], "%H:%M")
            if "window_minutes" in body and (type(body["window_minutes"]) is not int or not 1 <= body["window_minutes"] <= 120):
                raise ValueError("Window must be 1-120 minutes")
            if "price" in body:
                price_cents = dollars_to_cents(body["price"])
            if "days" in body and body["days"] not in ("all", "weekdays", "weekends"):
                raise ValueError("Invalid days")
            with LOCK, connect() as db:
                row = db.execute("SELECT * FROM bags WHERE id=?", (bag_id,)).fetchone()
                if row is None:
                    raise ValueError("Bag not found")
                if "enabled" in body:
                    arm_date = next_arm_date(dict(row) | body, datetime.now(TZ)) if body["enabled"] else None
                    db.execute("UPDATE bags SET enabled=?,status=?,last_session=NULL,arm_date=? WHERE id=?",
                               (int(body["enabled"]), "armed" if body["enabled"] else "disabled", arm_date, bag_id))
                if "drop_time" in body:
                    db.execute("UPDATE bags SET drop_time=? WHERE id=?", (body["drop_time"], bag_id))
                if "window_minutes" in body:
                    db.execute("UPDATE bags SET window_minutes=? WHERE id=?", (body["window_minutes"], bag_id))
                if "days" in body:
                    db.execute("UPDATE bags SET days=? WHERE id=?", (body["days"], bag_id))
                if "price" in body:
                    db.execute("UPDATE bags SET price_cents=? WHERE id=?", (price_cents, bag_id))
                if row["enabled"] and "enabled" not in body and any(k in body for k in ("drop_time", "window_minutes", "days")):
                    new_date = next_arm_date(dict(row) | body, datetime.now(TZ))
                    db.execute("UPDATE bags SET arm_date=?,status='armed',last_session=NULL WHERE id=?",
                               (new_date, bag_id))
                expire_sessions(db)
            self.respond(200, {"ok": True})
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            self.respond(400, {"error": str(e)})

    def do_PUT(self):
        if self.path == "/api/limits":
            try:
                body = self.read_json()
                if set(body) != {"max_dollars", "max_bags"}:
                    raise ValueError("Both limit fields required")
                max_cents = None if body["max_dollars"] is None else dollars_to_cents(body["max_dollars"])
                max_bags = body["max_bags"]
                if max_bags is not None and (type(max_bags) is not int or max_bags < 0):
                    raise ValueError("Max bags must be a nonnegative integer")
                with LOCK, connect() as db:
                    db.execute("UPDATE purchase_limits SET max_cents=?,max_bags=? WHERE id=1",
                               (max_cents, max_bags))
                return self.respond(200, {"ok": True})
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                return self.respond(400, {"error": str(exc)})
        if self.path != "/api/order":
            return self.respond(404, {"error": "Not found"})
        try:
            ids = self.read_json()["ids"]
            with LOCK, connect() as db:
                actual = [b["id"] for b in list_bags(db)]
                if not isinstance(ids, list) or any(type(i) is not int for i in ids) or len(ids) != len(actual) or set(ids) != set(actual):
                    raise ValueError("Order must contain every bag exactly once")
                for priority, bag_id in enumerate(ids, 1):
                    db.execute("UPDATE bags SET priority=? WHERE id=?", (priority, bag_id))
            self.respond(200, {"ok": True})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            self.respond(400, {"error": str(e)})


if __name__ == "__main__":
    initialize()
    print("Dashboard: http://127.0.0.1:8765 (local only; no checkout)")
    tick_seconds = float(os.environ.get("TGTG_SCHEDULER_TICK_SECONDS", "0.25"))
    if not 0.05 <= tick_seconds <= 60:
        raise ValueError("TGTG_SCHEDULER_TICK_SECONDS must be between 0.05 and 60")
    # Simulation is opt-in; never issue remote inventory or checkout requests.
    simulated_ids = os.environ.get("TGTG_SIMULATED_AVAILABLE_IDS", "").strip()
    source = SimulatedAvailability(
        [int(part.strip()) for part in simulated_ids.split(",") if part.strip()]
    ) if simulated_ids else None
    with LOCK, connect() as db:
        recovered = recover_simulated_reservations(db)
    if recovered:
        print(f"Recovered {recovered} simulated pending reservations", flush=True)
    Thread(target=scheduler_loop, args=(tick_seconds, source), daemon=True,
           name="bag-scheduler").start()
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
