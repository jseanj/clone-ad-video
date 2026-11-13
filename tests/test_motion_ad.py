import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import wave

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('motion',ROOT/'scripts/build-motion-ad.py')
motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)


class MotionTests(unittest.TestCase):
    def row(self):
        return motion.batch.load_rows(ROOT/'examples/ad-creative-batch/variants.csv','hook')[0]

    def test_config_uses_measured_frames_and_safe_script_embedding(self):
        row=dict(self.row(),cta='End </script> safely')
        project=motion.batch.generate_layout(row,'9:16')
        project['meta']['total_frames']=795
        template='CONFIG=__AD_CONFIG__'
        html=motion.render_program(template,project,row,'9:16',True)
        self.assertNotIn('</script>',html)
        config=json.loads(html.removeprefix('CONFIG='))
        self.assertEqual(config['segments'][-1]['end_frame'],795)
        self.assertEqual(config['ctaShort'],row['cta'])
        self.assertEqual(config['workspace'],'graph-resource://asset:workspace')
        self.assertEqual(config['segments'][0]['copy'],row['hook'])

    def test_old_polluted_or_wrong_preset_voice_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);row=self.row();tasks={}
            for segment,text in zip(motion.batch.SEGMENTS,motion.batch.texts(row)):
                path=directory/f'{segment}.wav'
                path.with_suffix('.json').write_text(json.dumps({'spoken_text':text,'voice_preset':'冰糖'}))
                tasks[f'voice-{segment}']={'outputs':{'audio':{'path':str(path),'mode':'production'}}}
            result=directory/'result.json';result.write_text(json.dumps({'mock':False,'tasks':tasks}))
            candidates,satisfy=motion.voice_candidates(result,row,'冰糖')
            self.assertEqual(len(candidates),5);self.assertEqual(len(satisfy),5)
            hook=directory/'hook.json';metadata=json.loads(hook.read_text());metadata['spoken_text']+=' /HOST>';hook.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'Cannot reuse hook'):
                motion.voice_candidates(result,row,'冰糖')
            with self.assertRaises(ValueError):motion.voice_candidates(result,row,'alloy')

    def test_original_score_duration_channels_and_determinism(self):
        project={'meta':{'total_seconds':.15},'tracks':{'voice':[{'start_seconds':0}]}}
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d);motion.score(project,directory)
            first=(directory/'score.wav').read_bytes();motion.score(project,directory)
            self.assertEqual(first,(directory/'score.wav').read_bytes())
            with wave.open(str(directory/'score.wav')) as f:
                self.assertEqual(f.getnchannels(),2);self.assertEqual(f.getframerate(),48000)
                self.assertEqual(f.getnframes(),7200)
                self.assertTrue(any(f.readframes(7200)))

    def test_campaign_metaphors_cannot_misstate_another_offer(self):
        row=self.row();motion.validate_campaign(row)
        for field,value in [('hook','Save 5 hours'),('proof','Adopted by 400 teams'),('cta','Seven day trial')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                motion.validate_campaign(dict(row,**{field:value}))

    def test_template_has_continuous_distinct_scene_program(self):
        html=(ROOT/'templates/kinetic-report/index.html').read_text()
        self.assertIn('window.renderFrame=function(frame)',html)
        for segment in motion.batch.SEGMENTS:self.assertIn(f'id="{segment}"',html)
        for forbidden in ['Date.now(', 'Math.random(', 'setInterval(', 'gsap.min.js','remotion']:
            self.assertNotIn(forbidden,html)


if __name__=='__main__':unittest.main()
