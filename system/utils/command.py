import shlex
import subprocess  # For executing a shell command`


def command(command):

    process = subprocess.Popen(shlex.split(command),stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(output.strip().decode("utf-8"))
    rc = process.poll()
    process.stdout.close()
    return rc