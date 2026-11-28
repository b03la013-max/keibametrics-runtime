"""Visual race card (PNG) for the delivery mail (Owner 2026-11-25 10:43 JST: 正式もペーパーも見ている、
デザインを良くして). One image per delivered edition, drawn from the frozen record that is already delivered
(no new judgement here): race header, marks, the horses with their roles, and the ticket summary.
Pure Pillow, fonts from the machine (Hiragino on the Owner's Mac, Noto CJK elsewhere).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1080
PAD = 48
FONTS = [
    '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc', '/Library/Fonts/Arial Unicode.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc',
]
FRAME = {1: ('#ffffff', '#222222'), 2: ('#222222', '#ffffff'), 3: ('#e53935', '#ffffff'), 4: ('#1e5bd8', '#ffffff'),
         5: ('#f6d31f', '#222222'), 6: ('#2e9e4f', '#ffffff'), 7: ('#f08a24', '#ffffff'), 8: ('#f48fb1', '#222222')}
ROLE = {'1着候補': ('#f2b705', '#3b2c00'), '2着候補': ('#4c8bf5', '#ffffff'), '3着候補': ('#c9ced6', '#2b2f36'),
        'W': ('#f2b705', '#3b2c00'), 'P2': ('#4c8bf5', '#ffffff'), 'P3': ('#c9ced6', '#2b2f36')}
PALETTE = {   # Owner 2026-11-25 15:56: 地方=茶（ダート）、中央=緑（芝）、ばんえい=黄（重し）
    'LOCAL': {'FORMAL': ('#4a3020', '#c8925a'), 'PAPER': ('#6b4a32', '#e0b98c'), 'ink': '#ffffff', 'sub': '#ecdccb'},
    'JRA': {'FORMAL': ('#0f3d2e', '#36b37e'), 'PAPER': ('#1f5240', '#8fd1ae'), 'ink': '#ffffff', 'sub': '#dfe7e2'},
    'BAN': {'FORMAL': ('#e0a800', '#7a5a00'), 'PAPER': ('#f2c94c', '#9a7608'), 'ink': '#2a2000', 'sub': '#4a3c00'},
}
LABEL = {'FORMAL': '正式 Signed FINAL', 'PAPER': 'PAPER（研究）'}


def _theme(card):
    pal = PALETTE.get(card.get('system', 'LOCAL'), PALETTE['LOCAL'])
    kind = card.get('kind', 'PAPER')
    band, accent = pal[kind]
    return {'band': band, 'accent': accent, 'label': LABEL[kind], 'ink': pal['ink'], 'sub': pal['sub'],
            'badge_ink': '#ffffff' if pal['ink'] != '#ffffff' else '#1d140c'}


BG, INK, SUB, LINE = '#f6f7f4', '#1d2420', '#5f6a64', '#dde2de'


def _font(size, bold=True):
    for p in (FONTS if bold else FONTS[1:] + FONTS[:1]):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    raise OSError('NO_CJK_FONT')   # no Japanese font: the mail goes out without the image


def _frame_of(no, field):
    """Frame (枠) from the horse number when the record has none (NAR rule: 8 frames, doubled from the back)."""
    if field <= 8:
        return no
    extra = field - 8
    singles = 8 - extra
    return no if no <= singles else singles + (no - singles + 1) // 2


def render(card, out_path):
    """card = {kind: FORMAL|PAPER, title, post, cutoff, cond, edition, marks: [(mark,no)], horses: [{no,name,mark,
    role,frame?,pct?}], tickets: [(券種, 点数)], invest, note}"""
    th = _theme(card)
    horses = card.get('horses') or []
    tickets = card.get('tickets') or []
    rows = min(len(horses), 8)
    H = 300 + 96 + rows * 74 + 70 + 56 * max(1, len(tickets)) + 70 + 90
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    # header band
    d.rectangle([0, 0, W, 236], fill=th['band'])
    d.rectangle([0, 236, W, 244], fill=th['accent'])
    d.text((PAD, 34), card['title'], font=_font(64), fill=th['ink'])
    d.text((PAD, 122), f"{card.get('post', '')}発走" + (f"　締切 {card['cutoff']}" if card.get('cutoff') else ''), font=_font(36, False), fill=th['sub'])
    lab = th['label'] + (f"・{card['edition']}" if card.get('edition') else '')
    lf = _font(30)
    tw = d.textlength(lab, font=lf)
    d.rounded_rectangle([W - PAD - tw - 36, 40, W - PAD, 92], radius=26, fill=th['accent'])
    d.text((W - PAD - tw - 18, 49), lab, font=lf, fill=th['badge_ink'])
    d.text((PAD, 178), card.get('cond', ''), font=_font(30, False), fill=th['sub'])
    y = 270
    # marks row
    x = PAD
    if not card.get('marks'):
        y -= 86
    for mk, no in (card.get('marks') or [])[:8]:
        d.text((x, y), mk, font=_font(46), fill=INK)
        d.text((x + 50, y + 2), str(no), font=_font(44), fill=INK)
        x += 50 + d.textlength(str(no), font=_font(44)) + 34
    y += 86
    d.line([PAD, y, W - PAD, y], fill=LINE, width=3)
    y += 18
    field = max([h['no'] for h in horses] + [len(horses)] or [8])
    pmax = max([h.get('pct') or 0 for h in horses] + [1])
    for h in horses[:rows]:
        if card.get('frames', True):
            fr = h.get('frame') or _frame_of(h['no'], field)
            bg, fg = FRAME.get(fr, ('#999999', '#ffffff'))
        else:
            bg, fg = '#ffffff', INK
        d.text((PAD, y + 6), h.get('mark') or '', font=_font(40), fill=INK)
        d.rounded_rectangle([PAD + 56, y, PAD + 56 + 62, y + 58], radius=10, fill=bg, outline='#9aa39e', width=2)
        nf = _font(36)
        s = str(h['no'])
        d.text((PAD + 56 + 31 - d.textlength(s, font=nf) / 2, y + 8), s, font=nf, fill=fg)
        d.text((PAD + 140, y + 8), h.get('name', ''), font=_font(36), fill=INK)
        role = h.get('role') or ''
        if role in ROLE:
            rb, rf = ROLE[role]
            rfnt = _font(26)
            rw = d.textlength(role, font=rfnt)
            rx = W - PAD - rw - 28
            d.rounded_rectangle([rx, y + 10, W - PAD, y + 50], radius=20, fill=rb)
            d.text((rx + 14, y + 14), role, font=rfnt, fill=rf)
        if h.get('pct') is not None:
            bx, bw = PAD + 560, 220
            d.rounded_rectangle([bx, y + 22, bx + bw, y + 38], radius=8, fill=LINE)
            d.rounded_rectangle([bx, y + 22, bx + max(8, int(bw * h['pct'] / pmax)), y + 38], radius=8, fill=th['accent'])
            d.text((bx + bw + 12, y + 12), f"{h['pct']:.0f}%", font=_font(28, False), fill=SUB)
        y += 74
    y += 10
    d.line([PAD, y, W - PAD, y], fill=LINE, width=3)
    y += 24
    d.text((PAD, y), '買い目', font=_font(34), fill=INK)
    y += 56
    for k, pt in tickets:
        d.text((PAD + 10, y), k, font=_font(34, False), fill=INK)
        s = f'{pt}点'
        d.text((W - PAD - d.textlength(s, font=_font(34)), y), s, font=_font(34), fill=INK)
        y += 56
    d.line([PAD, y + 4, W - PAD, y + 4], fill=INK, width=2)
    tot = f"合計 {sum(p for _, p in tickets)}点　{card.get('invest', 0):,}円"
    d.text((W - PAD - d.textlength(tot, font=_font(38)), y + 18), tot, font=_font(38), fill=INK)
    d.text((PAD, H - 64), card.get('note', '推薦試算・1点100円・実購入なし／確率は未較正'), font=_font(24, False), fill=SUB)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, optimize=True)
    return out_path


BET_JA = {'TRIO': '三連複', 'TRIFECTA': '三連単', 'EXACTA': '馬単', 'QUINELLA': '馬連', 'WIDE': 'ワイド', 'WIN': '単勝', 'PLACE': '複勝'}
ROLE_JA = {'W': '1着候補', 'P2': '2着候補', 'P3': '3着候補'}


def paper_card(rev, title, post, cutoff, edition=''):
    p = rev['prediction']
    rc = p.get('race_cond') or {}
    horses = [{'no': r['no'], 'name': r.get('name', ''), 'mark': r.get('mark') or '', 'role': r.get('role') or '',
               'frame': r.get('frame'), 'pct': 100 * (r.get('p_win') or 0)} for r in p['ranking'] if r.get('role') not in (None, '×')]
    tickets = [(t['k'], int(t['pt'])) for t in p.get('tickets') or [] if t.get('pt')]
    cond = '　'.join(str(x) for x in (rc.get('distance') and f"{rc.get('distance')}m", rc.get('going'), rc.get('class')) if x)
    return {'kind': 'PAPER', 'title': title, 'post': post, 'cutoff': cutoff, 'edition': edition, 'cond': cond,
            'marks': [(r['mark'], r['no']) for r in p['ranking'] if r.get('mark')], 'horses': horses,
            'tickets': tickets, 'invest': 100 * sum(pt for _, pt in tickets),
            'note': 'PAPER・1点100円・実購入なし／勝率は未較正の暫定値'}


def formal_card(summary, names, title, post, cutoff, cond='', edition=''):
    marks = summary.get('marks') or {}
    roles = summary.get('roles') or {}
    rank = [int(x) for x in summary.get('ranking') or []]

    def role(h):
        r = roles.get(str(h)) or []
        return next((ROLE_JA[x] for x in ('W', 'P2', 'P3') if x in r), '')
    horses = [{'no': h, 'name': (names.get(h) or {}).get('name', ''), 'frame': (names.get(h) or {}).get('frame'),
               'mark': marks.get(str(h), '') if marks.get(str(h)) != '△' or role(h) else '', 'role': role(h)}
              for h in rank if role(h)]
    cnt = {}
    for t in summary.get('tickets') or []:
        k = BET_JA.get(t['bet_type'], t['bet_type'])
        cnt[k] = cnt.get(k, 0) + 1
    tickets = list(cnt.items())
    top = [(marks[str(h)], h) for h in rank if marks.get(str(h)) and marks[str(h)] != '△'][:3]
    top += [('△', h) for h in rank if marks.get(str(h)) == '△' and role(h)][:3]
    return {'kind': 'FORMAL', 'title': title, 'post': post, 'cutoff': cutoff, 'edition': edition, 'cond': cond,
            'marks': top, 'horses': horses, 'tickets': tickets, 'invest': 100 * sum(cnt.values()),
            'note': '推薦試算・1点100円・実購入なし／KRS 5,000回は未較正'}


def publish(png_path, repo_path, token, repo, branch='local-autopilot-data'):
    """Upload the PNG to the public data branch with one Contents API call (no git push from the delivery path)
    and return its raw URL for the mail. None on any failure (the mail is then sent without the image)."""
    import base64
    import json
    import urllib.request
    url = f'https://api.github.com/repos/{repo}/contents/{repo_path}'
    hdr = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'km-local-autopilot'}
    body = {'message': f'LOCAL mail card {repo_path.rsplit("/", 1)[-1]} [skip ci]', 'branch': branch,
            'content': base64.b64encode(Path(png_path).read_bytes()).decode()}
    try:   # an existing file (same name) needs its sha
        with urllib.request.urlopen(urllib.request.Request(url + f'?ref={branch}', headers=hdr), timeout=15) as r:
            body['sha'] = json.loads(r.read().decode())['sha']
    except Exception:
        pass
    try:
        req = urllib.request.Request(url, method='PUT', data=json.dumps(body).encode(),
                                     headers=dict(hdr, **{'Content-Type': 'application/json'}))
        with urllib.request.urlopen(req, timeout=20):
            pass
    except Exception:
        return None
    return f'https://raw.githubusercontent.com/{repo}/{branch}/{repo_path}'


def jra_card(final, envelope, edition=''):
    """中央版 Signed FINAL (runtime/final_artifacts/<race_id>.json) + its source envelope (names, frames, course).
    印 (Owner 2026-11-28 15:53「地方版と同じく予想印をつけるべき」): the same rule as 地方版 FORMAL
    (formal_rakuten): ◎○▲ to the first three of the signed Static ranking, △ to the rest; the card shows △
    only for role holders. Display only: taken from the frozen ranking, no new judgement."""
    art = (envelope or {}).get('artifact') or {}
    det = art.get('jra_official_race_card_detail') or {}
    ctx = det.get('race_context') or {}
    names = {int(r['horse_no']): {'name': r.get('horse_name', ''), 'frame': r.get('frame_no')}
             for r in det.get('runners') or [] if r.get('horse_no')}
    fp = final.get('final_prediction_package') or {}
    ft = final.get('final_ticket') or {}
    ranking = [str(x) for x in fp.get('ranking') or []]
    marks = {h: '◎' if i == 0 else '○' if i == 1 else '▲' if i == 2 else '△' for i, h in enumerate(ranking)}
    sm = {'marks': marks, 'roles': fp.get('roles') or {}, 'ranking': ranking, 'tickets': ft.get('tickets') or []}
    post = str(final.get('scheduled_post_at') or '')[11:16]
    cut = str(final.get('prediction_cutoff') or '')[11:16]
    title = f"{ctx.get('venue_name', '')}{ctx.get('race_no', '')}R"
    cond = '　'.join(str(x) for x in (ctx.get('surface') and ctx.get('distance_m') and f"{ctx['surface']}{ctx['distance_m']}m",
                                      ctx.get('going'), ctx.get('race_class')) if x)
    c = formal_card(sm, names, title, post, cut, cond, edition)
    c.update(system='JRA', invest=int(ft.get('total_investment') or c['invest']), note='推薦試算・実購入なし／確率は未較正')
    return c


def ban_card(rec, edition=''):
    """ばんえい v4.0-BAN record (output_ban/<day>/R<no>[.rev2].json)."""
    ev = rec.get('evaluation') or {}
    marks = ev.get('marks') or {}
    tk = rec.get('tickets') or {}
    hd = rec.get('header') or {}
    rows = sorted(ev.get('rows') or [], key=lambda r: r.get('win_rank') or 99)

    def role(r):
        if r.get('role_w') in ('STRONG', 'BUY', 'CONDITIONAL'):
            return '1着候補'
        if r.get('role_p2') == 'BUY':
            return '2着候補'
        if r.get('role_p3') == 'BUY':
            return '3着候補'
        return ''
    horses = [{'no': r['no'], 'name': r.get('name', ''), 'mark': marks.get(str(r['no']), ''), 'role': role(r)}
              for r in rows if role(r) or marks.get(str(r['no']))]
    order = ['◎', '○', '▲', '△', '穴']
    mk = sorted(((m, int(n)) for n, m in marks.items()), key=lambda x: (order.index(x[0]) if x[0] in order else 9, x[1]))
    tickets = [(k, len(tk.get(f) or [])) for k, f in (('三連複', 'trio'), ('三連単', 'exact')) if tk.get(f)]
    cond = '　'.join(x for x in (hd.get('race_name'), hd.get('going') and f"馬場水分 {hd['going']}") if x)
    post = str((rec.get('race') or {}).get('post') or '')[11:16]
    kind = 'FORMAL' if tk.get('formality', 'FORMAL') == 'FORMAL' else 'PAPER'
    return {'kind': kind, 'system': 'BAN', 'frames': False, 'title': f"帯広{hd.get('race_no') or (rec.get('race') or {}).get('no')}R",
            'post': post, 'cutoff': '', 'edition': edition, 'cond': cond, 'marks': mk, 'horses': horses,
            'tickets': tickets, 'invest': int(tk.get('stake') or 100 * sum(n for _, n in tickets)),
            'note': 'ばんえい v4.0-BAN・1点100円・実購入なし／確率・EVではありません'}


def card_line(card, repo_path, repo=None, token=None):
    """Draw + upload; returns a markdown image line or '' (never raises)."""
    import os
    import tempfile
    if os.environ.get('KM_LOCAL_MAIL_CARD', '1') == '0':
        return ''
    try:
        tmp = Path(tempfile.mkdtemp()) / repo_path.rsplit('/', 1)[-1]
        render(card, tmp)
        u = publish(tmp, repo_path, token or os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN'),
                    repo or os.environ.get('GITHUB_REPOSITORY') or 'b03la013-max/keibametrics-runtime')
        return f'![{card.get("title", "")}]({u})\n' if u else ''
    except Exception:
        return ''
