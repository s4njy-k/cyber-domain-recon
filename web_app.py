import os
import subprocess
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import logging

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the reports directory to serve images and report.md
if os.path.exists("reports"):
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")

class ScanRequest(BaseModel):
    domains: List[str]

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/api/scan")
def launch_scan(request: ScanRequest):
    domains = [d.strip() for d in request.domains if d.strip()]
    if not domains:
        return {"status": "error", "message": "No valid domains provided."}
        
    # Write to domains.txt
    with open("domains.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(domains))
        
    # Start the python processor as a background daemon
    # Clean previous log
    if os.path.exists("scan.log"):
        os.remove("scan.log")
        
    try:
        subprocess.Popen(
            "nohup python main.py > scan.log 2>&1 &",
            shell=True,
            env=os.environ.copy()
        )
        return {"status": "success", "message": f"Pipeline triggered for {len(domains)} domains."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/status")
def get_status():
    if not os.path.exists("scan.log"):
        return {"phase": "idle", "progress": 0, "total": 0, "message": "Queue is idle."}
        
    with open("domains.txt", "r") as df:
        total_domains = len([l for l in df if l.strip()])
        
    scanned_count = 0
    analyzed_count = 0
    last_line = ""
    
    with open("scan.log", "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            last_line = line
            if "Scanning https" in line:
                scanned_count += 1
            if "Generating content" in line:
                analyzed_count += 1
                
    if "Done!" in last_line:
        return {"phase": "complete", "progress": total_domains, "total": total_domains, "message": "Scan Complete! Report published."}
        
    if analyzed_count > 0:
        return {"phase": "analysis", "progress": analyzed_count, "total": total_domains, "message": f"AI Parsing: {analyzed_count}/{total_domains}"}
    
    if scanned_count > 0:
        return {"phase": "recon", "progress": scanned_count, "total": total_domains, "message": f"Puppeteer Recon: {scanned_count}/{total_domains}"}
        
    return {"phase": "init", "progress": 0, "total": total_domains, "message": "Initializing modules..."}

@app.get("/api/report")
def get_report():
    if not os.path.exists("reports/report.md"):
        return {"content": "Report not generated yet. Please run a scan."}
    with open("reports/report.md", "r", encoding="utf-8") as f:
        return {"content": f.read()}
