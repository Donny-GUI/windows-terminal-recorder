import termrec 
import sys

def main():
    parser = termrec.get_parser()
    args = parser.parse_args()

    if "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
        parser.print_help()
        sys.exit(0)

    termrec.record_current_terminal(args.output_file, args.fps, args.reduce_percent, args.countdown_seconds)


if __name__ == "__main__":
    termrec.freeze_support()
    main()
