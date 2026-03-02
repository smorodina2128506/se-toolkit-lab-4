"""Unit tests for interaction filtering logic."""

from app.models.interaction import InteractionLog
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_includes_interaction_with_different_learner_id() -> None:
    """Test that filtering by item_id=1 includes interaction where learner_id is different."""
    interactions = [_make_log(1, learner_id=2, item_id=1)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_excludes_interaction_with_different_learner_id() -> None:
    """Test that filtering by item_id=1 excludes interaction where item_id is different."""
    interactions = [_make_log(1, learner_id=1, item_id=2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 0


def test_filter_returns_all_matching_when_multiple_same_item_id() -> None:
    """Test that filtering returns all interactions with matching item_id, not just the first."""
    interactions = [
        _make_log(1, learner_id=1, item_id=5),
        _make_log(2, learner_id=2, item_id=5),
        _make_log(3, learner_id=3, item_id=5),
        _make_log(4, learner_id=1, item_id=3),
    ]
    result = _filter_by_item_id(interactions, 5)
    assert len(result) == 3
    assert all(i.item_id == 5 for i in result)


def test_filter_with_zero_item_id() -> None:
    """Test filtering with item_id=0 as a boundary value."""
    interactions = [
        _make_log(1, learner_id=1, item_id=0),
        _make_log(2, learner_id=2, item_id=1),
    ]
    result = _filter_by_item_id(interactions, 0)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].item_id == 0


def test_filter_returns_empty_when_no_matching_item_id() -> None:
    """Test filtering returns empty list when item_id does not exist in any interaction."""
    interactions = [
        _make_log(1, learner_id=1, item_id=1),
        _make_log(2, learner_id=2, item_id=2),
        _make_log(3, learner_id=3, item_id=3),
    ]
    result = _filter_by_item_id(interactions, 999)
    assert result == []


def test_filter_with_very_large_item_id() -> None:
    """Test filtering with a very large item_id value (boundary testing)."""
    large_item_id = 2**31 - 1  # Max 32-bit signed integer
    interactions = [
        _make_log(1, learner_id=1, item_id=large_item_id),
        _make_log(2, learner_id=2, item_id=1),
    ]
    result = _filter_by_item_id(interactions, large_item_id)
    assert len(result) == 1
    assert result[0].id == 1
    assert result[0].item_id == large_item_id
