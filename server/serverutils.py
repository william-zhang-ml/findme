"""
Server utilities for number crunching.
"""
__author__ = 'William Zhang'

from pathlib import Path
from typing import List
import numpy as np
import onnxruntime as ort


CURR_DIR = Path(__file__).parent

# Ordered object categories supported by classifier
with open(CURR_DIR / 'cifar-lut.txt', 'r', encoding='utf-8') as file:
    CATEGORIES = [line.strip() for line in file.readlines()]


class OnnxEngine:
    """Wrapper class for using onnxruntime.InferenceSession. """
    def __init__(self, path: str) -> None:
        self.session = ort.InferenceSession(path)

    def __call__(self, *args: np.ndarray) -> List[np.ndarray]:
        outputs = self.session.run(
            self.output_names,
            {name: arg for name, arg in zip(self.input_names, args)}
        )
        return outputs

    @property
    def num_inputs(self) -> int:
        """ Number of input tensors. """
        return len(self.session.get_inputs())

    @property
    def num_outputs(self) -> int:
        """ Number of output tensors. """
        return len(self.session.get_outputs())

    @property
    def input_names(self) -> List[str]:
        """ Names of graph input nodes. """
        return [elem.name for elem in self.session.get_inputs()]

    @property
    def output_names(self) -> List[str]:
        """ Names of graph output nodes. """
        return [elem.name for elem in self.session.get_outputs()]


# Inference engine used for scoring
ENGINE = OnnxEngine(CURR_DIR / 'resnet18.onnx')


def score_image(img: np.ndarray, label: int = 0) -> int:
    """Score an image

    Args:
        img (np.ndarray): image to score
        label (int): object category index

    Returns:
        float: score
    """
    img = np.expand_dims(img, 0)  # add batch dim
    logits = ENGINE(img)[0][0]    # first output, first sample
    conf = np.exp(logits)
    conf = conf / np.sum(conf)
    return int(100 * conf[label])
