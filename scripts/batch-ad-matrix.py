#!/usr/bin/env python3
"""Compile an ad CSV into complete native clone-any-video production graphs."""
import argparse
import csv
import json
import re
from html import escape
from pathlib import Path

ASPECT_SPECS = {
    '9:16': (1080, 1920), '4:5': (1080, 1350),
    '1:1': (1080, 1080), '16:9': (1920, 1080),
}
SEGMENTS = ('hook', 'context', 'payoff', 'proof', 'outro')
LABELS = ('YOUR TIME MATTERS', 'THE PROBLEM', 'THE SOLUTION', 'THE RESULT', 'START TODAY')
FPS = 30


def script_input(vid, segment=None):
    value = {'kind': 'script', 'path': f'{vid}.svml', 'view': 'speech'}
    if segment:
        value['segment'] = segment
    return value


def output(name):
    return {'kind': 'output', 'output': name}


def file_input(path, kind):
    return {'kind': 'file', 'path': path, 'type': kind}


def texts(row):
    return [row[k] for k in ('hook', 'context', 'payoff', 'proof', 'cta')]


def generate_svml(row):
    parts = [f'<script id="{escape(row["id"], quote=True)}">']
    for segment, text in zip(SEGMENTS, texts(row)):
        parts.append(f'  <{segment}><HOST>{text}</{segment}>')
    return '\n'.join(parts + ['</script>', ''])


def generate_component_html(title, subtitle, accent, bg, aspect_key, cta=False):
    w, h = ASPECT_SPECS[aspect_key]
    # Intersection of the centered square and a conservative bottom keep-clear area.
    size = min(w, h)
    safe_h = min(size * .82, h - (480 if aspect_key == '9:16' else 120))
    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ width:{w}px; height:{h}px; overflow:hidden; background:{bg}; color:#f8fafc;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; display:grid; place-items:center }}
