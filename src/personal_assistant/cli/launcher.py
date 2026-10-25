import socket
import subprocess
import sys
import time
import httpx
from .api_client import base_url, set_base_url
from personal_assistant.api.server import DEFAULT_HOST, DEFAULT_PORT

# Maximum time to wait for the server process to accept requests.
STARTUP_TIMEOUT = 10
# Time to wait for the server process to exit before killing it.
SHUTDOWN_TIMEOUT = 5

# Check whether the API answers at the given base URL.
def server_is_ready(url: str) -> bool:
    try:
        response = httpx.get(f'{url}/api/health', timeout=0.5)
        return response.status_code == 200
    except httpx.RequestError:
        return False

# Check whether something already listens on the given local port.
def port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0

# Ask the operating system for a free local port.
def find_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]

# Poll the health endpoint until the server is ready
# or the timeout expires.
def wait_for_server(process: subprocess.Popen, url: str) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('The backend server stopped before becoming ready.')

        if server_is_ready(url):
            return

        time.sleep(0.1)

    raise RuntimeError(f'The backend server did not become ready within {STARTUP_TIMEOUT} seconds.')

# Start the API server as a child process on the given host and port.
def start_server(host: str, port: int) -> subprocess.Popen:
    return subprocess.Popen([
        sys.executable, '-m', 'uvicorn',
        'personal_assistant.api.app:app',
        '--host', host,
        '--port', str(port),
        '--log-level', 'warning',
        '--no-access-log',
    ])

# Stop the child server process, killing it if it does not exit.
def stop_server(process: subprocess.Popen) -> None:
    process.terminate()
    
    try:
        process.wait(timeout=SHUTDOWN_TIMEOUT)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

# Run the console client.
def run_cli() -> None:
    from .main import main as cli_main
    cli_main()

def main() -> None:
    # Build the local API URL.
    api_url = base_url()

    host = DEFAULT_HOST
    port = DEFAULT_PORT

    # Reuse an already running backend, otherwise start one.
    server_process = None
    if not server_is_ready(api_url):
        # The port is taken.
        if port_in_use(host, port):
            port = find_free_port(host)
            api_url = f'http://{host}:{port}'

        server_process = start_server(host, port)

        try:
            wait_for_server(server_process, api_url)
        except RuntimeError as error:
            stop_server(server_process)
            sys.exit(f'Cannot start the backend: {error}')

        print(f'Backend started at {api_url}.')

    # Set the base URL, the port can differ from the
    # default value when it was taken by another application.
    set_base_url(api_url)

    try:
        run_cli()
    finally:
        # Stop the server only if this process started it.
        if server_process is not None:
            stop_server(server_process)

if __name__ == '__main__':
    main()
