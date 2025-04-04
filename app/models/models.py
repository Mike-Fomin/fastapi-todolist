from pydantic import BaseModel, ConfigDict


class ToDoItemPy(BaseModel):
    title: str
    description: str | None = None
    done: bool = False

    model_config = ConfigDict(extra="forbid")


class UpgradeItemPy(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool = False

    model_config = ConfigDict(extra="forbid")


class UserPy(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(extra="forbid")
