from logging import basicConfig, INFO, DEBUG, debug

def configure_logging(level):
  if not level:
    level = INFO
  else:
    level = DEBUG
  basicConfig(
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=level)

