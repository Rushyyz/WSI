from cx_Freeze import setup, Executable
import sys

# Definir base apenas para Windows GUI apps
base = None
if sys.platform == "win32":
    base = None  # Deixe como None se for console
    # Se for um aplicativo GUI (ex: Tkinter, PyQt), use "Win32GUI"

executables = [
  #  Executable("coletor_logs.py", base=base),
  #  Executable("grafico_uso.py", base=base),
  #  Executable("monitor_space.py", base=base), 
  #  Executable("latency_monitor.py", base=base),
  #  Executable("plot_latency_data.py", base=base),
    Executable("SQL.py", base=base)
]

setup(
    name="bdbscripts",
    version="0.1",
    description="bdbscripts",
    executables=executables
)
