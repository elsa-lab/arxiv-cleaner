import re

from latex_tools.cli import run_command, check_command_results
from latex_tools.file_utils import (
    build_relative_path, change_extension, combine_paths, create_temp_dir,
    ensure_path_exist)


def run_latexpand(root_dir, tex_files):
    # Create a temporary directory
    temp_dir_obj, temp_dir = create_temp_dir(name='latexpand_output')

    # Process each TEX file
    for tex_file in tex_files:
        # Build the relative path
        relative_path = build_relative_path(tex_file, root_dir)

        # Build the output path
        output_path = combine_paths(temp_dir, relative_path)

        # Ensure the output directory exists
        ensure_path_exist(output_path)

        # Build the command to run latexpand
        command = build_latexpand_command(output_path, relative_path)

        # Run the command
        return_code, stdout, stderr = run_command(command, cwd=root_dir)

        # Check return code and STDERR
        check_command_results(command, return_code, stdout, stderr)

    # Return the temporary directory object and path
    return temp_dir_obj, temp_dir


def run_pdflatex(root_dir, tex_file):
    # Build the command to run pdflatex
    command = build_pdflatex_command(tex_file)

    # Run the command
    return_code, stdout, stderr = run_command(
        command, stdout=None, stderr=None, cwd=root_dir)

    # Check return code and STDERR
    check_command_results(command, return_code, stdout, stderr)

    # Build the path to FLS file
    fls_path = change_extension(tex_file, '.fls')

    # Read the FLS file to get all dependencies and return
    return read_fls_dependencies(fls_path)


def read_fls_dependencies(fls_path):
    # Read all lines in the FLS file
    with open(fls_path) as fp:
        lines = fp.readlines()

    # Initialize the dependencies
    deps = set()

    # Initialize the pattern
    pattern = re.compile(r'INPUT\s+(?P<path>.+)\n')

    # Check input paths for each line
    for line in lines:
        # Find the full match
        match = pattern.fullmatch(line)

        # Check if there is a match
        if match:
            # Get the input path
            input_path = match.group('path')

            # Add the input path to the set
            deps.add(input_path)

    # Return the dependencies
    return deps


def build_latexpand_command(output_path, input_path):
    # Build the command and return
    return ' '.join([
        'latexpand',
        '--output="{}"'.format(output_path),
        '--out-encoding="{}"'.format('encoding(UTF-8)'),
        '"{}"'.format(input_path),
    ])


def build_pdflatex_command(tex_file):
    # Build the command and return
    return ' '.join([
        'pdflatex',
        '-interaction=nonstopmode',
        '-recorder',
        '"{}"'.format(tex_file),
    ])
