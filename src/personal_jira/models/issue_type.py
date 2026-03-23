import enum


class IssueType(str, enum.Enum):
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    SUB_TASK = "sub_task"
