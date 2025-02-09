"""
Serverside implementation.
- assigns quests to users
- scores user submissions
- tracks user scores
"""

__author__ = 'William Zhang'

from typing import Tuple
from fastapi import FastAPI
import numpy as np
from PIL import Image
from pydantic import BaseModel
from . import serverutils


app = FastAPI()


class UserData(BaseModel):
    """Model for user data. """
    total_score: int = 0
    has_quest: bool = False
    quest_idx: int = -1
    quest_cat: str = ''


# Poor man's user "database"
USER_DATA = UserData()


class RawImage(BaseModel):
    """Expected image format to receive from client devices. """
    mode: str              # ex: RGB
    size: Tuple[int, int]  # width x height
    data: str


@app.get('/user/')
async def get_user_data() -> UserData:
    """Get user data for mobile client display.

    Returns:
        UserData: user data
    """
    return USER_DATA


@app.get('/newquest/')
async def get_new_quest() -> UserData:
    """Update user data with a new quest.

    Returns:
        UserData: user data
    """
    if not USER_DATA.has_quest:
        quest_idx, quest_cat = serverutils.name_random()
        USER_DATA.has_quest = True
        USER_DATA.quest_idx = quest_idx
        USER_DATA.quest_cat = quest_cat
    return USER_DATA


@app.post('/score/')
async def score_image(raw: RawImage) -> UserData:
    """Score a user image.

    Args:
        raw (RawImage): hex-encoded flattened image

    Returns:
        UserData: user data
    """
    if not USER_DATA.has_quest:
        # do not process questless submissions,
        # client should ideally not let you do this
        return USER_DATA

    # preprocess image for inference engine
    data = bytes.fromhex(raw.data)  # undo client conversion to hex/str
    img = Image.frombytes(raw.mode, raw.size, data)
    img = np.array(img)
    img = np.transpose(img, [2, 0, 1])
    img = img.astype(np.float32) / 255

    # inference
    score = serverutils.score_image(img)

    # update user data
    USER_DATA.total_score += score
    USER_DATA.has_quest = False
    USER_DATA.quest_idx = -1
    USER_DATA.quest_cat = ''

    return USER_DATA
