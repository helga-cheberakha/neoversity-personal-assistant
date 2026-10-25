import uvicorn
import argparse

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8000

# Parse command line options.
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the Personal Assistant API server.')
    parser.add_argument(
        '--host',
        default=DEFAULT_HOST,
        help=f'Interface to listen on: {DEFAULT_HOST}.',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Port to listen on: {DEFAULT_PORT}.',
    )
    return parser.parse_args()

def main() -> None:
    args = parse_args()

    # Run the API application.
    uvicorn.run('personal_assistant.api.app:app', host=args.host, port=args.port)

if __name__ == '__main__':
    main()
