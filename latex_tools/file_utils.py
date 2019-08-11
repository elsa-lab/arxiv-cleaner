from pathlib import Path
import hashlib
import logging
import shutil
import tempfile


def build_relative_path(path, relative_to_path):
    # Build the path object
    path_obj = Path(path)

    # Find the relative path
    relative_path_obj = path_obj.relative_to(relative_to_path)

    # Return the relative path
    return relative_path_obj.as_posix()


def calc_file_hash(path):
    """
    References:
    https://www.pythoncentral.io/hashing-files-with-python/
    https://stackoverflow.com/a/1131255
    """
    # Set the block size
    block_size = 2 ** 15

    # Build a hasher
    hasher = hashlib.md5()

    # Open the file in binary mode
    with open(path, 'rb') as fp:
        while True:
            # Read a segment
            buf = fp.read(block_size)

            # Check whether there are no contents any more
            if not buf:
                break

            # Update the hasher with the segment
            hasher.update(buf)

    # Return the hash
    return hasher.hexdigest()


def combine_paths(*paths):
    # Build the path object
    path_obj = Path(*paths)

    # Return the path
    return path_obj.as_posix()


def convert_paths_to_unix_style(paths):
    return [Path(path).as_posix() for path in paths]


def copy_file(src, dst):
    shutil.copyfile(src, dst)


def create_temp_dir(name=''):
    # Build the suffix
    suffix = '.{}'.format(name)

    # Create a temporary directory
    try:
        dir_obj = tempfile.TemporaryDirectory(
            prefix='latex_tools.', suffix=suffix)
    except:
        raise ValueError('Failed to create temporary directory')

    # Get the path of the temporary directory
    path = Path(dir_obj.name).as_posix()

    # Return the directory object
    return dir_obj, path


def create_temp_file(name=''):
    # Build the suffix
    suffix = '.{}'.format(name)

    # Create a temporary file
    try:
        # Create a named temporary file
        fp = tempfile.NamedTemporaryFile(
            delete=False, prefix='latex_tools.', suffix=suffix)
    except:
        raise ValueError('Failed to create temporary file')

    # Get the path of the temporary file
    path = Path(fp.name).as_posix()

    # Return the temporary file pointer and path
    return fp, path


def does_file_exist(path):
    # Build the path object
    path_obj = Path(path)

    # Check whether the file exists
    return path_obj.exists()


def ensure_path_exist(path):
    # Build the path object
    path_obj = Path(path)

    # Find the parent directory
    parent_obj = path_obj.parent

    # Make sure the parent directory exists
    parent_obj.mkdir(exist_ok=True)


def find_files(path, extension=None, recursive=True):
    # Build the path object
    path_obj = Path(path)

    # Build the extension pattern
    if extension is None:
        extension_pattern = '*'
    else:
        extension_pattern = '*.{}'.format(extension)

    # Build the pattern
    pattern = '**/{}'.format(extension_pattern)

    # Find all files
    found_files = path_obj.glob(pattern)

    # Convert paths to Unix style
    return convert_paths_to_unix_style(found_files)


def remove_temp_dir(dir_obj):
    dir_obj.cleanup()


def remove_temp_file(fp):
    # Get the path of the temporary file
    path = Path(fp.name).as_posix()

    # Close the file pointer
    fp.close()

    # Try to delete the temporary file
    try:
        Path.unlink(path)
    except:
        logging.warning(
            'Failed to delete the temporary file "{}"'.format(path))
