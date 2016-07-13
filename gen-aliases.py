# author: gergely.nyiri@gmail.com

import os
import getopt
import sys
import logging, logging.handlers
import re


def create_logger():
    """
    Create logger instance
    :return: logger instance
    """
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


class AliasCandidate(object):
    """
    Class representing a candidate for alias during a directory scan
    """
    def __init__(self, name, path, num_directories, level):
        """
        :param name: name of the alias
        :param path:  path of the alias
        :param num_directories: number of directories
        :param level: level of directory from the root
        """
        self._name = name
        self._path = path
        self._num_directories = num_directories
        self._level = level

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def num_directories(self):
        return self._num_directories

    @property
    def level(self):
        return self._level

    def __str__(self):
        return "alias " + self.name + "=\"cd " + self.path + "\"\n"



logger = create_logger()


def print_help():
    print('Usage: gen-aliases.py -d <directory> | --directory=<directory>')
    sys.exit(-1)


def gen_aliases(root_directory, candidates, level):
    """
    Generate aliases from root_directory
    :param root_directory: directory to start the traversing from
    :param candidates: set of aliases found so far
    :param level: level of recursion
    :return: None
    """

    num_directories = len([file_name for file_name in os.listdir(root_directory) if
                    os.path.isdir(os.path.join(root_directory, file_name))])

    candidates.append(AliasCandidate(os.path.basename(root_directory), root_directory, num_directories, level))

    logger.debug("%s (%s, %d, %d)", os.path.basename(root_directory), root_directory, num_directories, level)

    for file_name in os.listdir(root_directory):
        file_path = os.path.join(root_directory, file_name)
        if os.path.isdir(file_path):
            gen_aliases(file_path, candidates, level + 1)


def write_aliases(output_file, candidates, preferred):
    candidate_counter = dict()
    regex = r'%s' % preferred

    for candidate in candidates:
        if candidate.name in candidate_counter.keys():
            candidate_counter[candidate.name] += 1
        else:
            candidate_counter[candidate.name] = 1

    for candidate in candidates:
        if candidate.name:
            if candidate.name[0] == ".":
                continue
            if candidate.name and (candidate_counter[candidate.name] == 1):
                output_file.write(str(candidate))
            else:
                ambiguous_candidates = [(c.name, c.path) for c in candidates if c.name == candidate.name]
                logger.warning("path %s is ambiguous (%d directories of the same name)", candidate.name, candidate_counter[candidate.name])
                for amb in ambiguous_candidates:
                    if amb[0]:
                        if re.match(regex, amb[1], re.M | re.I):
                            output_file.write(str(candidate))
                            logger.warning("--> %s will be taken", amb[1])
                            break


def main(argv):
    logger.debug("Start")

    directory = "."
    preferred = "."

    try:
        opts, args = getopt.getopt(argv[1:], "d:p:", ["directory=", "preferred="])
    except getopt.GetoptError:
        print_help()
    for opt, arg in opts:
        if opt == "-h":
            print_help()
        elif opt in ("-d", "--directory"):
            directory = arg
        elif opt in ("-p", "--preferred"):
            preferred = arg
        else:
            print_help()

    output_file = open("aliases.sh", "w")
    candidates = list()
    gen_aliases(directory, candidates, 1)
    write_aliases(output_file, candidates, preferred)


if __name__ == '__main__':
    main(sys.argv)
