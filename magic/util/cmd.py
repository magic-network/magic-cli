import subprocess


# Send a command to the shell and return the result
# TODO: Windows support
def cmd(command, sudo=False, arg=None):
    if sudo:
        command = "sudo -S %s" % command
    process = subprocess.Popen(
        command, shell=True,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    stdoutdata, stderrdata = process.communicate(arg)

    return type('obj', (object,), {
        'stdout': stdoutdata.decode(),
        'returncode': process.returncode
    })