# Dockerfile
# Testing automatic build

FROM python:3.10.7

# EXPOSE 8501 is documentation, not a functional networking command
# — worth being precise about what it actually does versus what people
# assume it does.

# It tells anyone reading the Dockerfile (and tools like docker inspect)
# that the containerized app listens on port 8501 internally. It's
# metadata baked into the image. That's it — it doesn't open the port,
# forward traffic, or make anything reachable from outside the container
# by itself.

# Why 8501 specifically

# That's just Streamlit's default port — when you run streamlit run
# app.py, it binds to localhost:8501 unless told otherwise. So EXPOSE
# 8501 in the Dockerfile matches what Streamlit is actually doing inside
# the container.

EXPOSE 8501

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

COPY DemandDataLoader.py .
COPY DataTransformer.py .
COPY main.py .
COPY weather_config.py .
COPY WeatherDataLoader.py .

# FAQ: Difference between address and port.
# Address (IP) — which network interface the server listens on. A machine can have multiple network interfaces (e.g. loopback, a LAN interface, a public interface), and the address tells the server which one(s) to accept connections through.
## 127.0.0.1 (aka localhost) — only accepts connections that originate from inside the same machine/container. Nothing external can reach it, even if the port is "open," because the OS never routes outside traffic to that interface.
## 0.0.0.0 — means "listen on every available network interface." This is what makes the server reachable from outside the container.

# Port — which "door" on that interface the server is listening at. A single IP address can have thousands of ports, each potentially running a different service. The port is how the OS knows which running process should receive a given piece of incoming traffic (port 8080 → your Streamlit app, port 5432 → maybe a database, etc).

CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
