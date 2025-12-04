
def writeMessage(message):
	with open('/home/lemmondpi/Documents/html/index.html', 'w') as file:
	    file.write(f'<html><body><h1>{message}</h1></body></html>')

writeMessage("Hello ")