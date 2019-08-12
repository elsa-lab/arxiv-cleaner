import re
import subprocess

from latex_tools.cli import run_command, check_command_results
from latex_tools.file_utils import (
    build_relative_path, change_extension, combine_paths, create_temp_dir,
    ensure_path_exist)


class LatexRunner:
    def __init__(self, latex_compiler, latex_extra_args='',
                 latexpand_extra_args=''):
        # Save the arguments
        self.latex_compiler = latex_compiler
        self.latex_extra_args = latex_extra_args
        self.latexpand_extra_args = latexpand_extra_args

    def run_latexpand(self, root_dir, tex_files):
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
            command = self._build_latexpand_command(output_path, relative_path)

            # Run the command
            return_code, stdout, stderr = run_command(command, cwd=root_dir)

            # Check return code and STDERR
            check_command_results(command, return_code, stdout, stderr)

        # Return the temporary directory object and path
        return temp_dir_obj, temp_dir

    def run_pdflatex(self, root_dir, tex_file):
        # Build the command to run pdflatex
        command = self._build_pdflatex_command(tex_file)

        # Run the command
        return_code, stdout, stderr = run_command(
            command, stdout=subprocess.DEVNULL, stderr=None, cwd=root_dir)

        # Check return code and STDERR
        check_command_results(command, return_code, stdout, stderr)

        # Build the path to FLS file
        fls_path = change_extension(tex_file, '.fls')

        # Read the FLS file to get all dependencies and return
        return self._read_fls_dependencies(fls_path)

    def _read_fls_dependencies(self, fls_path):
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

    def _build_latexpand_command(self, output_path, input_path):
        # Build the command and return
        return ' '.join([
            'latexpand',
            '--output="{}"'.format(output_path),
            '--out-encoding="{}"'.format('encoding(UTF-8)'),
            self.latexpand_extra_args,
            '"{}"'.format(input_path),
        ])

    def _build_pdflatex_command(self, tex_file):
        # Build the command and return
        return ' '.join([
            self.latex_compiler,
            '-interaction=nonstopmode',
            '-recorder',
            self.latex_extra_args,
            '"{}"'.format(tex_file),
        ])
