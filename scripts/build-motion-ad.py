#!/usr/bin/env python3
"""Build a measured, continuous kinetic-report ad using only clone-any-video media tools."""
import argparse
import array
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import wave

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('batch', ROOT/'scripts/batch-ad-matrix.py')
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def engine(args, directory, name, environment):
    command = [str(ROOT/'scripts/cav-runner.sh'), *map(str, args)]
    with (directory/f'{name}.log').open('w') as log:
        done = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
    if done.returncode:
        raise RuntimeError(f'{name} failed; inspect {directory/name}.log')
    return (directory/f'{name}.log').read_text()


def build(run, directory, name, environment, output=None):
    args = ['build', run]
    if output:
        args += ['--output', output]
    log = engine(args, directory, name, environment)
    match = re.search(r'Production Result: (.+)', log)
    if not match:
        raise RuntimeError('Build did not return a Result')
    path = Path(match.group(1).strip())
    return path, json.loads(path.read_text())


def voice_candidates(result_path, row, voice):
    """Only reuse production takes whose recorded speech and preset exactly match."""
    result = json.loads(result_path.read_text())
    if result.get('mock'):
        raise ValueError('A mock Result cannot supply production voices')
    candidates, satisfy = {}, {}
    for segment, expected in zip(batch.SEGMENTS, batch.texts(row)):
        artifact = result['tasks'][f'voice-{segment}']['outputs']['audio']
        meta = json.loads(Path(artifact['path']).with_suffix('.json').read_text())
        if artifact['mode'] != 'production' or meta['spoken_text'] != expected or meta.get('voice_preset') != voice:
            raise ValueError(f'Cannot reuse {segment}: spoken text, preset or provenance differs')
        candidates[segment] = {'kind': 'result', 'result': str(result_path), 'output': f'voice-{segment}.audio'}
        satisfy[f'voice-{segment}.audio'] = segment
    return candidates, satisfy


def score(project, directory):
    """Original deterministic 120-BPM instrumental and section-synced design sounds, not mock media."""
    rate = 48000
    frames = round(project['meta']['total_seconds']*rate)
    starts = [v['start_seconds'] for v in project['tracks']['voice']]
    music, effects = array.array('h'), array.array('h')
    for i in range(frames):
        t = i/rate
        section = max(j for j, start in enumerate(starts) if t >= start)
        local = t-starts[section]
        beat = local % .5
        noise = math.sin(i*2.173)*math.sin(i*.971+1.3)
        kick = .30*math.exp(-beat*22)*math.sin(math.tau*(48*beat+6*(1-math.exp(-beat*18))))
        hat = .065*math.exp(-(local % .25)*110)*noise
        snare = .10*math.exp(-beat*38)*noise if int(local/.5)%2 else 0
        bassfreq = [65.406,58.27,77.78,65.406,51.913][section]
        bass = .13*math.exp(-beat*6)*math.sin(math.tau*bassfreq*t)
        pad = sum(math.sin(math.tau*f*t) for f in [261.626,311.127,391.995])*.022*(.5+.5*math.exp(-beat*5))
        fade = min(1,t/.15,max(0,(frames/rate-t)/.65))
        sound = (kick+hat+snare+bass+pad)*fade
        fx = 0
        for mark in starts:
            dt=t-mark
            if 0<=dt<.5:
                fx += .42*math.exp(-dt*15)*math.sin(math.tau*(53*dt+2.5*(1-math.exp(-dt*20))))
            if -.22<dt<0:
                fx += noise*.11*((dt+.22)/.22)**2
        # Subtle eighth-note stereo movement; hard limit is only a numerical safeguard.
        for channel in (0,1):
            stereo = sound + .014*math.sin(math.tau*523.25*t+(channel*.5))*math.exp(-beat*12)
            music.append(round(max(-.95,min(.95,stereo))*32767))
            effects.append(round(max(-.95,min(.95,fx))*32767))
    for name, samples in [('score.wav',music),('design-sfx.wav',effects)]:
        with wave.open(str(directory/name),'wb') as f:
            f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(samples.tobytes())
    save(directory/'score-source.json', {'kind':'original authored procedural instrumental', 'bpm':120,
         'sample_rate':rate,'section_cues':starts,'seed':'analytic deterministic functions','mock':False,
         'description':'Synthesized kick, bass, chord stabs, hats, section impacts and short reverse swells.'})


