"""
Serverside implementation.
- assigns quests to users
- scores user submissions
- tracks user scores
"""

__author__ = 'William Zhang'

from typing import Dict, Tuple
from fastapi import FastAPI
import numpy as np
from PIL import Image
from pydantic import BaseModel
from . import serverutils


app = FastAPI()


# Poor man's user "database"
USER_DATA = {
    'total_score': 0,
    'has_quest': 0,
    'quest_idx': -1,
    'quest_str': ''
}


class RawImage(BaseModel):
    """Expected image format to receive from client devices. """
    mode: str              # ex: RGB
    size: Tuple[int, int]  # width x height
    data: str


@app.get('/user/')
async def get_user_data() -> Dict:
    """Get user data for mobile client display.

    Returns:
        Dict: user data
    """
    return USER_DATA


@app.get('/newquest/')
async def get_new_quest() -> Dict:
    """Update user data with a new quest.

    Returns:
        Dict: user data
    """
    if USER_DATA['quest_idx'] == -1:
        quest_idx, quest_str = serverutils.name_random()
        USER_DATA['quest_idx'] = quest_idx
        USER_DATA['quest_str'] = quest_str
    return USER_DATA


@app.post('/score/')
async def score(raw: RawImage) -> Dict[str, int]:
    """Score an image (for plumbing checks).

    Args:
        raw (RawImage): hex-encoded flattened image

    Returns:
        Dict[str, int]: image score
    """
    result = {'score': float('nan')}

    # preprocess image for inference engine
    data = bytes.fromhex(raw.data)  # undo client conversion to hex/str
    img = Image.frombytes(raw.mode, raw.size, data)
    img = np.array(img)
    img = np.transpose(img, [2, 0, 1])
    img = img.astype(np.float32) / 255

    # inference
    result['score'] = serverutils.score_image(img)

    return result
