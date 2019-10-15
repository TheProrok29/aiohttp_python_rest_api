import pydantic as pd


class BirdSample(pd.BaseModel):
    name: str
    download_count: int
    path: pd.FilePath