.card {{ width:{size * .82}px; height:{safe_h}px; padding:{size * .045}px; border:2px solid {accent};
border-radius:32px; display:flex; flex-direction:column; justify-content:center; gap:32px;
background:linear-gradient(145deg,#172339,#0b1220); box-shadow:0 24px 80px #0008; text-align:center }}
p {{ color:{accent}; font-size:{size * .024}px; letter-spacing:4px; font-weight:700 }}
h1 {{ font-size:{size * .058}px; line-height:1.14; overflow-wrap:anywhere }}
.bar {{ height:6px; width:100%; background:{accent}; transform-origin:left }}
.button {{ display:{'block' if cta else 'none'}; border-radius:18px; padding:22px; background:{accent};
color:#07101f; font-size:{size * .032}px; font-weight:800 }}
</style></head><body><main class="card"><p>{escape(subtitle)}</p><h1>{escape(title)}</h1>
<div class="bar"></div><div class="button">14-DAY FREE TRIAL →</div></main>
<script>
// Capture seeks frames directly; no wall-clock timers, network fonts or dependencies.
window.renderFrame = function(frame, progress) {{
 const t=Math.max(0,Math.min(1,frame/20)); const e=1-Math.pow(1-t,3);
 const card=document.querySelector('.card');
 card.style.opacity=0.15+0.85*e; card.style.transform=`translateY(${{(1-e)*48}}px) scale(${{.96+.04*e}})`;
 document.querySelector('.bar').style.transform=`scaleX(${{e}})`;
}};
window.renderFrame(29,1);
</script></body></html>'''


def generate_layout(row, aspect):
    w, h = ASPECT_SPECS[aspect]
    project = {'format': 'clone-any-video.project@1',
        'meta': {'id': row['id'], 'title': row['id'], 'width': w, 'height': h,
                 'fps': FPS, 'total_seconds': 25, 'total_frames': 750},
        'shots': [], 'tracks': {k: [] for k in ('visual_bg', 'visual_components', 'captions', 'voice', 'bgm', 'sfx')},
        'asset_tasks': []}
    for i, (segment, text) in enumerate(zip(SEGMENTS, texts(row))):
        window = {'start_seconds': i*5, 'end_seconds': (i+1)*5,
                  'start_frame': i*150, 'end_frame': (i+1)*150}
        project['shots'].append(dict(window, id=f'shot_{segment}', segment_id=segment,
            shot_index=i+1, duration_seconds=5, visual_type='GeneratedVideo',
            description=f'Animated {segment} card', prompt_hint=''))
        project['tracks']['voice'].append(dict(window, id=f'voice_{segment}', name=segment,
            payload={'spoken_text': text, 'timing_status': 'estimated', 'turns_count': 1}))
        project['tracks']['visual_bg'].append(dict(window, id=f'bg_shot_{segment}', name=segment,
            payload={'shot_id': f'shot_{segment}', 'sampling': {'shortage': 'hold'}}))
    return project


def generate_author_dag(row, out_dir, aspect_key, voice="alloy"):
    vid = row['id']
    w, h = ASPECT_SPECS[aspect_key]
    tasks = []
    voices = {f'voice:{s}': output(f'voice-{s}.audio') for s in SEGMENTS}
    for segment in SEGMENTS:
        tasks.append({'id': f'voice-{segment}', 'action': {'producer': 'voice', 'voice': voice, 'language': 'en'},
                      'inputs': {'script': script_input(vid, segment)}})
    tasks += [
        {'id': 'align', 'action': {'producer': 'realign', 'fps': FPS, 'gap': 0},
         'inputs': {'script': script_input(vid), 'layout': file_input('layout.json', 'project'), **voices}},
        {'id': 'mix', 'action': {'producer': 'mix'},
         'inputs': {'script': script_input(vid), 'project': output('align.project'), **voices}},
    ]
    for segment in SEGMENTS:
        tasks.append({'id': f'card-{segment}', 'action': {'producer': 'render-html', 'frames': FPS,
            'config': {'width': w, 'height': h, 'fps': FPS, 'crf': 20, 'preset': 'fast',
                       'transparent': False, 'timeout_seconds': 30}},
            'inputs': {'html': file_input(f'{segment}_card.html', 'html')}})
    tasks += [
        {'id': 'compose', 'action': {'producer': 'compose'},
         'inputs': {'project': output('align.project'), 'audio': output('mix.audio'),
                    **{f'background:shot_{s}': output(f'card-{s}.video') for s in SEGMENTS}}},
        {'id': 'review', 'action': {'producer': 'review'},
         'inputs': {'project': output('compose.project'), 'video': output('compose.video')}},
    ]
    return {'format': 'clone-any-video.author@1', 'tasks': tasks,
            'outputs': {'final.video': {'task': 'compose', 'port': 'video'},
                        'final.review': {'task': 'review', 'port': 'report'}}}


def generate_run_manifest(vid):
    return {'format': 'clone-any-video.run@1', 'author': f'{vid}.author.json',
            'targets': ['final.video', 'final.review']}


def load_rows(csv_path, test_field=None):
    with csv_path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError('CSV requires unique column names')
        rows = list(reader)
    if not rows:
        raise ValueError('CSV contains no variants')
    seen = set()
    for index, row in enumerate(rows, 1):
        if None in row:
            raise ValueError(f'Row {index}: too many columns')
        for key in ('id', 'hook', 'context', 'payoff', 'proof', 'cta'):
            if not (row.get(key) or '').strip():
                raise ValueError(f'Row {index}: missing {key}')
            row[key] = row[key].strip()
            if key != 'id' and any(token in row[key] for token in ('<', '>', '|', '@{')):
                raise ValueError(f'Row {index}: {key} contains reserved SVML markup; provide plain speech text')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', row['id']) or row['id'] in seen:
            raise ValueError(f'Row {index}: unsafe or duplicate id {row["id"]!r}')
        seen.add(row['id'])
        row['accent'] = (row.get('accent') or '#38bdf8').strip()
        row['bg'] = (row.get('bg') or '#0f172a').strip()
        for key in ('accent', 'bg'):
            if not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?|rgba?\([0-9.,%\s]+\)', row[key]):
                raise ValueError(f'Row {index}: invalid CSS color {key}')
    if test_field:
        fixed = {'hook', 'context', 'payoff', 'proof', 'cta', 'accent', 'bg'} - {test_field}
        for row in rows[1:]:
            changed = sorted(k for k in fixed if row[k] != rows[0][k])
            if changed:
                raise ValueError(f'{row["id"]}: --test-field {test_field} requires fixed {", ".join(changed)}')
    return rows


def compile_variant(row, directory, aspect, voice="alloy"):
    directory.mkdir(parents=True, exist_ok=True)
    vid = row['id']
    (directory / f'{vid}.svml').write_text(generate_svml(row), encoding='utf-8')
    for segment, label, text in zip(SEGMENTS, LABELS, texts(row)):
        (directory / f'{segment}_card.html').write_text(generate_component_html(
            text, label, row['accent'], row['bg'], aspect, segment == 'outro'), encoding='utf-8')
    for name, data in [('layout.json', generate_layout(row, aspect)),
                       (f'{vid}.author.json', generate_author_dag(row, directory, aspect, voice)),
                       (f'{vid}.run.json', generate_run_manifest(vid))]:
        (directory / name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--aspect', choices=ASPECT_SPECS, default='9:16')
    parser.add_argument('--test-field', choices=('hook', 'context', 'payoff', 'proof', 'cta'),
                        help='Reject changes to other creative fields; id may always differ')
    parser.add_argument('--voice', default='alloy', help='Provider-specific preset, e.g. alloy (OpenAI) or 冰糖 (MiMo)')
    args = parser.parse_args()
    try:
        rows = load_rows(args.csv_file, args.test_field)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    for row in rows:
        compile_variant(row, args.output_dir / row['id'], args.aspect, args.voice)
        print(f'Generated {row["id"]}: 5 voices, measured timeline, 5 animated cards, mix, compose, review')
    print(f'Compiled {len(rows)} variants to {args.output_dir.resolve()}')


if __name__ == '__main__':
    main()