def render_program(template, project, row, aspect, workspace):
    w,h = batch.ASPECT_SPECS[aspect]
    value = re.search(r'\d+(?:\.\d+)?',row['proof'])
    config = {'width':w,'height':h,'fps':project['meta']['fps'],'totalFrames':project['meta']['total_frames'],
              'proofValue':float(value.group()) if value else 11,
              'hero':row.get('hero') or '2H','ctaShort':row.get('cta_display') or row['cta'].split('—')[0].strip(),
              'workspace':'graph-resource://asset:workspace' if workspace else '',
              'segments':[dict(start_frame=v['start_frame'],end_frame=v['end_frame'],copy=text)
                          for v,text in zip(project['tracks']['voice'],batch.texts(row))]}
    # Never allow a CSV value to terminate the embedded script.
    config['segments'][-1]['end_frame'] = config['totalFrames']
    return template.replace('__AD_CONFIG__',json.dumps(config,ensure_ascii=False).replace('<','\\u003c'))


def validate_campaign(row):
    # The visual metaphors belong to this reporting campaign, not arbitrary products.
    if not re.search(r'\b2\s*(?:hours?|hrs?)\b',row['hook'],re.I):
        raise ValueError('kinetic-report requires a Hook about 2 hours; create a new motif for another claim')
    if not re.search(r'\bhours?\b',row['proof'],re.I) or not re.search(r'\bweek\b',row['proof'],re.I):
        raise ValueError('kinetic-report proof must describe weekly hours saved')
    if not re.search(r'14[ -]*day',row['cta'],re.I):
        raise ValueError('kinetic-report offer is 14 days; update the offer design for a different campaign')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--id')
    parser.add_argument('--voice',default='alloy')
    parser.add_argument('--aspect',choices=batch.ASPECT_SPECS,default='9:16')
    parser.add_argument('--env-file',type=Path)
    parser.add_argument('--workspace-image',type=Path,required=True,help='Accepted production concept/product image; must have provenance')
    parser.add_argument('--voice-result',type=Path,help='Reuse explicitly accepted matching real TTS outputs')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--tail-hold',type=float,default=1.5,help='Additional CTA dwell after measured speech, seconds')
    parser.add_argument('--prepare-only',action='store_true',help='Stop after real voices, measured timing and HTML authoring for still review')
    parser.add_argument('--reuse-preparation',type=Path,help='Existing preparation Result; avoids resubmitting voices')
    args=parser.parse_args()
    if not args.workspace_image.is_file():
        parser.error('workspace-image does not exist')
    rows=batch.load_rows(args.csv)
    row=next((r for r in rows if not args.id or r['id']==args.id),None)
    if row is None:parser.error('Variant id not found')
    validate_campaign(row)
    directory=args.directory.resolve();directory.mkdir(parents=True,exist_ok=True)
    environment=dict(os.environ)
    if args.env_file:environment['CAV_ENV_FILE']=str(args.env_file.resolve())
    batch.compile_variant(row,directory,args.aspect,args.voice)
    prep={'format':'clone-any-video.run@1','author':f'{row["id"]}.author.json','targets':['align.project']}
    if args.voice_result:
        prep['candidates'],prep['satisfy']=voice_candidates(args.voice_result.resolve(),row,args.voice)
    if args.reuse_preparation:prep['reuse']=str(args.reuse_preparation.resolve())
    save(directory/'prepare.run.json',prep)
    print('Preparing real voices and measured timing.',flush=True)
    prepared_path,prepared=build(directory/'prepare.run.json',directory,'prepare',environment)
    project=json.loads(Path(prepared['tasks']['align']['outputs']['project']['path']).read_text())
    if not math.isfinite(args.tail_hold) or not 0 <= args.tail_hold <= 10:
        raise ValueError('tail-hold must be between 0 and 10 seconds')
    project['meta']['total_frames'] += round(args.tail_hold*batch.FPS)
    project['meta']['total_seconds'] = project['meta']['total_frames']/batch.FPS
    if prepared.get('mock'):raise ValueError('Production preparation cannot use mock assets')
    # Each voice window remains in the program; the visual track is one continuous edit.
    project['shots']=[{'id':'shot_master','segment_id':'hook','shot_index':1,'start_seconds':0,
        'end_seconds':project['meta']['total_seconds'],'start_frame':0,'end_frame':project['meta']['total_frames'],
        'duration_seconds':project['meta']['total_seconds'],'visual_type':'GeneratedVideo',
        'description':'Continuous kinetic typography / UI / metric / CTA master','prompt_hint':''}]
    project['tracks']['visual_bg']=[];project['tracks']['visual_components']=[]
    project['tracks']['sfx']=[{'id':'design','name':'Authored section accents','start_seconds':0,
        'end_seconds':project['meta']['total_seconds'],'start_frame':0,'end_frame':project['meta']['total_frames'],
        'payload':{'gain':.65}}]
    save(directory/'motion.project.json',project)
    template=(ROOT/'templates/kinetic-report/index.html').read_text()
    program=render_program(template,project,row,args.aspect,True)
    (directory/'motion.html').write_text(program)
    (directory/'preview.html').write_text(program.replace('graph-resource://asset:workspace',args.workspace_image.resolve().as_uri()))
    save(directory/'preparation.json',{'result':str(prepared_path),'total_frames':project['meta']['total_frames']})
    if args.prepare_only:
        print('Prepared for still review:',directory/'preview.html',flush=True);return
    score(project,directory)
    for name in ['score.wav','design-sfx.wav']:
        engine(['admit-media','--asset',directory/name],directory,f'admit-{name}',environment)
    w,h=batch.ASPECT_SPECS[args.aspect]
    voices={f'voice:{s}':batch.file_input(prepared['tasks'][f'voice-{s}']['outputs']['audio']['path'],'audio') for s in batch.SEGMENTS}
    author={'format':'clone-any-video.author@1','tasks':[
      {'id':'program','action':{'producer':'render-html','frames':project['meta']['total_frames'],
       'config':{'width':w,'height':h,'fps':batch.FPS,'crf':18,'preset':'fast','transparent':False,'timeout_seconds':30}},
       'inputs':{'html':batch.file_input('motion.html','html'),'asset:workspace':batch.file_input(str(args.workspace_image.resolve()),'image')}},
      {'id':'mix','action':{'producer':'mix','ducking':{'lead_margin_seconds':.08,'tail_margin_seconds':.15,'ramp_duration_seconds':.10,'ducked_gain':.35,'normal_gain':.65}},
       'inputs':{'script':batch.script_input(row['id']),'project':batch.file_input('motion.project.json','project'),
                 **voices,'bgm':batch.file_input('score.wav','audio'),'sfx:design':batch.file_input('design-sfx.wav','audio')}},
      {'id':'compose','action':{'producer':'compose'},'inputs':{'project':batch.file_input('motion.project.json','project'),
       'audio':batch.output('mix.audio'),'background:shot_master':batch.output('program.video')}},
      {'id':'review','action':{'producer':'review'},'inputs':{'project':batch.output('compose.project'),'video':batch.output('compose.video')}}],
      'outputs':{'final.video':{'task':'compose','port':'video'},'final.review':{'task':'review','port':'report'}}}
    save(directory/'motion.author.json',author)
    save(directory/'render.run.json',{'format':'clone-any-video.run@1','author':'motion.author.json','targets':['program.video','mix.audio']})
    print('Capturing continuous motion and mixing real media.',flush=True)
    rendered_path,rendered=build(directory/'render.run.json',directory,'render',environment)
    mixed=rendered['tasks']['mix']['outputs']['audio']['path']
    engine(['media','prepare-audio','--input',mixed,'--output',directory/'master.wav','--target-lufs','-16','--max-true-peak','-1'],directory,'master',environment)
    save(directory/'final.run.json',{'format':'clone-any-video.run@1','author':'motion.author.json','targets':['final.video','final.review'],
         'reuse':str(rendered_path),'candidates':{'master':{'kind':'file','path':'master.wav','type':'audio'}},'satisfy':{'mix.audio':'master'}})
    args.output.resolve().parent.mkdir(parents=True,exist_ok=True)
    final_path,final=build(directory/'final.run.json',directory,'final',environment,args.output.resolve())
    report=Path(final['tasks']['review']['outputs']['report']['path'])
    print('Production video:',args.output.resolve(),flush=True)
    print('Result:',final_path,flush=True);print('Review:',report,flush=True)


if __name__=='__main__':
    main()
