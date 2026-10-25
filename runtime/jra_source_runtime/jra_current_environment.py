"""Bind a new SOURCE's current environment to its already captured official card.

Only new acquisition opts in. Old signed SOURCEs keep their original context;
no second fetch, prediction, signing or retrospective OOS is performed here.
"""
import base64
import gzip
import hashlib
import io

try:
    from .source_acquisition import sha_obj
    from .jra_race_card_detail import parse_race_card_detail
    from .jra_market_observation import _ts,official_observation
except ImportError:
    from source_acquisition import sha_obj
    from jra_race_card_detail import parse_race_card_detail
    from jra_market_observation import _ts,official_observation

PROFILE='KM-JRA-CURRENT-ENVIRONMENT-BINDING-v1'
FIELD='jra_current_environment_binding'
IDENTITY=('race_date','venue_id','race_no','surface','distance_m','race_class','scheduled_post_at',
          'meeting_no','meeting_day','course_variant','weight_rule')


def resolve_current_environment(artifact, primary):
    binding=artifact.get(FIELD) or {}
    if binding.get('profile')!=PROFILE or binding.get('sha256')!=sha_obj({k:v for k,v in binding.items() if k!='sha256'}):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_BINDING_HASH_INVALID')
    if binding.get('primary_context_sha256')!=primary.get('sha256'):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_PRIMARY_CONTEXT_MISMATCH')
    series=artifact.get('aki_external_observations') or []
    if len(series)!=2 or artifact.get('aki_external_observation_status',{}).get('status')!='PASS':
        raise ValueError('JRA_CURRENT_ENVIRONMENT_ORDERED_SERIES_REQUIRED')
    if artifact.get('aki_external_observations_sha256')!=sha_obj(series):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_SERIES_HASH_INVALID')
    first,last=series
    refs=last.get('evidence_refs') or []
    matches=[s for s in artifact.get('sources') or [] if
        s.get('source_id')=='JRA-OFFICIAL-RACE-CARD-DETAIL-REOBSERVATION' and
        'SOURCE-SNAPSHOT:'+str(s.get('snapshot_sha256')) in refs]
    if len(matches)!=1:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_SNAPSHOT_AMBIGUOUS')
    snapshot=matches[0]
    if (snapshot.get('snapshot_sha256')!=binding.get('source_snapshot_sha256') or
            snapshot.get('raw_sha256')!=binding.get('raw_sha256')):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_SNAPSHOT_BINDING_MISMATCH')
    with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(snapshot['raw_gzip_b64'],validate=True))) as stream:
        raw=stream.read(6000001)
    if len(raw)>6000000 or hashlib.sha256(raw).hexdigest()!=snapshot.get('raw_sha256'):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_RAW_HASH_INVALID')
    current=parse_race_card_detail(raw,snapshot.get('content_type',''))
    observed=current.get('race_context') or {}
    if any(observed.get(k)!=primary.get(k) for k in IDENTITY):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_RACE_IDENTITY_CONFLICT')
    active={str(r['runner_id']):str(r.get('canonical_name') or r.get('name') or '').replace(' ','')
            for r in artifact['jra_official_runner_universe']['runners'] if r.get('status','ACTIVE')=='ACTIVE'}
    rows={str(r['runner_id']):str(r.get('horse_name') or '').replace(' ','')
          for r in current['runners'] if r.get('status')=='ACTIVE'}
    if rows!=active:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_ACTIVE_IDENTITIES_CONFLICT')
    replay,reason=official_observation(current,snapshot,set(active))
    if replay!=last:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_OBSERVATION_REPLAY_MISMATCH:'+str(reason))
    primary_detail=artifact.get('jra_official_race_card_detail') or {}
    primary_snaps=[s for s in artifact.get('sources') or [] if
        s.get('source_id')=='JRA-OFFICIAL-RACE-CARD-DETAIL' and
        s.get('snapshot_sha256')==primary_detail.get('source_snapshot_sha256')]
    if len(primary_snaps)!=1 or official_observation(primary_detail,primary_snaps[0],set(active))[0]!=first:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_FIRST_OBSERVATION_MISMATCH')
    cutoff=_ts(artifact.get('prediction_cutoff') or binding['prediction_cutoff'])
    if (not _ts(first['observed_at'])<_ts(last['observed_at'])<=cutoff or
            _ts(last['observed_at'])!=_ts(snapshot['fetched_at']) or
            binding.get('observed_at')!=last['observed_at']):
        raise ValueError('JRA_CURRENT_ENVIRONMENT_TIME_INVALID')
    if _ts(binding['prediction_cutoff'])!=cutoff:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_CUTOFF_MISMATCH')
    # Keep the primary card and both raw pages. Only the context derived from
    # the later same-race official page changes before this new SOURCE freezes.
    context={**observed,'context_source':'JRA_OFFICIAL_DETAILED_CARD',
        'context_source_kind':'OFFICIAL_REOBSERVATION',
        'context_source_snapshot_sha256':snapshot['snapshot_sha256'],
        'context_source_raw_sha256':snapshot['raw_sha256'],
        'context_observed_at':snapshot['fetched_at'],
        'previous_context_sha256':primary['sha256']}
    context['sha256']=sha_obj(context)
    return context


def bind_latest_environment(artifact, prediction_cutoff):
    """New-acquisition-only opt in; return input unchanged if no full series."""
    if artifact.get('aki_external_observation_status',{}).get('status')!='PASS':
        return artifact
    try:
        from .jra_observed_context import resolve_primary_observed_context
    except ImportError:
        from jra_observed_context import resolve_primary_observed_context
    primary=resolve_primary_observed_context(artifact)
    series=artifact.get('aki_external_observations') or []
    if len(series)!=2:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_ORDERED_SERIES_REQUIRED')
    last=series[-1]
    refs=last.get('evidence_refs') or []
    matches=[s for s in artifact.get('sources') or [] if
        'SOURCE-SNAPSHOT:'+str(s.get('snapshot_sha256')) in refs]
    if len(matches)!=1:
        raise ValueError('JRA_CURRENT_ENVIRONMENT_SNAPSHOT_AMBIGUOUS')
    snapshot=matches[0]
    binding={'profile':PROFILE,'source_snapshot_sha256':snapshot['snapshot_sha256'],
        'raw_sha256':snapshot['raw_sha256'],'observed_at':last['observed_at'],
        'prediction_cutoff':prediction_cutoff,'primary_context_sha256':primary.get('sha256')}
    binding['sha256']=sha_obj(binding)
    prospective={**artifact,FIELD:binding}
    context=resolve_current_environment(prospective,primary)
    # Do not partially mutate acquisition on failed identity/time/raw checks.
    artifact[FIELD]=binding
    artifact['jra_race_context']=context
    artifact['jra_race_context_sha256']=sha_obj(context)
    artifact['jra_current_environment_reconciliation']={
        'status':'LATEST_OFFICIAL_PRE_FREEZE_CONTEXT',
        'primary_context_sha256':primary.get('sha256'),'current_context_sha256':context['sha256'],
        'changes':{k:{'previous':primary.get(k),'current':context.get(k)} for k in ('going','weather')
                   if primary.get(k)!=context.get(k)}}
    return artifact
