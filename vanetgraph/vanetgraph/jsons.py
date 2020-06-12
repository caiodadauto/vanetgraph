import os

import graph_tool as gt
from tqdm import tqdm
from pathlib import Path

from .utils.constructor import get_metrics


class JsonData:
    def __init__(self, path):
        self.labels_translate= {}
        self.load_path = path
        self.save_path = path.parent.joinpath("metric_jsons")
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)

    def create_jsons_from_graphs(self, metrics):
        translated_labels = []
        graph_paths = sorted(self.load_path.glob("*.gt.xz"), key=lambda x: int(x.stem.split(".")[0]))
        for i in tqdm(range(len(graph_paths))):
            p = graph_paths[i]
            G = gt.load_graph(str(p))

            labels = G.vp.label.get_2d_array([0]).tolist()[0]
            # TODO: delete duplicates keeping order.
            # x = G.vp.pos.get_2d_array([0]).tolist()[0]
            # y = G.vp.pos.get_2d_array([1]).tolist()[0]
            # set_labels = set(labels)
            # x = G.vp.pos.get_2d_array([0]).tolist()[0]
            # y = G.vp.pos.get_2d_array([1]).tolist()[0]
            # non_duplicate_labels = [ l for l, xx, yy in zip(l, x, y) if l

            for l, xx, yy in zip(labels, x, y):
                if not l in self.labels_translate.keys():
                    self.labels_translate[l] = len(self.labels_translate)
                translated_labels.append(self.labels_translate[l])
            if len(translated_labels) != len(set(translated_labels)):
                print("There is label duplication!!!")
                exit(1)
            get_metrics(G, G.num_vertices(), G.num_edges(), int(p.stem.split(".")[0]), str(self.save_path), metrics, translated_labels)
        with open(self.save_path.parent.joinpath("labels_translate.json"), "w") as f:
            json.dump(self.labels_translate, f)
        return sorted(self.save_path.glob("*.json"), key=lambda x: int(x.stem))
