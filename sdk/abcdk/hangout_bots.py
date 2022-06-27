#https://hangouts.google.com/group/d7viKWWW2ypkEF8P8
#~ eseYDDdMmuKYZfDi7
#~ https://hangouts.google.com/group/FYPZMb9857wZfYrZ8
#~ https://hangouts.google.com/group/FYPZMb9857wZfYrZ8

from httplib2 import Http
from json import dumps

#
# Hangouts Chat incoming webhook quickstart
#
def main():
    url = 'https://hangouts.google.com/group/FYPZMb9857wZfYrZ8'
    bot_message = {
        'text' : 'Hello from Python script!'}

    message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = Http()

    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )

    print(response)

if __name__ == '__main__':
    main()
