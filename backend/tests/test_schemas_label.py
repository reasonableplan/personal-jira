import pytest
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate, TaskLabelsAttach
from pydantic import ValidationError


class TestLabelCreate:
    def test_valid(self) -> None:
        schema = LabelCreate(name="bug", color="#FF0000")
        assert schema.name == "bug"
        assert schema.color == "#FF0000"

    def test_color_lowercase_normalized(self) -> None:
        schema = LabelCreate(name="bug", color="#ff00aa")
        assert schema.color == "#FF00AA"

    def test_invalid_color_no_hash(self) -> None:
        with pytest.raises(ValidationError, match="color"):
            LabelCreate(name="bug", color="FF0000")

    def test_invalid_color_short(self) -> None:
        with pytest.raises(ValidationError, match="color"):
            LabelCreate(name="bug", color="#FFF")

    def test_invalid_color_bad_chars(self) -> None:
        with pytest.raises(ValidationError, match="color"):
            LabelCreate(name="bug", color="#ZZZZZZ")

    def test_missing_name(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(color="#FF0000")  # type: ignore[call-arg]

    def test_missing_color(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(name="bug")  # type: ignore[call-arg]


class TestLabelUpdate:
    def test_partial_name_only(self) -> None:
        schema = LabelUpdate(name="feature")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"name": "feature"}

    def test_partial_color_only(self) -> None:
        schema = LabelUpdate(color="#00FF00")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"color": "#00FF00"}

    def test_empty(self) -> None:
        schema = LabelUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}

    def test_invalid_color(self) -> None:
        with pytest.raises(ValidationError, match="color"):
            LabelUpdate(color="red")

    def test_color_normalized(self) -> None:
        schema = LabelUpdate(color="#abcdef")
        assert schema.color == "#ABCDEF"


class TestLabelResponse:
    def test_from_attributes(self) -> None:
        class FakeLabel:
            id = "abc"
            name = "bug"
            color = "#FF0000"

        resp = LabelResponse.model_validate(FakeLabel(), from_attributes=True)
        assert resp.id == "abc"
        assert resp.name == "bug"
        assert resp.color == "#FF0000"


class TestTaskLabelsAttach:
    def test_valid(self) -> None:
        schema = TaskLabelsAttach(label_ids=["id1", "id2"])
        assert schema.label_ids == ["id1", "id2"]

    def test_empty_list(self) -> None:
        schema = TaskLabelsAttach(label_ids=[])
        assert schema.label_ids == []

    def test_missing_label_ids(self) -> None:
        with pytest.raises(ValidationError):
            TaskLabelsAttach()  # type: ignore[call-arg]
