import logging

from latex_tools.arguments import parse_args
from latex_tools.file_utils import (
    build_relative_path, calc_file_hash, combine_paths, copy_file, copy_files,
    create_temp_dir, does_file_exist, ensure_path_exist, find_files,
    remove_temp_dir)
from latex_tools.latex import run_latexpand, run_pdflatex


def config_logging(verbose):
    # Set the logging level
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


def clean(input_dir, output_dir, keep):
    # Parse the files to keep
    files_to_keep = keep.split(',')

    # Check whether the files to keep exist
    check_files_to_keep(input_dir, files_to_keep)

    # Find all files in the input directory
    input_files = find_files(input_dir)

    # Build relative paths for all input files
    relative_input_paths = build_relative_input_paths(input_files, input_dir)

    # Expand the files
    expanded_dir_obj, expanded_dir = expand_files(input_dir, input_files)

    # Create a temporary project with expanded files
    project_dir_obj, project_dir = create_temp_project(
        input_files, relative_input_paths)

    # Copy the input files to the temporary project directory
    copy_input_files_to_project(relative_input_paths, input_dir, project_dir)

    # Copy the expanded files to the temporary project directory
    copy_expanded_files_to_project(files_to_keep, expanded_dir, project_dir)

    # Find the dependencies of the files to keep
    project_deps = find_project_dependencies(
        files_to_keep, project_dir, relative_input_paths)

    # Copy the dependency files to the output directory
    copy_dependencies_to_output(project_deps, input_dir, output_dir)

    # Copy the expanded files to the output directory
    copy_expanded_files_to_output(
        project_deps, files_to_keep, expanded_dir, output_dir)

    # Remove the temporary expanded directory
    remove_temp_dir(expanded_dir_obj)

    # Remove the temporary project directory
    remove_temp_dir(project_dir_obj)

    # Log the finish
    logging.info('Check the cleaned project at "{}"'.format(output_dir))


def check_files_to_keep(input_dir, files_to_keep):
    # Check each file
    for file_to_keep in files_to_keep:
        # Build the full path
        full_path = combine_paths(input_dir, file_to_keep)

        # Check whether the file exists
        if not does_file_exist(full_path):
            raise ValueError(('File to keep "{}" does not exist in the input' +
                              ' directory "{}"').format(
                                  file_to_keep, input_dir))


def expand_files(input_dir, input_files):
    # Log the start
    logging.info(
        'Start expanding files in the directory "{}"'.format(input_dir))

    # Initialize the extensions
    # Reference: https://tex.stackexchange.com/a/424669
    extensions = ['tex', 'cls', 'clo', 'sty', 'bst']

    # Initialize the old directory
    old_dir = input_dir

    # Initialize the old directory object
    old_dir_obj = None

    # Find all TEX files in the input directory and set it as old TEX files
    old_tex_files = find_files(input_dir, extensions=extensions)

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
        new_tex_files = find_files(new_dir, extensions=extensions)

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


def create_temp_project(input_files, relative_input_paths):
    # Log the start
    logging.info('Start creating temporary project')

    # Create a temporary directory
    temp_dir_obj, temp_dir = create_temp_dir(name='temp_project')

    # Return the directory object and path
    return temp_dir_obj, temp_dir


def copy_input_files_to_project(relative_input_paths, input_dir, project_dir):
    # Log the start
    logging.info(
        'Start copying files from input directory to temporary project')

    # Copy the files from the input directory to project directory
    copy_files(relative_input_paths, input_dir, project_dir)


def copy_expanded_files_to_project(files_to_keep, expanded_dir, project_dir):
    # Log the start
    logging.info('Start copying files to temporary project')

    # Copy the files from the expanded directory to project directory
    copy_files(files_to_keep, expanded_dir, project_dir)


def find_project_dependencies(
        files_to_keep, project_dir, relative_input_paths):
    # Log the start
    logging.info('Start finding project dependencies')

    # Convert the relative input paths to set
    relative_input_paths = set(relative_input_paths)

    # Initialize the project dependencies
    project_deps = set()

    # Find dependencies for each file to keep
    for file_to_keep in files_to_keep:
        # Build the full path
        full_path = combine_paths(project_dir, file_to_keep)

        # Run pdflatex to read the dependencies
        fls_deps = run_pdflatex(project_dir, full_path)

        # Find the dependencies in the input directory
        deps = fls_deps.intersection(relative_input_paths)

        # Add the dependencies to the project dependencies
        project_deps.update(deps)

    # Return the project dependencies
    return project_deps


def copy_dependencies_to_output(project_deps, input_dir, output_dir):
    # Log the start
    logging.info('Start copying dependency files to output directory')

    # Copy the files from the input directory to output directory
    copy_files(project_deps, input_dir, output_dir)


def copy_expanded_files_to_output(
        project_deps, files_to_keep, expanded_dir, output_dir):
    # Log the start
    logging.info('Start copying expanded files to output directory')

    # Copy the files from the expanded directory to output directory and skip
    # any nonexistent dependency file
    copy_files(project_deps, expanded_dir, output_dir, skip_nonexistent=True)

    # Copy the files from the expanded directory to output directory
    copy_files(files_to_keep, expanded_dir, output_dir)


def build_relative_input_paths(input_files, input_dir):
    # Build relative paths and return
    return [build_relative_path(f, input_dir) for f in input_files]


def calc_files_hashes(files, root_dir):
    # Build relative paths
    relative_paths = [build_relative_path(path, root_dir) for path in files]

    # Calculate file hashes and return
    return {relative_path: calc_file_hash(path)
            for path, relative_path in zip(files, relative_paths)}


def main():
    # Parse the arguments
    args = parse_args()

    # Configure logging
    config_logging(args.verbose)

    # Run the cleaner
    clean(args.input, args.output, args.keep)


if __name__ == '__main__':
    main()
