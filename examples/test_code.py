import time
if __name__ == "__main__":
    with open('aiida.in', 'r') as f:
        string = f.read()

    with open('aiida.out', 'w+') as f:
        f.write('{0}\n{1}'.format(time.time(), string))
