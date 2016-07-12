import os
import getopt
import sys
import logging, logging.handlers


def create_logger():
    _logger = logging.getLogger('gen-aliases')
    file_handler = logging.FileHandler('log.txt')
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    _logger.addHandler(stream_handler)
    _logger.setLevel(logging.DEBUG)
    return _logger


logger = create_logger()


def print_help():
    print('Usage: gen-aliases.py -d <directory> | --directory=<directory>')
    sys.exit(-1)


def gen_aliases(root_directory, alias_set, level):
    # logger.info("Generate aliases from %s", root_directory)

    num_dirs = len([file_name for file_name in os.listdir(root_directory) if
                    os.path.isdir(os.path.join(root_directory, file_name))])

    alias_set.add((os.path.basename(root_directory), root_directory, num_dirs, level))

    logger.debug("%s (%s, %d, %d)", os.path.basename(root_directory), root_directory, num_dirs, level)

    for file_name in os.listdir(root_directory):
        file_path = os.path.join(root_directory, file_name)
        if os.path.isdir(file_path):
            gen_aliases(file_path, alias_set, level + 1)


def write_aliases(alias_file, alias_set):
    for elem in alias_set:
        if elem[0]:
            alias_file.write("alias " + elem[0] + "=\"cd " + elem[1] + "\"\n")


def main(argv):
    logger.debug("Start")

    directory = "."

    try:
        opts, args = getopt.getopt(argv[1:], "d:", ["directory="])
    except getopt.GetoptError:
        print_help()
    for opt, arg in opts:
        if opt == "-h":
            print_help()
        elif opt in ("-d", "--directory"):
            directory = arg
        else:
            print_help()

    alias_file = open("aliases.sh", "w")
    alias_set = set()
    gen_aliases(directory, alias_set, 1)
    write_aliases(alias_file, alias_set)


if __name__ == '__main__':
    main(sys.argv)
