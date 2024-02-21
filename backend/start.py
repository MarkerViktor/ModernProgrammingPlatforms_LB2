import logging

from aiohttp import web

from src.main import init


def start():
    logging.basicConfig(level=logging.INFO)
    web.run_app(init(), port=8080)


if __name__ == "__main__":
    start()
