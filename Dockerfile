# Dockerfile
# Testing automatic build

FROM python:3.10.7

WORKDIR app/

# A venv's whole purpose is to isolate one 
# project's dependencies from your machine's
# global Python and from other projects on the
# same machine. But a Docker container is already isolated
# - it's the whole point of a container. There's no "other project"
# or "global system Python" competing for space inside this image; 
# the container's Python is this app's Python.

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY config.py .
COPY main.py .
COPY JobExecutionViewer.py .
COPY DemandDataViewer.py .
COPY CloudStorage.py .

# FAQ: Difference between address and port.
# Address (IP) — which network interface the server listens on. A machine can have multiple network interfaces (e.g. loopback, a LAN interface, a public interface), and the address tells the server which one(s) to accept connections through.
## 127.0.0.1 (aka localhost) — only accepts connections that originate from inside the same machine/container. Nothing external can reach it, even if the port is "open," because the OS never routes outside traffic to that interface.
## 0.0.0.0 — means "listen on every available network interface." This is what makes the server reachable from outside the container.

# Port — which "door" on that interface the server is listening at. A single IP address can have thousands of ports, each potentially running a different service. The port is how the OS knows which running process should receive a given piece of incoming traffic (port 8080 → your Streamlit app, port 5432 → maybe a database, etc).

CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
