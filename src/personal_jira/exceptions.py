import uuid


class PersonalJiraError(Exception):
    pass


class IssueNotFoundError(PersonalJiraError):
    def __init__(self, issue_id: uuid.UUID) -> None:
        super().__init__(f"Issue {issue_id} not found")
        self.issue_id = issue_id


class DependencyNotFoundError(PersonalJiraError):
    def __init__(self, dependency_id: uuid.UUID) -> None:
        super().__init__(f"Dependency {dependency_id} not found")
        self.dependency_id = dependency_id


class SelfDependencyError(PersonalJiraError):
    def __init__(self) -> None:
        super().__init__("An issue cannot depend on itself")


class DuplicateDependencyError(PersonalJiraError):
    def __init__(self) -> None:
        super().__init__("This dependency already exists")


class CircularDependencyError(PersonalJiraError):
    def __init__(self, cycle: list[uuid.UUID]) -> None:
        super().__init__(f"Circular dependency detected: {' -> '.join(str(i) for i in cycle)}")
        self.cycle = cycle
