import logging

from latex_tools.arguments import parse_args
from latex_tools.cli import run_command
from latex_tools.file_utils import (
    build_relative_path, calc_file_hash, combine_paths, copy_file,
    create_temp_dir, does_file_exist, ensure_path_exist, find_files,
    remove_temp_dir)


def config_logging(verbose):
    # Set the logging level
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def clean(input_dir, output_dir, keep):
    # Expand the files
    expanded_dir_obj, expanded_dir = expand_files(input_dir)

    # Copy the files to keep
    copy_files_to_keep(output_dir, keep, expanded_dir)

    # Remove the temporary expanded directory
    remove_temp_dir(expanded_dir_obj)


def expand_files(input_dir):
    # Log the start
    logging.info(
        'Start expanding files in the directory "{}"'.format(input_dir))

    # Initialize the old directory
    old_dir = input_dir

    # Initialize the old directory object
    old_dir_obj = None

    # Find all TEX files in the old directory
    old_tex_files = find_files(old_dir, extension='tex')

    # Calculate hashes of all old TEX files
    old_hashes = calc_files_hashes(old_tex_files, old_dir)

    # Keep expanding files until the file contents have no changes
    has_changes = True
    round_idx = 0

    while has_changes:
        # Run latexpand and produce new TEX files in the new temporary
        # directory
        new_dir_obj, new_dir = run_latexpand(old_dir, old_tex_files)

        # Log the new directory
        logging.info(('Round #{}: Use latexpand to produce new TEX files to' +
                      ' directory "{}"').format(round_idx, new_dir))

        # Find all TEX files in the new directory
        new_tex_files = find_files(new_dir, extension='tex')

        # Calculate hashes of all new TEX files
        new_hashes = calc_files_hashes(new_tex_files, new_dir)

        # Check whether the old and new hashes are the same
        has_changes = (old_hashes != new_hashes)

        # Remove the old directory if it's temporary directory
        if old_dir_obj is not None:
            remove_temp_dir(old_dir_obj)

        # Update the old states
        old_dir = new_dir
        old_dir_obj = new_dir_obj
        old_tex_files = new_tex_files
        old_hashes = new_hashes

        # Increment the round index
        round_idx += 1

    # Return the final directory object and path
    return new_dir_obj, new_dir


def copy_files_to_keep(output_dir, keep, expanded_dir):
    # Log the start
    logging.info('Start copying files to keep to the directory "{}"'.format(
        output_dir))

    # Parse the files to keep
    files_to_keep = keep.split(',')

    # Copy each file to output directory
    for file_to_keep in files_to_keep:
        # Build the source path
        src_path = combine_paths(expanded_dir, file_to_keep)

        # Build the destination path
        dst_path = combine_paths(output_dir, file_to_keep)

        # Check whether the file exists
        if not does_file_exist(src_path):
            raise ValueError(
                ('File "{}" does not exist in the final expanded directory' +
                 ' "{}"').format(file_to_keep, expanded_dir))

        # Ensure the destination directory exists
        ensure_path_exist(dst_path)

        # Log the destination path
        logging.info('Copy the file to "{}"'.format(dst_path))

        # Copy the file from expanded directory to output directory
        copy_file(src_path, dst_path)


def calc_files_hashes(files, root_dir):
    # Build relative paths
    relative_paths = [build_relative_path(path, root_dir) for path in files]

    # Calculate file hashes and return
    return {relative_path: calc_file_hash(path)
            for path, relative_path in zip(files, relative_paths)}


def run_latexpand(old_dir, old_tex_files):
    # Create a temporary directory
    temp_dir_obj, temp_dir = create_temp_dir(name='latexpand_output')

    # Process each TEX file
    for tex_file in old_tex_files:
        # Build the relative path
        relative_path = build_relative_path(tex_file, old_dir)

        # Build the output path
        output_path = combine_paths(temp_dir, relative_path)

        # Ensure the output directory exists
        ensure_path_exist(output_path)

        # Build the command to run latexpand
        command = build_latexpand_command(output_path, relative_path)

        # Run the command
        stdout, stderr, return_code = run_command(command, cwd=old_dir)

        # Check return code and STDERR
        if return_code != 0 or len(stderr) > 0:
            raise ValueError(('Failed to run the command "{}"\n' +
                              'Return code: {}\n' +
                              'STDOUT->\n{}\n' +
                              'STDERR->\n{}').format(
                                  command, return_code, stdout, stderr))

    # Return the temporary directory object and path
    return temp_dir_obj, temp_dir


def build_latexpand_command(output_path, input_path):
    # Build the command and return
    return ' '.join([
        'latexpand',
        '--output="{}"'.format(output_path),
        '--out-encoding="{}"'.format('encoding(UTF-8)'),
        '"{}"'.format(input_path),
    ])


def main():
    # Parse the arguments
    args = parse_args()

    # Configure logging
    config_logging(args.verbose)

    # Run the cleaner
    clean(args.input, args.output, args.keep)


if __name__ == '__main__':
    main()
