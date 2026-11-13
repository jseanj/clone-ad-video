import csv
import importlib.util
import tempfile
import unittest
import subprocess
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('batch', ROOT / 'scripts/batch-ad-matrix.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.rows = batch.load_rows(ROOT/'examples/ad-creative-batch/variants.csv', 'hook')

    def test_complete_typed_graph_and_explicit_dependencies(self):
        graph = batch.generate_author_dag(self.rows[0], Path('.'), '9:16')
        self.assertEqual(graph['outputs']['final.video'], {'task': 'compose', 'port': 'video'})
        self.assertEqual(graph['outputs']['final.review'], {'task': 'review', 'port': 'report'})
        tasks = {t['id']: t for t in graph['tasks']}
        for s in batch.SEGMENTS:
            self.assertEqual(tasks[f'voice-{s}']['inputs']['script']['segment'], s)
            self.assertIn(f'voice:{s}', tasks['align']['inputs'])
            self.assertIn(f'voice:{s}', tasks['mix']['inputs'])
            self.assertEqual(tasks[f'card-{s}']['inputs']['html']['path'], f'{s}_card.html')
            self.assertEqual(tasks['compose']['inputs'][f'background:shot_{s}']['output'], f'card-{s}.video')

    def test_provider_specific_voice_preset(self):
        graph = batch.generate_author_dag(self.rows[0], Path('.'), '9:16', voice='冰糖')
        voices = [t['action']['voice'] for t in graph['tasks'] if t['action']['producer'] == 'voice']
        self.assertEqual(voices, ['冰糖'] * 5)

    def test_engine_speech_matches_plain_text(self):
        row = dict(self.rows[0], hook='R&D reports "quoted" today?')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'test.svml'
            path.write_text(batch.generate_svml(row))
            result = subprocess.run([str(ROOT/'scripts/cav-runner.sh'), 'script', str(path), '--json'], capture_output=True, text=True, check=True)
            doc = json.loads(result.stdout)
            self.assertEqual([s['spoken_text'] for s in doc['segments']], batch.texts(row))
        html = batch.generate_component_html('<reports>', 'test', '#38bdf8', '#0f172a', '9:16')
        self.assertIn('&lt;reports&gt;', html)
        self.assertNotIn('<reports>', html)

    def write_rows(self, directory, rows):
        path = Path(directory)/'variants.csv'
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_single_variable_rejects_cta_or_style_changes(self):
        for field, value in [('cta', 'Buy now'), ('accent', '#ff0000')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                rows = [dict(r) for r in self.rows]
                rows[1][field] = value
                with self.assertRaisesRegex(ValueError, field):
                    batch.load_rows(self.write_rows(d, rows), 'hook')

    def test_rejects_unsafe_duplicate_ids_missing_text_and_css(self):
        for field, value in [('id', '../escape'), ('id', self.rows[0]['id']),
                             ('proof', ''), ('hook', '<HOST> injected'), ('accent', 'red;display:none')]:
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as d:
                rows = [dict(r) for r in self.rows]
                rows[1][field] = value
                with self.assertRaises(ValueError):
                    batch.load_rows(self.write_rows(d, rows))

    def test_all_aspects_have_gapless_shots_and_explicit_hold(self):
        for aspect, dimensions in batch.ASPECT_SPECS.items():
            p = batch.generate_layout(self.rows[0], aspect)
            self.assertEqual((p['meta']['width'], p['meta']['height']), dimensions)
            self.assertEqual([s['start_frame'] for s in p['shots']], [0,150,300,450,600])
            self.assertEqual(p['shots'][-1]['end_frame'], p['meta']['total_frames'])
            self.assertTrue(all(t['payload']['sampling']['shortage'] == 'hold' for t in p['tracks']['visual_bg']))

    def test_checked_in_example_matches_compiler(self):
        import json
        directory = ROOT/'examples/ad-creative-batch'
        row = dict(self.rows[0], id='script')
        self.assertEqual(json.loads((directory/'author.json').read_text()), batch.generate_author_dag(row, directory, '9:16'))
        self.assertEqual((directory/'script.svml').read_text(), batch.generate_svml(row))


if __name__ == '__main__':
    unittest.main()
