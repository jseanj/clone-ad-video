import importlib.util,json,tempfile,unittest,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('campaign',ROOT/'scripts/build-skill-campaign.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

class CampaignTests(unittest.TestCase):
    def campaign(self):return json.loads((ROOT/'examples/blender-trilogy/campaign.json').read_text())
    def test_real_sources_and_dated_testimonial(self):
        data=self.campaign();C.validate_campaign(data)
        quote=data['videos']['testimonial'];self.assertEqual(quote['author'],'Pierrot Jacquet');self.assertEqual(quote['quote_date'],'2019-07-22');self.assertNotIn('rating',quote)
        self.assertTrue(any('news.ubisoft.com' in s['url'] for s in data['sources']))
    def test_no_invented_rating_or_overlapping_score(self):
        for change in ['rating','overlap','offbeat']:
            with self.subTest(change=change):
                data=self.campaign()
                if change=='rating':data['videos']['testimonial']['rating']=5
                elif change=='overlap':data['videos']['launch']['segments'][1]['start']=1
                else:data['videos']['launch']['drop']=6.5
                with self.assertRaises(ValueError):C.validate_campaign(data)
    def test_native_ast_for_all_three_scripts(self):
        import subprocess
        for name,video in self.campaign()['videos'].items():
            with self.subTest(name=name),tempfile.TemporaryDirectory() as d:
                path=Path(d)/'script.svml';path.write_text('<script id="test">'+''.join(f'<{s["id"]}><HOST>{s["text"]}</{s["id"]}>' for s in video['segments'])+'</script>')
                result=subprocess.run([str(ROOT/'scripts/cav-runner.sh'),'script',str(path),'--json'],check=True,capture_output=True,text=True)
                self.assertEqual([s['spoken_text'] for s in json.loads(result.stdout)['segments']],[s['text'] for s in video['segments']])
    def test_distinct_production_templates_no_clock_timers(self):
        for name in ['ad','launch','testimonial']:
            html=(ROOT/'templates/blender-campaign'/f'{name}.html').read_text()
            self.assertIn('window.renderFrame=function(frame)',html);self.assertIn('__CONFIG__',html)
            self.assertNotIn('Preparing design',html)
            for bad in ['Date.now(', 'Math.random(', 'setInterval(']:
                self.assertNotIn(bad,html)
    def test_original_scores_have_exact_sample_domains(self):
        for mode in ['ad','launch','testimonial']:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as d:
                video={'bpm':120,'drop':.04};project={'meta':{'total_seconds':.1},'tracks':{'voice':[{'start_seconds':0}]}}
                C.make_audio(video,project,Path(d),mode)
                for name in ['music.wav','sfx.wav']:
                    with wave.open(str(Path(d)/name)) as f:
                        self.assertEqual(f.getnframes(),4800);self.assertEqual(f.getnchannels(),2);self.assertEqual(f.getframerate(),48000)
    def test_reveal_is_visible_at_the_exact_drop(self):
        html=(ROOT/'templates/blender-campaign/launch.html').read_text()
        self.assertIn("move('#reveal .version',0,0,1.2-.2*p,0,1)",html)
        self.assertIn('wipes(t,[2.4,9.6,19.2])',html)
        self.assertNotIn('wipes(t,[2.4,6.4',html)

    def test_explicit_candidates_need_no_producer_task(self):
        artifact={'path':'accepted.wav','mode':'production'}
        self.assertEqual(C.audio_artifact({'tasks':{},'outputs':{'voice-hook.audio':artifact}},'hook'),artifact)

    def test_reused_speech_cannot_silently_change(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.wav';p.with_suffix('.json').write_text(json.dumps({'spoken_text':'old','voice_preset':'冰糖'}))
            with self.assertRaises(ValueError):C.validate_bindings({'segments':[{'id':'a','text':'new'}],'voice':'冰糖'},{'a':str(p)})
if __name__=='__main__':unittest.main()
