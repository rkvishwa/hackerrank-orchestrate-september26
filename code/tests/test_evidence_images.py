from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.evidence.resolver import EvidenceResolver
from buy_or_wait.evidence.cache import image_source_hash
from buy_or_wait.ingest.loader import load_dataset

DATASET = Path(__file__).resolve().parents[2] / "dataset"


def test_verified_image_values():
    dataset = load_dataset(DATASET)
    resolver = EvidenceResolver(dataset, Settings(deterministic_mode=True, llm_enabled=False))
    for image_id, expected in [("image_01", "4365000"), ("image_02", "100000"),
                                ("image_05", "822.05"), ("image_10", "79679.26"),
                                ("image_12", "33.50")]:
        image = dataset.images_by_id[image_id]
        event = dataset.events_by_id[image.related_event_id]
        assert resolver._extract_image_amount(event, image_id).amount == Decimal(expected)


def test_image_id_is_not_an_amount_lookup():
    dataset = load_dataset(DATASET)
    resolver = EvidenceResolver(dataset, Settings(deterministic_mode=True, llm_enabled=False))
    event = dataset.events_by_id[dataset.images_by_id["image_10"].related_event_id]
    assert resolver._rule_based_image_amount(event, "image_10") is None
    changed = replace(event, description="A different amount role in the same document")
    assert resolver._extract_image_amount(changed, "image_10") is None


def test_missing_or_changed_image_does_not_reuse_cache(tmp_path):
    dataset = load_dataset(DATASET)
    event = dataset.events_by_id[dataset.images_by_id["image_10"].related_event_id]
    original = dataset.media_dir / "image_10.png"
    changed = tmp_path / "image_10.png"
    changed.write_bytes(original.read_bytes() + b"changed")
    assert image_source_hash(changed, event) != image_source_hash(original, event)
    dataset.media_dir = tmp_path
    resolver = EvidenceResolver(dataset, Settings(deterministic_mode=True, llm_enabled=False))
    assert resolver._extract_image_amount(event, "image_10") is None
    changed.unlink()
    assert resolver._extract_image_amount(event, "image_10") is None
