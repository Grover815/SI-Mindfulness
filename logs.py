import logging
import multiprocessing

def setup_logger():

	logger  = multiprocessing.get_logger()
	logger.setLevel(logging.INFO)
	handler = logging.FileHandler(f'logs/info.log')
	handler.setFormatter(logging.Formatter("%(levelname)s: %(asctime)s - %(process)s - %(message)s"))

	if not len(logger.handlers): 
		logger.addHandler(handler)

	return logger
