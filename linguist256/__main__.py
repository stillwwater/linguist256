"""
Linguist256 is designed to produce a similar output to GitHub Linguist*
within a terminal window, provided the terminal has `xterm` 8bit color support.

* https://github.com/github/linguist
"""

import os
import time
import glob
import yaml
import argparse
import random

from threading import Thread
from linguist256 import convert

RESET = '\33[0m'


def __center(width: int):
    """return centered version of text"""
    return ' ' * int(args.width / 2 - width / 2)


def __inc_dict(src: dict, key: str, increment: int):
    if key in src:
        src[key] += increment
        return
    src[key] = increment


def color(lang: str):
    """return language 8bit color"""
    if 'color' not in data[lang]:
        color = random.randint(17, 230)
    else:
        color = data[lang]['color']

    if isinstance(color, str):
        color = convert.to8bit(color)

    return '\33[48;5;%im' % color


def print_header():
    """display a header with the repository's name"""
    head_width = len(args.name) + 4
    print('\n%s' % __center(head_width), '=' * head_width)
    print('%s   %s  ' % (__center(head_width), args.name))
    print('%s' % __center(head_width), '=' * head_width)


def get_extension_size(path: str):
    ext = '.' + '.'.join(os.path.basename(path).split('.')[1:])
    size = os.stat(path).st_size
    return ext, size


def map_files(path: str, size_map: dict):
    for f in glob.glob(path.strip() + '/**/*', recursive=True):
        if not os.path.isfile(f):
            continue

        ext, size = get_extension_size(f)
        __inc_dict(size_map, ext, size)


def map_extension_sizes():
    """map files in repository by their file extension"""
    size_map = {}
    threads = []

    for path in args.paths.split(','):
        for subdir in os.listdir(path):
            real_path = os.path.join(path, subdir)

            if os.path.isfile(real_path):
                ext, size = get_extension_size(real_path)
                __inc_dict(size_map, ext, size)
                continue

            # handle each immediate subdirectory in a separate thread
            t = Thread(target=map_files, args=(real_path, size_map))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    return size_map


def count_size(lang: str, size_map: dict):
    size = 0

    for ext in data[lang]['extensions']:
        if 'all' not in args.types and data[lang]['type'] not in args.types:
            continue
        if ext in size_map:
            size += size_map[ext]

    return size


def map_languages(size_map: dict):
    total = 0
    results = []

    for lang in data:
        if 'extensions' not in data[lang]:
            continue

        size = count_size(lang, size_map)

        if size > 0:
            results.append((lang, size))
            total += size

    return (results, total)


def render(results: list):
    """render results"""
    legend = ''
    plot = ''

    # used to offset legend centering by the amount of non-printed characters
    legend_null_width = 0

    # render plot
    for r in results:
        # character width of bar
        char_width = int(r[1] / total * args.width)

        if char_width < 1:
            # language has width of less than one character on plot
            continue

        legend_color = color(r[0])
        legend_null_width += len(legend_color) + len(RESET) * 4
        legend += '  %s  %s %s: %.2f%%' % (legend_color, RESET, r[0], r[1] / total * 100)

        plot += legend_color
        plot += ' ' * char_width

    legend_offset = len(legend) - legend_null_width / 2
    return '%s%s\n\n%s%s\n' % (__center(legend_offset), legend, plot, RESET)


# get arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('paths')
argparser.add_argument(
    '-w', '--width', help='column width of plot [default: 80]', type=int)
argparser.add_argument(
    '-n', '--name', help='show a header title')
argparser.add_argument(
    '-t', '--types', help='language types, comma separated [default: "programming"]')
argparser.add_argument(
    '-b', '--benchmark', help='time process', action='store_true')
args = argparser.parse_args()

args.width = 80 if args.width is None else args.width
args.types = ['programming'] if args.types is None else args.types.split(',')

wd = os.path.realpath(os.path.dirname(__file__))

# find languages.yml
for f in ['languages.yml', 'langauges.yaml', os.path.join(wd, 'languages.yml')]:
    if os.path.isfile(f):
        data_file = f
        break

if data_file is None:
    print('Err: Missing languages.yml')
    exit(-1)

# load languages file
with open(data_file, 'r') as f:
    data = yaml.load(f.read())

# print a header
if args.name is not None:
    print_header()

start = int(round(time.time() * 1000))
results, total = map_languages(map_extension_sizes())

print()

# sort biggest to smallest
results.sort(key=lambda x: x[1], reverse=True)

# render results
print(render(results))

if args.benchmark:
    print('Process completed in %ims' % int(round(time.time() * 1000) - start))
