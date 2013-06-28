from handleemail import *

if __name__ == '__main__':
    lines = sys.stdin.readlines()
    handler = EmailHandler()
    answer = handler.handle(lines)
    answer.send_back()