import argparse
import logging

import colorlog

from fnac_prices import settings
from fnac_prices.classes.fnac import ManagedApp


def __make_logger(level=logging.DEBUG):
    log_format = ("%(asctime)s %(log_color)s%(levelname)-8s"
                  "%(reset)s %(white)s%(message)s")
    date_format = "%Y-%m-%d %H:%M:%S"
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        log_format, datefmt=date_format, reset=True))

    logger = colorlog.getLogger()
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger


def run_engine(email: str, password: str, input_path=None, log_level=logging.DEBUG):
    logger = __make_logger(log_level)
    logger.info("Running {}-{}".format(settings.BASE_VERSION, settings.BASE_CODENAME))
    app = ManagedApp(email, password, input_path, logger)
    app.run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--email", required=True, help="FNAC user email")
    ap.add_argument("-p", "--password", required=True,
                    help="FNAC user password (cleartext)")
    ap.add_argument("-i", "--input", required=False,
                    help="FNAC input inventory")
    ap.add_argument("-d", "--debug", dest="log_level", action="store_const",
                    const=logging.DEBUG, default=logging.INFO,
                    help="Show debug log messages")
    args = ap.parse_args()
    run_engine(args.email, args.password, args.input, args.log_level)
