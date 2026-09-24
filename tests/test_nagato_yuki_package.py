"""Nagato Yuki package acceptance tests; no Redis, QQ or LLM calls.

Run from the project root:
    python -m unittest tests.test_nagato_yuki_package -v

This checks package data and the current loader/formatters. It does NOT measure
LLM response quality or prove that online message delivery works.
"""
from __future__ import annotations

import contextlib
import io
import math
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import yaml

from bot.character_loader import load_character_package
from bot.character_registry import list_characters
from bot.emotion_engine import build_long_term_emotion, calculate_memory_emotion
from bot.knowledge_formatter import (
    format_events,
    format_lore,
    format_memories,
    format_relationships,
)
from bot.memory_retriever import retrieve_memories
from bot.proactive_prompt import build_proactive_prompt
from bot.prompt import build_prompt
from bot.validators.package_validator import validate_character_package

CHARACTER_ID = 'nagato_yuki'
ROOT = Path(__file__).resolve().parents[1]
CHARACTER_DIR = ROOT / 'bot' / 'characters' / CHARACTER_ID
CORE_FILES = {
    'card.yaml': {'character'},
    'lore.yaml': {'world', 'rules', 'locations', 'culture', 'knowledge'},
    'memories.yaml': {'memories'},
    'relationships.yaml': {'relationships'},
    'events.yaml': {'events'},
    'reply_behavior.yaml': {'reply_behavior'},
}
REPLY_TYPES = ('answer', 'chat', 'tease', 'comfort', 'greet', 'share', 'ignore')
RELATIONSHIP_PAIRS = (
    ('stranger', '陌生人'), ('acquaintance', '认识'),
    ('friend', '朋友'), ('close_friend', '亲密朋友'),
)


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of accepting the last value silently."""


def construct_unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key!r}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


class NagatoYukiPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {}
        for filename in CORE_FILES:
            text = (CHARACTER_DIR / filename).read_text(encoding='utf-8')
            cls.data[filename] = yaml.load(text, Loader=UniqueKeyLoader)
        cls.package = load_character_package(CHARACTER_ID)
        cls.character = cls.package['character']
        cls.knowledge = {
            key: cls.package[key]
            for key in ('lore', 'memories', 'relationships', 'events', 'reply_behavior')
        }

    def assert_string_list(self, value, *, allow_empty=False):
        self.assertIsInstance(value, list)
        if not allow_empty:
            self.assertTrue(value)
        for item in value:
            self.assertIsInstance(item, str)
            self.assertTrue(item.strip())

    def assert_impact(self, value):
        self.assertIsInstance(value, dict)
        for emotion, score in value.items():
            self.assertIsInstance(emotion, str)
            self.assertIsInstance(score, (int, float))
            self.assertNotIsInstance(score, bool)
            self.assertTrue(math.isfinite(score))
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_six_core_files_and_yaml_shapes(self):
        for filename, required_roots in CORE_FILES.items():
            with self.subTest(filename=filename):
                text = (CHARACTER_DIR / filename).read_text(encoding='utf-8')
                self.assertNotIn('\t', text)
                self.assertIsInstance(self.data[filename], dict)
                self.assertTrue(required_roots <= set(self.data[filename]))
        # A later dialogue corpus is permitted, but is not required by these tests.
        actual = {path.name for path in CHARACTER_DIR.glob('*.yaml')}
        self.assertTrue(set(CORE_FILES) <= actual)
        self.assertFalse(actual - set(CORE_FILES) - {'dialogue_examples.yaml'})

    def test_runtime_hard_fields_have_correct_types(self):
        c = self.character
        for name in ('meta', 'identity', 'personality', 'speech_style', 'behavior', 'goals', 'roleplay_rules'):
            self.assertIsInstance(c[name], dict)
        self.assertIsInstance(c['identity']['background'], str)
        self.assertTrue(c['identity']['background'].strip())
        for name in ('core_traits', 'values', 'weaknesses', 'fears'):
            self.assert_string_list(c['personality'][name])
        self.assertNotIn('traits', c['personality'])
        for name in ('tone', 'habits', 'forbidden'):
            self.assert_string_list(c['speech_style'][name])
        for name in ('greeting', 'praised', 'teased', 'angry', 'sad', 'excited'):
            self.assertIsInstance(c['behavior'][name], str)
        for name in ('short_term', 'long_term'):
            self.assertIsInstance(c['goals'][name], str)
        for name in ('must', 'must_not'):
            self.assert_string_list(c['roleplay_rules'][name])

    def test_metadata_id_and_registry_discovery(self):
        meta = self.character['meta']
        self.assertEqual(meta['id'], CHARACTER_ID)
        self.assertRegex(meta['id'], r'^[a-z][a-z0-9_]*$')
        self.assertEqual(meta['name'], '长门有希')
        self.assert_string_list(meta['aliases'])
        self.assertIn(CHARACTER_ID, list_characters())

    def test_name_variants_match_current_substring_contract(self):
        # Mirrors the existing resolver's case-insensitive substring contract;
        # this is a data check, not a claim of end-to-end target evaluation.
        meta = self.character['meta']
        names = [meta['name'], *meta['aliases']]
        for message in ('长门有希晚上好', '長門有希，今天怎么样', '长门，你在吗',
                        '長門，帮我看看', 'NAGATO YUKI hello', 'Yuki Nagato hello'):
            with self.subTest(message=message):
                self.assertTrue(any(name.lower() in message.lower() for name in names))

    def test_aliases_do_not_match_common_hope_phrases(self):
        meta = self.character['meta']
        names = [meta['name'], *meta['aliases']]
        self.assertNotIn('有希', names)
        self.assertNotIn('Yuki', names)
        for message in ('还有希望', '这次没有希望了', '今天有希望完成', '希望明天别下雨',
                        '今晚吃什么', '芙宁娜晚上好'):
            with self.subTest(message=message):
                self.assertFalse(any(name.lower() in message.lower() for name in names))

    def test_lore_is_formatted_by_real_formatter(self):
        lore = self.package['lore']
        self.assert_string_list(lore['rules'])
        self.assertIsInstance(lore['locations'], dict)
        result = format_lore(lore)
        for text in ('SOS团', '文艺部部室', '《消失》事件前', '现实'):
            self.assertIn(text, result)

    def test_memories_have_unique_ids_tags_and_numeric_impacts(self):
        memories = self.package['memories']['memories']
        self.assertTrue(memories)
        self.assertEqual(len(memories), len({m['id'] for m in memories}))
        for memory in memories:
            with self.subTest(memory=memory['id']):
                self.assertRegex(memory['id'], r'^ny_[a-z0-9_]+$')
                self.assertTrue(memory['title'].strip())
                self.assertTrue(memory['description'].strip())
                self.assert_string_list(memory['tags'])
                self.assert_impact(memory['emotional_impact'])
                self.assertIs(type(memory['importance']), int)
                self.assertTrue(0 <= memory['importance'] <= 100)
        formatted = format_memories(self.package['memories'])
        self.assertIn(memories[0]['title'], formatted)

    def test_memory_retrieval_uses_actual_tags(self):
        cases = (
            ('文艺部的部室', 'ny_literature_room'),
            ('朝仓的袭击', 'ny_protected_kyon'),
            ('电脑研究部的游戏对战', 'ny_computer_match'),
        )
        for query, expected in cases:
            with self.subTest(query=query):
                result = retrieve_memories(query, self.package['memories'], top_k=1)
                self.assertEqual(result[0]['id'], expected)

    def test_memory_emotion_does_not_start_saturated(self):
        raw = calculate_memory_emotion(self.package['memories'])
        normalized = build_long_term_emotion(self.package['memories'])
        self.assertTrue(raw)
        self.assertTrue(all(0 <= score < 100 for score in raw.values()))
        self.assertEqual(raw, normalized)

    def test_fixed_relationships_are_not_user_bindings(self):
        people = self.package['relationships']['relationships']['characters']
        self.assertEqual(set(people), {
            'haruhi_suzumiya', 'kyon', 'mikuru_asahina', 'itsuki_koizumi', 'ryoko_asakura'
        })
        for person in people.values():
            for name in ('name', 'relationship', 'attitude', 'history'):
                self.assertIsInstance(person[name], str)
                self.assertTrue(person[name].strip())
        self.assertIn('阿虚', format_relationships(self.package['relationships']))

    def test_events_have_runtime_compatible_shape(self):
        events = self.package['events']['events']
        self.assertEqual(len(events), len({event['id'] for event in events}))
        for event in events:
            self.assertTrue(event['title'].strip())
            self.assertTrue(event['description'].strip())
            self.assert_string_list(event['tags'])
            self.assertIs(type(event['importance']), int)
            self.assertTrue(0 <= event['importance'] <= 100)
            self.assert_impact(event['emotional_impact'])
        self.assertIn('文化祭', format_events(self.package['events']))

    def test_behavior_modes_and_bilingual_relationship_levels(self):
        behavior = self.package['reply_behavior']
        self.assertTrue(set(REPLY_TYPES) <= set(behavior['reply_type_behavior']))
        for en, cn in RELATIONSHIP_PAIRS:
            self.assertEqual(behavior['relationship_behavior'][en], behavior['relationship_behavior'][cn])
        self.assertTrue({'normal', 'happy', 'sad', 'melancholy', 'angry'} <= set(behavior['emotion_behavior']))
        self.assertTrue({'group_chat', 'private_chat', 'funny', 'serious', 'emotional', 'conflict', 'quiet'}
                        <= set(behavior['scene_behavior']))
        for section in ('reply_type_behavior', 'relationship_behavior', 'emotion_behavior', 'scene_behavior'):
            for item in behavior[section].values():
                self.assertTrue(item['description'].strip())
                self.assert_string_list(item['rules'])

    def test_proactive_config_is_typed_and_in_range(self):
        p = self.package['reply_behavior']['proactive']
        self.assertIs(type(p['enabled']), bool)
        self.assertIs(type(p['min_context_messages']), int)
        self.assertGreaterEqual(p['min_context_messages'], 1)
        self.assertIs(type(p['cooldown_seconds']), int)
        self.assertGreaterEqual(p['cooldown_seconds'], 0)
        self.assertNotIsInstance(p['min_join_probability'], bool)
        self.assertTrue(0 <= p['min_join_probability'] <= 1)

    def test_actual_package_validator_returns_true(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = validate_character_package(CHARACTER_ID)
        self.assertTrue(result, output.getvalue())

    def test_loader_allows_absent_optional_dialogue_file(self):
        # Deliberately exercise six files only, even if a future corpus is installed.
        with tempfile.TemporaryDirectory() as temp:
            character_path = Path(temp) / CHARACTER_ID
            character_path.mkdir()
            for filename in CORE_FILES:
                shutil.copy2(CHARACTER_DIR / filename, character_path / filename)
            with patch('bot.character_loader.CHARACTER_DIR', temp):
                package = load_character_package(CHARACTER_ID)
            self.assertEqual(package['dialogue_style'], {})
            self.assertEqual(package['character']['meta']['id'], CHARACTER_ID)

    def test_reactive_prompt_builds_for_all_reply_modes_and_levels(self):
        for reply_type in REPLY_TYPES:
            for level in ('陌生人', '朋友', '亲密朋友', 'stranger', 'friend'):
                with self.subTest(reply_type=reply_type, level=level):
                    prompt = build_prompt(
                        self.character, knowledge=self.knowledge,
                        reply_type=reply_type, relationship_level=level,
                        relationship={'trust': 0, 'intimacy': 0, 'familiarity': 0},
                        message_context={'target': 'character', 'person': 'character'},
                    )
                    self.assertIn('长门有希', prompt)
                    self.assertIn('资讯统合思念体', prompt)
                    self.assertIn(self.package['reply_behavior']['reply_type_behavior'][reply_type]['description'], prompt)
                    self.assertIn(self.package['reply_behavior']['relationship_behavior'][level]['description'], prompt)

    def test_proactive_prompt_builds_without_dialogue_corpus(self):
        package = dict(self.package, dialogue_style={})
        prompt = build_proactive_prompt(
            package,
            {'scene': 'quiet', 'topic': '阅读', 'emotion': 'normal', 'energy': 'low'},
            {'messages': [{'user_id': 'user_a', 'message': '最近想看书', 'sender_type': 'user'}]},
            'share',
        )
        self.assertIn('长门有希', prompt)
        self.assertIn('最近想看书', prompt)
        self.assertIn('主动发言', prompt)


if __name__ == '__main__':
    unittest.main()
