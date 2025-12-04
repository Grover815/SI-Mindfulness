import configparser

def cfg(group,value):
	config = configparser.ConfigParser()
	config.read('config.ini')

	return config.get(group,value)