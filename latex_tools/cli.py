import logging
import subprocess


def run_command(command, cwd=None):
    try:
        # Run the command
        p_obj = subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, shell=True, cwd=cwd)

        # Wait the process to finish
        p_obj.wait()

        # Read return code
        return_code = p_obj.returncode

        # Read stdout and stderr
        stdout, stderr = p_obj.communicate()

        # Decode the stdout and stderr
        stdout = decode_output(stdout)
        stderr = decode_output(stderr)

        # Return the raw results and return code
        return stdout, stderr, return_code
    except subprocess.CalledProcessError as e:
        message = ('Could not run the command "{}"'.format(command) +
                   'RETURN_CODE: {}'.format(e.returncode) +
                   'STDOUT=>\n{}'.format(decode_output(e.stdout)) +
                   'STDERR=>\n{}'.format(decode_output(e.stderr)))
        raise ValueError(message)
    except:
        raise ValueError('Unknown error occurred')


def decode_output(output):
    try:
        return output.decode('utf-8')
    except UnicodeDecodeError:
        return output
