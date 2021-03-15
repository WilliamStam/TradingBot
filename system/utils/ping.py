import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import traceback  


def ping(host:str,timeout=5) -> bool:
    cmd = "ping -{} 1 {} {}".format('c', f'-W {timeout}', host )
    if platform.system().lower() == "windows":
        cmd = "ping -{} 1 {} {}".format('n' , f'-w {timeout}000' , host )
    try:
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True,close_fds=True, timeout=timeout)
        if 'unreachable' in output:
            return False
        else:
            return True
    except Exception as e:
        if 'returned non-zero exit status 1' in str(e):
            return False
    
        return False
