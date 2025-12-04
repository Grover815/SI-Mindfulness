import logging
import multiprocessing

def setup_logger():

	logger  = multiprocessing.get_logger()
	logger.setLevel(logging.INFO)
	handler1 = logging.FileHandler(f'logs/info.log')
	handler2 = logging.StreamHandler()
	handler1.setFormatter(logging.Formatter("%(levelname)s: %(asctime)s - %(process)s - %(message)s"))

	if not len(logger.handlers): 
		logger.addHandler(handler1)
		logger.addHandler(handler2)

	return logger
