"""Pure JRA source identity binding, independent of service boot configuration."""

def bind_source_identity(artifact, race_id, ctx):
    artifact['family_id'] = 'JRA'
    artifact['race_id'] = str(race_id)
    artifact['source_race_context'] = dict(ctx)
    return artifact
