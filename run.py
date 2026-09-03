import webbrowser
import threading
import time
from app import app

def open_browser(port):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"[Launcher] Opening web dashboard in browser: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    PORT = 5000
    threading.Thread(target=open_browser, args=(PORT,), daemon=True).start()
    print(f"==========================================================")
    print(f"🌟 AI Multi-Model Analytics Hub (Diabetes, House, Ecom) 🌟")
    print(f"👉 Local URL: http://127.0.0.1:{PORT}")
    print(f"==========================================================")
    app.run(host="127.0.0.1", port=PORT, debug=False)
