#!/usr/bin/env python3
import curses, os, subprocess, threading, time
from datetime import datetime

MACHINES = [
    {"name":"zeta-lab","label":"PC1 · zeta-lab","role":"Orchestrateur / Calcul principal","host":"localhost","user":None,"key":None,"color":"cyan"},
    {"name":"zeta-calc-second","label":"PC2 · zeta-calc-second","role":"Second nœud calcul (E8400 2C)","host":"192.168.1.52","user":"hprzeta","key":"~/.ssh/id_acer","color":"yellow"},
    {"name":"zeta-backup","label":"PC3 · zeta-backup","role":"Backup / monitoring (E2140 2C)","host":"192.168.1.22","user":"hprzeta","key":"~/.ssh/id_acer","color":"blue"},
    {"name":"zeta-secure","label":"PC4 · zeta-secure","role":"Bastion VPN / WireGuard (OpenBSD)","host":"192.168.1.54","user":"hprzeta","key":"~/.ssh/id_acer","color":"green","openbsd":True},
]

REFRESH = 10
CMD_LINUX = ("PYTHONNOUSERSITE=1 python3 -c \""
    "import os,time;"
    "s1=open('/proc/stat').readline().split();"
    "time.sleep(0.5);"
    "s2=open('/proc/stat').readline().split();"
    "d=[int(b)-int(a) for a,b in zip(s1[1:],s2[1:])];"
    "idle=d[3];total=sum(d);"
    "cpu=round(100*(1-idle/total),1) if total else 0;"
    "m=open('/proc/meminfo').read();"
    "mt=int([l for l in m.split(chr(10)) if 'MemTotal' in l][0].split()[1]);"
    "ma=int([l for l in m.split(chr(10)) if 'MemAvailable' in l][0].split()[1]);"
    "mu=round(100*(mt-ma)/mt,1);"
    "la=open('/proc/loadavg').read().split()[:3];"
    "print('{0}|{1}|{2}|{3}|{4}|{5}|{6}'.format(cpu,mt//1024,round((mt-ma)/1024),mu,la[0],la[1],la[2]));"
    "\"")
CMD_OPENBSD = ("top -b -n 1 2>/dev/null | awk '/CPU states/{idle=$(NF-1); gsub(/%/,\"\",idle); printf \"%s|0|0|0|0.00|0.00|0.00\\n\", 100-idle}'")

def ssh_cmd(machine, cmd):
    if machine["host"] == "localhost":
        proc = subprocess.run(["bash","-c",cmd], capture_output=True, text=True, timeout=8)
    else:
        key = os.path.expanduser(machine["key"])
        args = ["ssh","-o","ConnectTimeout=6","-o","StrictHostKeyChecking=no",
                "-o","BatchMode=yes","-o","IdentitiesOnly=yes","-i",key,
                f"{machine['user']}@{machine['host']}",cmd]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=10)
    return proc.stdout.strip(), proc.returncode

state = {m["name"]:{"cpu":None,"ram_total":None,"ram_used":None,"ram_pct":None,
         "load1":None,"load5":None,"load15":None,"status":"init","last_update":None,"error":None}
         for m in MACHINES}
lock = threading.Lock()

def poll_machine(machine):
    name = machine["name"]
    cmd = CMD_OPENBSD if machine.get("openbsd") else CMD_LINUX
    while True:
        try:
            out, rc = ssh_cmd(machine, cmd)
            if rc == 0 and out and "|" in out:
                p = out.split("|")
                if len(p) >= 7:
                    def safe(v, t=float):
                        try: return t(v)
                        except: return None
                    with lock:
                        state[name].update({"cpu":safe(p[0]),"ram_total":safe(p[1],int),
                            "ram_used":safe(p[2],int),"ram_pct":safe(p[3]),
                            "load1":p[4],"load5":p[5],"load15":p[6],
                            "status":"ok","error":None,
                            "last_update":datetime.now().strftime("%H:%M:%S")})
                else: raise ValueError(f"parse:{out}")
            else: raise ConnectionError(f"rc={rc}")
        except Exception as e:
            with lock:
                state[name].update({"status":"err","error":str(e)[:60],
                    "last_update":datetime.now().strftime("%H:%M:%S")})
        time.sleep(REFRESH)

COLORS = {"cyan":curses.COLOR_CYAN,"yellow":curses.COLOR_YELLOW,"green":curses.COLOR_GREEN,
          "magenta":curses.COLOR_MAGENTA,"red":curses.COLOR_RED,"white":curses.COLOR_WHITE,
          "blue":curses.COLOR_BLUE}
PAIR = {}

