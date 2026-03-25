import pytest
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate, TaskLabelsAttach
from pydantic import ValidationError


class TestLabelCreate:
    def test_valid(self) -> None:
        lc = LabelCreate(name="bug", color="#FF0000")
        assert lc.name == "bug"
        assert lc.color == "#FF0000"

    def test_invalid_color_no_hash(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(name="bug", color="FF0000")

    def test_invalid_color_short(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(name="bug", color="#FFF")

    def test_invalid_color_word(self) -> None:
        with pytest.raises(ValidationError):
            LabelCreate(name="bug", color="red")


class TestLabelUpdate:
    def test_partial(self) -> None:
        lu = LabelUpdate(name="bugfix")
        assert lu.name == "bugfix"
        assert lu.color is None

    def test_color_validation(self) -> None:
        with pytest.raises(ValidationError):
            LabelUpdate(color="invalid")


class TestLabelResponse:
    def test_fields(self) -> None:
        lr = LabelResponse(id="l1", name="bug", color="#FF0000")
        assert lr.id == "l1"


class TestTaskLabelsAttach:
    def test_valid(self) -> None:
        ta = TaskLabelsAttach(label_ids=["l1", "l2"])
        assert len(ta.label_ids) == 2
