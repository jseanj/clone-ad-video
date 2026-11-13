#!/usr/bin/env python3
"""Production campaign runner for three independently art-directed native CAV skills."""
import argparse,array,importlib.util,json,math,os,re,subprocess,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('motion',ROOT/'scripts/build-motion-ad.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
FPS=30

def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def file(p,kind):return {'kind':'file','path':str(p),'type':kind}
def output(name):return {'kind':'output','output':name}

def layout(video,vid):
    segments=video['segments'];duration=video.get('duration',len(segments)*5)
    project={'format':'clone-any-video.project@1','meta':{'id':vid,'title':vid,'width':1080,'height':1920,'fps':FPS,'total_frames':round(duration*FPS),'total_seconds':duration},
      'shots':[],'tracks':{k:[] for k in ['visual_bg','visual_components','captions','voice','bgm','sfx']},'asset_tasks':[]}
    for i,s in enumerate(segments):
        a=s.get('start',i*5);b=s.get('end',(i+1)*5)
        project['tracks']['voice'].append({'id':'voice_'+s['id'],'name':s['id'],'start_seconds':a,'end_seconds':b,'start_frame':round(a*FPS),'end_frame':round(b*FPS),'payload':{'spoken_text':s['text'],'timing_status':'estimated'}})
        project['shots'].append({'id':'shot_'+s['id'],'segment_id':s['id'],'shot_index':i+1,'start_seconds':a,'end_seconds':b,'start_frame':round(a*FPS),'end_frame':round(b*FPS),'duration_seconds':b-a,'visual_type':'GeneratedVideo','description':s['id'],'prompt_hint':''})
    return project

def make_audio(video,project,directory,mode):
    rate=48000;total=project['meta']['total_seconds'];N=round(total*rate);beat=60/video['bpm'];drop=video.get('drop',0)
    music=array.array('h');effects=array.array('h');starts=[s['start_seconds'] for s in project['tracks']['voice']]
    for i in range(N):
        t=i/rate;r=t%beat;noise=math.sin(i*2.173)*math.sin(i*.971+1.3)
        if mode=='testimonial':
            # A restrained, spacious electric-piano bed; no drum groove under the quote.
            measure=int(t/3)%4;root=[130.813,116.541,155.563,103.826][measure]
            age=t%3;chord=sum(math.sin(math.tau*f*t)*math.exp(-age*1.0) for f in [root,root*1.25992,root*1.4983,root*2])*.035
            snd=chord+.015*math.sin(math.tau*root*.5*t)
        else:
            strength=.32 if mode=='ad' or t>=drop else .08
            kick=strength*math.exp(-r*24)*math.sin(math.tau*(48*r+5*(1-math.exp(-r*22))))
            hat=.05*math.exp(-(t%(beat/2))*120)*noise
            snare=.10*math.exp(-r*40)*noise if int(t/beat)%2 else 0
            root=[65.406,77.782,58.27,51.913][int(t/(beat*4))%4]
            bass=.14*math.exp(-r*7)*math.sin(math.tau*root*t)
            chord=.021*sum(math.sin(math.tau*f*t) for f in [261.626,311.127,391.995])*(.4+.6*math.exp(-r*6))
            snd=kick+hat+snare+bass+chord
            if mode=='launch' and t<drop:
                snd*=.32+.68*t/drop
                snd+=noise*.055*(t/drop)**3
        fx=0
        if mode!='testimonial':
            cues=starts if mode=='ad' else [0,2.4,6.4,9.6,12.8,16,19.2]
            for mark in cues:
                dt=t-mark
                if 0<=dt<.5:fx+=.36*math.exp(-dt*16)*math.sin(math.tau*(51*dt+3*(1-math.exp(-dt*20))))
                if -.22<dt<0:fx+=noise*.1*((dt+.22)/.22)**2
            if mode=='launch' and drop-.6<t<drop:fx+=noise*.13*((t-drop+.6)/.6)**2
        fade=min(1,t/.2,max(0,(total-t)/.7))
        for ch in (0,1):
            stereo=snd+.009*math.sin(math.tau*523.25*t+ch*.6)*math.exp(-r*8)
            music.append(round(max(-.95,min(.95,stereo*fade))*32767));effects.append(round(max(-.95,min(.95,fx*fade))*32767))
    for name,data in [('music.wav',music),('sfx.wav',effects)]:
        with wave.open(str(directory/name),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(data.tobytes())
    write(directory/'music-source.json',{'type':'original authored procedural score','bpm':video['bpm'],'duration':total,'mode':mode,'drop':drop if mode=='launch' else None,'copyright':'Original production for this campaign','mock':False})

def validate_campaign(campaign):
    if campaign.get('brand')!='Blender':raise ValueError('These three art directions are Blender-specific')
    if not campaign.get('sources'):raise ValueError('A public-product campaign requires evidence sources')
    for kind,video in campaign['videos'].items():
        if video.get('language')!='zh':raise ValueError('This production template expects Chinese narration')
        for segment in video['segments']:
            if not segment['text'].strip() or any(c in segment['text'] for c in '<>|') or '@{' in segment['text']:
                raise ValueError('Speech must be plain text, without reserved SVML markup')
        if kind!='ad':
            end=0
            for segment in video['segments']:
                if not all(math.isfinite(segment[k]) for k in ['start','end']) or segment['start']<end-1e-6 or segment['end']<=segment['start'] or segment['end']>video['duration']:
                    raise ValueError('Score windows must be finite, non-overlapping, within the program')
                end=segment['end']
        if kind=='launch' and abs(video['drop']*video['bpm']/60-round(video['drop']*video['bpm']/60))>1e-6:
            raise ValueError('Reveal must land on the authored score beat')
        if kind=='testimonial':
            for key in ['quote','translation','author','role','company','quote_date']:
                if not video.get(key):raise ValueError('Real testimonial requires quote and dated attribution')
            if 'rating' in video and not video.get('rating_source'):raise ValueError('Do not fabricate a star rating')

def validate_bindings(video,bindings):
    for segment in video['segments']:
        meta=json.loads(Path(bindings[segment['id']]).with_suffix('.json').read_text())
        if meta.get('spoken_text')!=segment['text'] or meta.get('voice_preset')!=video['voice']:
            raise ValueError('Prepared speech differs from the current source; prepare again')


def audio_artifact(result,segment):
    # Explicit candidates prune producers; their accepted facts live in Result.outputs.
    key='voice-'+segment+'.audio'
    if key in result.get('outputs',{}):return result['outputs'][key]
    return result['tasks']['voice-'+segment]['outputs']['audio']


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('campaign',type=Path);ap.add_argument('work',type=Path);ap.add_argument('--video',choices=['ad','launch','testimonial'],required=True);ap.add_argument('--env-file',type=Path,default=None);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--reuse-preparation',type=Path);ap.add_argument('--reuse-render',type=Path);ap.add_argument('--render-only',action='store_true');a=ap.parse_args()
    campaign=json.loads(a.campaign.read_text());validate_campaign(campaign);video=campaign['videos'][a.video];d=a.work.resolve();d.mkdir(parents=True,exist_ok=True);env=dict(os.environ)
    if a.env_file:env['CAV_ENV_FILE']=str(a.env_file.resolve())
    vid='blender_'+a.video;segments=video['segments']
    if not a.render_only:
        if any(any(c in s['text'] for c in '<>|') or '@{' in s['text'] for s in segments):raise ValueError('Reserved SVML tokens in speech')
        (d/'script.svml').write_text('<script id="'+vid+'">\n'+''.join(f'  <{s["id"]}><HOST>{s["text"]}</{s["id"]}>\n' for s in segments)+'</script>\n')
        ast=M.engine(['script',d/'script.svml','--json'],d,'speech-check',env);doc=json.loads(ast)
        if [s['spoken_text'] for s in doc['segments']]!=[s['text'] for s in segments]:raise ValueError('Native speech AST differs from source')
        project=layout(video,vid);write(d/'layout.json',project)
        tasks=[{'id':'voice-'+s['id'],'action':{'producer':'voice','voice':video['voice'],'language':video['language'],'direction':'自然、有感染力的中文广告旁白，清晰克制，不要添加原文之外的任何内容，不要背景音乐。'},'inputs':{'script':{'kind':'script','path':'script.svml','view':'speech','segment':s['id']}}} for s in segments]
        voices={'voice:'+s['id']:output('voice-'+s['id']+'.audio') for s in segments}
        tasks.append({'id':'align','action':{'producer':'realign','fps':FPS,'gap':0},'inputs':{'script':{'kind':'script','path':'script.svml','view':'speech'},'layout':file('layout.json','project'),**voices}})
        write(d/'voices.author.json',{'format':'clone-any-video.author@1','tasks':tasks,'outputs':{}})
        targets=['align.project'] if a.video=='ad' else ['voice-'+s['id']+'.audio' for s in segments]
        run={'format':'clone-any-video.run@1','author':'voices.author.json','targets':targets}
        if a.reuse_preparation:
            run['reuse']=str(a.reuse_preparation.resolve())
            old=json.loads(a.reuse_preparation.read_text());candidates={};satisfy={}
            if old.get('mock'):raise ValueError('Cannot reuse mock speech')
            for seg in segments:
                artifact=old.get('outputs',{}).get('voice-'+seg['id']+'.audio') or old.get('tasks',{}).get('voice-'+seg['id'],{}).get('outputs',{}).get('audio')
                if artifact:
                    meta=json.loads(Path(artifact['path']).with_suffix('.json').read_text())
                    if artifact['mode']=='production' and meta.get('spoken_text')==seg['text'] and meta.get('voice_preset')==video['voice']:
                        name='accepted-'+seg['id'];candidates[name]={'kind':'result','result':str(a.reuse_preparation.resolve()),'output':'voice-'+seg['id']+'.audio'};satisfy['voice-'+seg['id']+'.audio']=name
            if candidates:run.update(candidates=candidates,satisfy=satisfy)
        write(d/'prepare.run.json',run)
        print(a.video,'real TTS preparation',flush=True)
        prep_path,prep=M.build(d/'prepare.run.json',d,'prepare',env)
        if prep.get('mock'):raise ValueError('Mock Result rejected')
        bindings={s['id']:audio_artifact(prep,s['id'])['path'] for s in segments}
        if a.video=='ad':
            project=json.loads(Path(prep['tasks']['align']['outputs']['project']['path']).read_text());project['meta']['total_frames']+=round(video['tail']*FPS);project['meta']['total_seconds']=project['meta']['total_frames']/FPS
        else:
            # Sound-first fixed edit: check observed takes fit, never silently cut speech.
            for row,s in zip(project['tracks']['voice'],segments):
                artifact=audio_artifact(prep,s['id']);info=json.loads(Path(artifact['path']).with_suffix('.json').read_text());dur=info['duration_seconds']
                if dur>s['end']-s['start']-.05:
                    tempo=dur/(s['end']-s['start']-.08)
                    if tempo>1.35:raise ValueError(f'Take {s["id"]} needs more than 35% retiming; revise narration')
                    timed=d/('voice-'+s['id']+'-timed.wav')
                    M.engine(['media','prepare-audio','--input',artifact['path'],'--output',timed,'--tempo',str(tempo)],d,'retime-'+s['id'],env)
                    dur=json.loads(timed.with_suffix('.json').read_text())['duration_seconds'];bindings[s['id']]=str(timed)
                if dur>s['end']-s['start']:raise ValueError('Measured retimed take still exceeds window')
                row['end_seconds']=row['start_seconds']+dur;row['end_frame']=math.ceil(row['end_seconds']*FPS);row['payload']['timing_status']='measured'
        n=project['meta']['total_frames'];duration=project['meta']['total_seconds']
        project['shots']=[{'id':'master','segment_id':segments[0]['id'],'shot_index':1,'start_seconds':0,'end_seconds':duration,'start_frame':0,'end_frame':n,'duration_seconds':duration,'visual_type':'GeneratedVideo','description':'Continuous '+a.video+' master','prompt_hint':''}]
        project['tracks']['visual_bg']=[];project['tracks']['visual_components']=[];project['tracks']['sfx']=[{'id':'design','name':'Score-locked accents','start_seconds':0,'end_seconds':duration,'start_frame':0,'end_frame':n,'payload':{'gain':.6}}]
        write(d/'voice-bindings.json',bindings)
        write(d/'project.json',project);write(d/'preparation.json',{'result':str(prep_path)})
    else:
        prep_path=Path(json.loads((d/'preparation.json').read_text())['result']);prep=json.loads(prep_path.read_text());project=json.loads((d/'project.json').read_text())
    config={'mode':a.video,'fps':FPS,'frames':project['meta']['total_frames'],'duration':project['meta']['total_seconds'],'segments':[],'video':{k:v for k,v in video.items() if k!='master_lufs'}}
    for i,s in enumerate(segments):
        v=project['tracks']['voice'][i];start=v['start_frame'];end=v['end_frame']
        if a.video!='ad':start=round(s['start']*FPS);end=round(s['end']*FPS)
        if i==len(segments)-1 and a.video=='ad':end=config['frames']
        config['segments'].append({'id':s['id'],'start':start,'end':end,'text':s['text']})
    template=(ROOT/'templates/blender-campaign'/f'{a.video}.html').read_text()
    html=template.replace('__COMMON__',(ROOT/'templates/blender-campaign/common.js').read_text()).replace('__CONFIG__',json.dumps(config,ensure_ascii=False).replace('<','\\u003c'))
    (d/'program.html').write_text(html)
    if a.prepare_only:print('prepared',d/'program.html',flush=True);return
    make_audio(video,project,d,a.video)
    for name in ['music.wav','sfx.wav']:M.engine(['admit-media','--asset',d/name],d,'admit-'+name,env)
    bindings=json.loads((d/'voice-bindings.json').read_text());validate_bindings(video,bindings)
    voice_inputs={'voice:'+s['id']:file(bindings[s['id']],'audio') for s in segments}
    duck={'lead_margin_seconds':.08,'tail_margin_seconds':.18,'ramp_duration_seconds':.1,'ducked_gain':.3 if a.video!='testimonial' else .45,'normal_gain':.65}
    author={'format':'clone-any-video.author@1','tasks':[
      {'id':'program','action':{'producer':'render-html','frames':config['frames'],'config':{'width':1080,'height':1920,'fps':FPS,'crf':17,'preset':'fast','transparent':False,'timeout_seconds':30}},'inputs':{'html':file('program.html','html')}},
      {'id':'mix','action':{'producer':'mix','ducking':duck},'inputs':{'script':{'kind':'script','path':'script.svml','view':'speech'},'project':file('project.json','project'),**voice_inputs,'bgm':file('music.wav','audio'),'sfx:design':file('sfx.wav','audio')}},
      {'id':'compose','action':{'producer':'compose'},'inputs':{'project':file('project.json','project'),'audio':output('mix.audio'),'background:master':output('program.video')}},
      {'id':'review','action':{'producer':'review'},'inputs':{'project':output('compose.project'),'video':output('compose.video')}}],
      'outputs':{'final.video':{'task':'compose','port':'video'},'final.review':{'task':'review','port':'report'}}}
    write(d/'author.json',author)
    render_run={'format':'clone-any-video.run@1','author':'author.json','targets':['program.video','mix.audio']}
    if a.reuse_render:render_run['reuse']=str(a.reuse_render.resolve())
    write(d/'render.run.json',render_run)
    print(a.video,'Chrome render + native mix',flush=True);render_path,render=M.build(d/'render.run.json',d,'render',env)
    M.engine(['media','prepare-audio','--input',render['tasks']['mix']['outputs']['audio']['path'],'--output',d/'master.wav','--target-lufs',str(video.get('master_lufs',-16)),'--max-true-peak','-1'],d,'master',env)
    write(d/'final.run.json',{'format':'clone-any-video.run@1','author':'author.json','targets':['final.video','final.review'],'reuse':str(render_path),'candidates':{'master':{'kind':'file','path':'master.wav','type':'audio'}},'satisfy':{'mix.audio':'master'}})
    a.output.resolve().parent.mkdir(exist_ok=True,parents=True);final_path,final=M.build(d/'final.run.json',d,'final',env,a.output.resolve())
    review=json.loads(Path(final['tasks']['review']['outputs']['report']['path']).read_text());write(d/'review.json',review)
    write(d/'delivery.json',{'result':str(final_path),'video':str(a.output.resolve()),'review':str(d/'review.json'),'passed':review['passed'],'mode':review['mode'],'voice_request_text_verified':True})
    print(a.video,'done',a.output.resolve(),flush=True)
if __name__=='__main__':main()
