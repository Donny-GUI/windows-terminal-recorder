import argparse


def get_parser():
    parser = argparse.ArgumentParser(usage="termrec [options]", prog="termrec", description="Record current terminal")
    parser.add_argument("-o", "--output-file", type=str, default="output.gif", help="Output file")
    parser.add_argument("-f", "--fps", type=int, default=12, help="Frames per second")
    parser.add_argument("-r", "--reduce-percent", type=int, default=20, help="Reduce size of output by percent")
    parser.add_argument("-c", "--countdown-seconds", type=int, default=5, help="Countdown before starting recording")

    return parser
