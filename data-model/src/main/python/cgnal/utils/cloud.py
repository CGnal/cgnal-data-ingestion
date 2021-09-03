import os
import http.server

import cgi
import requests

from typing import Callable
from cgnal import PathLike
from cgnal.logging.defaults import WithLogging
from cgnal.utils.fs import create_dir_if_not_exists


class CloudSync(WithLogging):

    def __init__(self, url: str, root: PathLike) -> None:
        self.url = url
        self.root = root

    def pathTo(self, filename: PathLike) -> PathLike:
        return os.path.join(self.root, filename)

    @staticmethod
    def create_base_directory(filename: PathLike) -> PathLike:
        return os.path.join(
            create_dir_if_not_exists(os.path.dirname(filename)),
            os.path.basename(filename)
        )

    def get(self, filename: PathLike) -> None:

        self.logger.info(f"Getting resource {filename} from {self.url}")

        r = requests.get(f"{self.url}/{filename}")

        if r.status_code == 200:
            file_out = self.pathTo(filename)

            with open(self.create_base_directory(file_out), 'wb') as f:
                f.write(r.content)
        else:
            raise FileNotFoundError

    def get_if_not_exists(self, filename: PathLike) -> PathLike:
        file_out = self.pathTo(filename)

        if not os.path.exists(file_out):
            self.get(filename)
        return file_out

    def get_if_not_exists_decorator(self, f: Callable[[PathLike], PathLike]) -> Callable[[PathLike], PathLike]:
        def wrap(filename):
            return f(self.get_if_not_exists(filename))
        return wrap

    def upload(self, filename: PathLike) -> requests.Response:
        with open(self.pathTo(filename), "rb") as fid:
            files = {'file': fid}
            self.logger.info(f"POST REQUEST ON {self.url}/{filename}")
            return requests.post(f"{self.url}/{filename}", files=files)


class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler, WithLogging):
    def do_POST(self) -> None:

        path = self.translate_path(self.path)

        dirname = os.path.dirname(path)

        try:
            os.makedirs(dirname)
        except FileExistsError:
            pass

        form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                             'CONTENT_TYPE':self.headers['Content-Type'],
                             })

        filename = f"{dirname}/{form['file'].filename}" if path.endswith('/') else path
        data = form['file'].file.read()

        self.send_response(201, "Created")
        self.end_headers()

        with open(filename, "wb") as fid:
            fid.write(data)

        self.logger.info("POST Request handled")


if __name__ == '__main__':
    """
    python - m cgnal.utils.cloud - -bind [IP_ADDRESS] [PORT]
    """

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    http.server.test(HandlerClass=HTTPRequestHandler, port=args.port, bind=args.bind)
