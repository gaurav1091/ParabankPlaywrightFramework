from enum import Enum


class WaitStrategy(str, Enum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    ATTACHED = "attached"
    DETACHED = "detached"