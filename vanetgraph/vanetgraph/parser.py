import os
import logging
from time import time as get_time
import logging.handlers as handlers
from multiprocessing import cpu_count

import numpy as np
import graph_tool as gt

from .utils.constructor import create_graph


def raw_graph_generator(raw_file_path, last_read_time):
    with open(raw_file_path, "r") as f:
        pos = []
        speed = []
        label = []
        last_time = np.inf
        for line in f:
            time = int(line.split(" ")[0].rstrip())
            if time > last_read_time:
                l = line.split(" ")[1].rstrip()
                x = line.split(" ")[2].rstrip()
                y = line.split(" ")[3].rstrip()
                s = line.split(" ")[4].rstrip()
                label.append(l)
                pos.append([x, y])
                speed.append(s)
                if last_time < time:
                    graph_time = last_time
                    pos_arr = np.array(pos[:-1], dtype='f4')
                    speed_arr = np.array(speed[:-1], dtype='f4')
                    label_out = label[:-1].copy()
                    pos = [pos[-1]]
                    speed = [speed[-1]]
                    label = [label[-1]]
                    last_time = time
                    yield graph_time, label_out, pos_arr, speed_arr
                last_time = time
    if(len(pos) > 0):
        graph_time = last_time
        pos_arr = np.array(pos, dtype='f4')
        speed_arr = np.array(speed, dtype='f4')
        label_out = label.copy()
        last_time = time
        yield graph_time, label_out, pos_arr, speed_arr

def parser( raw_file_path, n_proc=None, last_read_time=-1, graph_root="graphs/", transmission_range=200.0, metrics=["d", "dc", "pgr"] ):
    formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
    file_logger = logging.getLogger( 'Logger' )
    file_logger.setLevel( logging.DEBUG )
    file_handler = handlers.RotatingFileHandler( 'parser.log', maxBytes=200 * 1024 * 1024, backupCount=1 )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_logger.addHandler(file_handler)

    if not os.path.isdir(graph_root):
        os.makedirs(graph_root)

    n_proc = cpu_count() if not n_proc else n_proc
    graph_lines_generator = raw_graph_generator(raw_file_path, last_read_time)
    for time, label, pos, speed in graph_lines_generator:
        start = get_time();
        create_graph(pos, speed, label, metrics, n_proc, transmission_range, graph_root, time)
        file_logger.info("Processed Graph: size - {}, time - {}, duration - {:.4f}".format( len(label), time, get_time() - start))
