from datetime import datetime

import pandas as pd


class Cigar():
    def __init__(
        self, title: str = None, score: int = None, length: float = None,
        strength: str = None, gauge: int = None, size: str = None,
        filler: str = None, binder: str = None, wrapper: str = None,
        country: str = None, price: float = None,
        box_date: datetime = None, issue: str = None, tasting_note: str = None
    ):
        self.title = title
        self.score = score
        self.length = length
        self.strength = strength
        self.gauge = gauge
        self.size = size
        self.filler = filler
        self.binder = binder
        self.wrapper = wrapper
        self.country = country
        self.price = price
        self.box_date = box_date
        self.issue = issue
        self.tasting_note = tasting_note

    def to_pandas(self) -> pd.DataFrame:
        return pd.DataFrame([self.__dict__])
