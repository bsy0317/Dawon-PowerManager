from rich.console import Console
import multiprocessing
import os
console = Console()

def on_starting(server):
    console.print("[bold green]Server starting...[/bold green]")

def worker_exit(server, worker):
    console.print("[bold red]Worker exit...[/bold red]")

def on_exit(server):
    console.print("[bold red]Server exit...[/bold red]")
    
# Gunicorn 설정
bind = '0.0.0.0:6000'  # 서버가 수신 대기할 주소와 포트
workers = multiprocessing.cpu_count() * 2 + 1

worker_class = 'sync'

# Environment variables
os.environ.setdefault('BIND_ADDRESS', bind)
os.environ.setdefault('GUNICORN_WORKERS', str(workers))