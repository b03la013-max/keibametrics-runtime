"""Authority-bound newcomer PAPER selection; established runners retain R50."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jra_aki_v21 import apply_authorized_v21 as established, materialize, select_columns
from jra_aki_v21_features import compile_features
from jra_aki_capital_preflight import sha, AKICapitalError

PROFILE = 'KM-JRA-NEWCOMER-AKI-PAPER-v1-20261012'
BASE = ('HPI','SSI','CFI','RFI','BVI','JTI','CSI','TRI','BWI','GCI','PRI','KGI','VMI')


def is_newcomer(request):
    rows = request.get('runners') or []
    return bool(rows) and all(all((r.get('canonical_components') or {}).get(k, {}).get('profile') == 'NEWCOMER'
                                 for k in BASE) for r in rows)


def _observed(component):
    # A transport/DCR neutral, unlabelled scalar or absent observation cannot
    # provide a second evidence channel. Numerical provenance remains upstream.
    return (component.get('information_status') != 'INFORMATION_INSUFFICIENT_DCR_ART3'
            and bool(component.get('components')) and all(
                c.get('feature_rule_id') and c.get('evidence_refs') and c.get('source_fact')
                for c in component['components']))


def apply_authorized_v21(request, source, authority, *, root):
    activation = (authority.get('family_scoped_authority', {}).get('JRA', {})
                  .get('newcomer_aki_paper_activation'))
    if not activation or not is_newcomer(request):
        return established(request, source, authority, root=root)
    root = Path(root).resolve()
    if (activation.get('profile') != PROFILE or activation.get('status') != 'OWNER_AUTHORIZED_UNVALIDATED'
            or activation.get('purchase_authority') is not False
            or activation.get('automatic_promotion') is not False
            or activation.get('runtime_sha256') != hashlib.sha256(Path(__file__).read_bytes()).hexdigest()):
        raise AKICapitalError('NEWCOMER_AKI_ACTIVATION_INVALID')
    path = (root / activation['policy_path']).resolve()
    if not path.is_relative_to(root):
        raise AKICapitalError('NEWCOMER_AKI_POLICY_PATH_INVALID')
    policy = json.loads(path.read_text())
    if sha(policy) != activation['policy_sha256'] or policy.get('profile') != PROFILE:
        raise AKICapitalError('NEWCOMER_AKI_POLICY_FINGERPRINT_MISMATCH')
    record = (root / activation['owner_authorization_record']).resolve()
    if (not record.is_relative_to(root) or hashlib.sha256(record.read_bytes()).hexdigest()
            != activation['owner_authorization_record_sha256']):
        raise AKICapitalError('NEWCOMER_AKI_OWNER_RECORD_INVALID')
    # This executes the existing trust/Full20/external/registry fingerprint gates.
    # Only the two known positive-selection stops are allowed to use this path.
    try:
        established(request, source, authority, root=root)
    except AKICapitalError as exc:
        if str(exc) not in {'AKI_EVIDENCE_SELECTED_COLUMN_EMPTY','AKI_SINGLE_HEAD_FORBIDDEN'}:
            raise
    core = authority['family_scoped_authority']['JRA']['aki_v21_activation']
    components = json.loads((root / core['components']['path']).read_text())
    columns = json.loads((root / core['columns']['path']).read_text())
    enriched = compile_features(request, source, components['feature_compiler_policy'])
    package, calculation = materialize(enriched, components, registry_hash=core['components']['sha256'])
    risk = (100 - calculation['axes']['ASI']) / 100
    by_id = {str(r['runner_id']): r['canonical_components'] for r in request['runners']}
    for rid, facts in enriched['aki_selection_features']['runners'].items():
        cc = by_id[rid]
        channels = []
        # CFI and BVI share pedigree observations: count them ONCE.
        if any(_observed(cc[k]) and cc[k]['value'] >= policy['pedigree_quality_floor'] for k in ('CFI','BVI')):
            channels.append('PEDIGREE')
        if any(_observed(cc[k]) for k in ('JTI','CSI')):
            channels.append('HUMAN_OFFICIAL_STATS')
        if _observed(cc['BWI']):
            channels.append('CURRENT_PHYSIQUE')
        eligible = 'PEDIGREE' in channels and len(channels) >= policy['minimum_observed_channels']
        for c, f in facts.items():
            raw = f['source_fact']
            g = raw['normalized_gap']
            limits = components['feature_compiler_policy']['column_gap'][c]
            maximum = limits['REVIEW'] + policy['axis_risk_gap_extension'] * risk
            qualified = eligible and raw['value'] >= policy['role_quality_floor']
            f['category'] = ('MAIN' if qualified and g <= limits['BASE'] else
                             'ALTERNATIVE' if qualified and g <= maximum else 'OTHER')
            raw.update(observed_channels=channels, observation_channel_count=len(channels),
                       support_group_count=len(channels), newcomer_review_gap=maximum,
                       support_semantics='OBSERVATION_CHANNELS / NOT_BET_POSITIVE_CONFIDENCE',
                       newcomer_policy_sha256=activation['policy_sha256'])
            f['derivation'] = PROFILE
    # Rebuild pair-local evidence from the NEW columns; never reuse the empty
    # established-race compatibility universe. Distinct runners are required.
    selection = enriched['aki_selection_features']
    potential = {c:[rid for rid,f in selection['runners'].items() if f[c]['category'] != 'OTHER']
                 for c in ('W','P2','P3')}
    def fact(raw):
        return {'status':'OBSERVED','category':'YES','observed_at':source['source_freeze_at'],
                'source_snapshot_sha256':source['source_snapshot_sha256'],
                'evidence_refs':['FULL20:'+sha(request['runners'])], 'source_fact':raw,
                'derivation':PROFILE,'dependency_sha256':sha(request['runners'])}
    selection['pairs'], selection['thirds'] = {}, {}
    for h in potential['W']:
        for s in potential['P2']:
            if h == s: continue
            selection['pairs'][h+'>'+s] = {'compatible':fact({'head':h,'second':s,'paper_model_roles':True})}
            for t in potential['P3']:
                if t in {h,s}: continue
                selection['thirds'][h+'>'+s+'>'+t] = {'compatible':fact({'head':h,'second':s,'third':t,'paper_model_roles':True})}
    out = select_columns(request, enriched, calculation, columns, registry_hash=core['columns']['sha256'])
    receipt = enriched['aki_compiler_receipt']
    receipt['feature_sha256'] = sha({'axes':enriched['aki_evidence_features'],'selection':selection})
    receipt['newcomer_policy_sha256'] = activation['policy_sha256']
    receipt['information_gate'] = {'status':'LIMITED','action':'PAPER',
        'reason':'NEWCOMER_ROLE_POLICY_UNVALIDATED / OBSERVED_CHANNELS_NOT_BET_CONFIDENCE',
        'source_snapshot_sha256':source['source_snapshot_sha256']}
    out.update(official_aki_package=package,
               official_aki_verification={'status':'PASS','profile':PROFILE,'calculation':calculation,
                                         'activation_sha256':sha(activation)},
               aki_compiler_receipt=receipt, aki_information_gate=receipt['information_gate'],
               aki_calculation_requirement='OFFICIAL_V2_1')
    out['aki_column_selection']['newcomer_policy'] = PROFILE
    out['aki_column_selection']['purchase_authority'] = False
    out['aki_column_selection']['sha256'] = sha({k:v for k,v in out['aki_column_selection'].items() if k != 'sha256'})
    for name in ('role_registry','pair_dispositions','third_dispositions'):
        for row in out[name]:
            row.update(authority=PROFILE,production_authority=True,
                       evidence_scope='MODEL_ROLE_FOR_PAPER / NOT_POSITIVE_PURCHASE_EVIDENCE')
    return out