def init_colors():
    curses.start_color(); curses.use_default_colors()
    idx = 1
    for n,fg in COLORS.items(): curses.init_pair(idx,fg,-1); PAIR[n]=idx; idx+=1
    curses.init_pair(idx,curses.COLOR_BLACK,curses.COLOR_GREEN);  PAIR["ok"]=idx;   idx+=1
    curses.init_pair(idx,curses.COLOR_BLACK,curses.COLOR_YELLOW); PAIR["warn"]=idx; idx+=1
    curses.init_pair(idx,curses.COLOR_BLACK,curses.COLOR_RED);    PAIR["crit"]=idx; idx+=1
    curses.init_pair(idx,curses.COLOR_BLACK,curses.COLOR_WHITE);  PAIR["bg"]=idx;   idx+=1

def bar(stdscr, y, x, pct, width=22, label=""):
    if pct is None:
        stdscr.addstr(y,x,"["+"?"*width+"]",curses.color_pair(PAIR["white"])); return
    filled = int(width*pct/100)
    color = PAIR["ok"] if pct<60 else (PAIR["warn"] if pct<85 else PAIR["crit"])
    stdscr.addstr(y,x,"[",curses.color_pair(PAIR["white"]))
    stdscr.addstr(y,x+1,"█"*filled,curses.color_pair(color))
    stdscr.addstr(y,x+1+filled,"░"*(width-filled),curses.color_pair(PAIR["bg"]))
    stdscr.addstr(y,x+1+width,f"] {pct:5.1f}% {label}",curses.color_pair(PAIR["white"]))

def draw(stdscr):
    init_colors(); curses.curs_set(0); stdscr.nodelay(True)
    while True:
        stdscr.erase(); h,w = stdscr.getmaxyx()
        title = "  ζ  CLUSTER ZETA — MONITOR  ζ  "
        stdscr.addstr(0,max(0,(w-len(title))//2),title,curses.color_pair(PAIR["cyan"])|curses.A_BOLD)
        stdscr.addstr(1,2,f"Refresh:{REFRESH}s | {datetime.now().strftime('%H:%M:%S')} | q=quitter",curses.color_pair(PAIR["white"]))
        stdscr.addstr(2,0,"─"*w,curses.color_pair(PAIR["white"]))
        row=3
        with lock: snap={k:dict(v) for k,v in state.items()}
        for i,m in enumerate(MACHINES):
            s=snap[m["name"]]
            cp=curses.color_pair(PAIR[m["color"]])|curses.A_BOLD
            sym="✓" if s["status"]=="ok" else ("…" if s["status"]=="init" else "✗")
            sc=PAIR["green"] if s["status"]=="ok" else (PAIR["yellow"] if s["status"]=="init" else PAIR["red"])
            stdscr.addstr(row,2,f"[{sym}] ",curses.color_pair(sc)|curses.A_BOLD)
            stdscr.addstr(row,7,m["label"],cp)
            rx=7+len(m["label"])+2
            if rx<w-20: stdscr.addstr(row,rx,m["role"],curses.color_pair(PAIR["white"]))
            row+=1
            if s["status"]=="err":
                stdscr.addstr(row,6,f"⚠  {s['error']}",curses.color_pair(PAIR["red"])); row+=1
            elif s["status"]=="init":
                stdscr.addstr(row,6,"Connexion...",curses.color_pair(PAIR["yellow"])); row+=1
            else:
                stdscr.addstr(row,4,"CPU ",curses.color_pair(PAIR["white"])|curses.A_BOLD)
                bar(stdscr,row,8,s["cpu"])
                ls=f"  load:{s['load1']} {s['load5']} {s['load15']}"
                if 8+22+12+len(ls)<w: stdscr.addstr(row,8+22+12,ls,curses.color_pair(PAIR["white"]))
                row+=1
                stdscr.addstr(row,4,"RAM ",curses.color_pair(PAIR["white"])|curses.A_BOLD)
                rl=f"{s['ram_used']}M/{s['ram_total']}M" if s["ram_used"] and s["ram_total"] else ""
                bar(stdscr,row,8,s["ram_pct"],label=rl); row+=1
                stdscr.addstr(row,6,f"MAJ:{s['last_update']}",curses.color_pair(PAIR["white"])); row+=1
            if i<len(MACHINES)-1: stdscr.addstr(row,2,"·"*(w-4),curses.color_pair(PAIR["white"]))
            row+=1
            if row>=h-2: break
        footer=" zeta_monitor.py · hprzeta · 2026-06-16 "
        try: stdscr.addstr(h-1,max(0,(w-len(footer))//2),footer,curses.color_pair(PAIR["white"]))
        except: pass
        stdscr.refresh()
        if stdscr.getch() in (ord('q'),ord('Q')): break
        time.sleep(1)

def main():
    for m in MACHINES: threading.Thread(target=poll_machine,args=(m,),daemon=True).start()
    curses.wrapper(draw)

if __name__=="__main__": main()
