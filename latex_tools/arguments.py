import argparse


def parse_args():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description='Clean project for submitting on arXiv')

    # Directories
    parser.add_argument('--input', type=str, required=True,
                        help='Input directory')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory')
    # Paths
    parser.add_argument('--keep', type=str, required=True,
                        help=('TEX Files to keep (Comma-sepearted paths,' +
                              ' relative to input directory)'))
    # Logging
    parser.add_argument('--verbose', action='store_true',
                        help='Turns on verbose logging')

    # Parse the arguments
    args = parser.parse_args()

    # Return the arguments
    return args
