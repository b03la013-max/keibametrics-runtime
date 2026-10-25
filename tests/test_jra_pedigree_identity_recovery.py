"""Real stored Raw plus adversarial identity/provenance/time boundaries."""
import base64,copy,gzip,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'runtime'),str(ROOT/'runtime/jra_source_runtime')]
from jra_pedigree_identity_recovery import profile,locator,recover,reverify_oidc,verify_recovery_bindings,sha_obj,digest_bytes,_decode
from jra_horse_history import parse_horse_history


def fixture():
 q=json.loads((ROOT/'runtime/requests/KM-JRA-TKY-20261018-R10-LIVE-R1-FORMAL.json').read_text())
 snap=next(x for x in q['source_snapshot']['sources'] if 'accessU' in x.get('requested_url',''))
 return snap

class RecoveryTest(unittest.TestCase):
 def test_real_raw_parent_and_result_links_are_observed_not_invented(self):
  snap=fixture();out=profile(snap)
  self.assertEqual(out['profile_token'],locator(snap['requested_url'],'U'))
  self.assertEqual(out['pedigree']['sire'],'ルヴァンスレーヴ')
  self.assertIn('pw01dud102015104189/',out['parent_profile_tokens']['sire'])
  self.assertTrue(out['runs']);self.assertTrue(all(x['official_result_navigation_token'].startswith('pw01sde') for x in out['runs']))
 def test_raw_tamper_redirect_nonofficial_and_parent_ambiguity_refused(self):
  original=fixture()
  for kind in ('raw','redirect','official','parent'):
   s=copy.deepcopy(original)
   if kind=='raw':s['raw_sha256']='0'*64
   elif kind=='redirect':s['final_url']=s['final_url'].replace('www.jra.go.jp','example.org')
   elif kind=='official':s['official']=False
   else:
    raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
    # A separate labelled dt/dd preserves the parsed father name while exposing
    # two contradictory official links for that same relationship.
    from bs4 import BeautifulSoup
    import re
    soup=BeautifulSoup(_decode(raw,s['content_type']),'html.parser')
    link=soup.find('a',href=re.compile('pw01dud102015104189/6E'));self.assertIsNotNone(link)
    dd=link.find_parent('dd');dt=dd.find_previous_sibling('dt')
    other=BeautifulSoup(str(dd),'html.parser').find('dd')
    for a in other.select('a[href]'):a['href']=a['href'].replace('pw01dud102015104189/6E','pw01dud102015104188/6E')
    dd.insert_after(other);dd.insert_after(copy.copy(dt))
    raw=str(soup).encode();s['content_type']='text/html; charset=utf-8'
    s['raw_gzip_b64']=base64.b64encode(gzip.compress(raw)).decode();s['raw_sha256']=digest_bytes(raw);s['byte_count']=len(raw)
   s['snapshot_sha256']=sha_obj({k:v for k,v in s.items() if k!='snapshot_sha256'})
   with self.subTest(kind=kind),self.assertRaises(ValueError):profile(s)
 def test_actual_signed_source_exact_hash_recovery_and_alias_remains_unresolved(self):
  s=fixture();p=profile(s);raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
  h={**p['pedigree'],'runs':parse_horse_history(raw,s['content_type'])['runs'],
     'raw_sha256':s['raw_sha256'],'profile_token_sha256':digest_bytes(p['profile_token'].encode())}
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);directory=root/'runtime/pedigree_corpus';directory.mkdir(parents=True)
   other=copy.deepcopy(h);other['profile_token_sha256']='a'*64;other['raw_sha256']='b'*64
   obj={'official':True,'source':'www.jra.go.jp','harvested_at':'2026-10-18T00:00:00+00:00','horses':[h,other]}
   obj['sha256']=digest_bytes(json.dumps(obj,ensure_ascii=False,sort_keys=True).encode())
   (directory/'fixture.json').write_text(json.dumps(obj))
   candidates=list((ROOT/'runtime/executions/KM-JRA-TKY-20261018-R10-LIVE-R1/SOURCE/runs').glob('*/source_receipt_envelope.json'))
   self.assertTrue(candidates);path=root/candidates[0].relative_to(ROOT);path.parent.mkdir(parents=True);path.write_bytes(candidates[0].read_bytes())
   out=recover(root)
   self.assertEqual(out['counts']['profile_locator_resolved_observations'],1)
   self.assertEqual(out['counts']['profile_locator_unresolved_observations'],1)
   self.assertGreater(out['counts']['official_result_locator_resolved_runs'],0)
   self.assertEqual(out['counts']['permanent_horse_ids_resolved'],0)
   self.assertFalse(out['resolved'][0]['research_training_eligible'])
   self.assertEqual(out['counts']['same_pedigree_tuple_multiple_navigation_tokens'],1)
   self.assertTrue(verify_recovery_bindings(out,root))
   for kind in ('valid_locator','parent_locator','run_locator','run_index','duplicate_observation','duplicate_run','availability','cutoff_flag','proof_time','path_traversal'):
    bad=copy.deepcopy(out);row=bad['resolved'][0]
    if kind=='valid_locator':row['official_profile_token']='pw01dud102015104189/6E'
    elif kind=='parent_locator':row['parent_profile_tokens']['sire']=row['official_profile_token']
    elif kind=='run_locator':row['run_bindings'][0]['official_result_navigation_token']=row['run_bindings'][0]['official_result_navigation_token'][:-2]+'00'
    elif kind=='run_index':row['run_bindings'][0]['run_index']=-1
    elif kind=='duplicate_observation':bad['resolved'].append(copy.deepcopy(row))
    elif kind=='duplicate_run':row['run_bindings'].append(copy.deepcopy(row['run_bindings'][0]))
    elif kind=='availability':row['earliest_content_available_at']='2000-01-01T00:00:00+00:00'
    elif kind=='cutoff_flag':row['chronology_before_target']=not row['chronology_before_target']
    elif kind=='path_traversal':
     old=row['corpus_file'];row['corpus_file']=old.replace('/pedigree_corpus/','/pedigree_corpus/../pedigree_corpus/')
     bad['corpus_files'][row['corpus_file']]=bad['corpus_files'][old]
    else:bad['raw_proofs'][row['proof']]['fetched_at']='2000-01-01T00:00:00+00:00'
    bad['sha256']=sha_obj({k:v for k,v in bad.items() if k!='sha256'})
    with self.subTest(kind=kind):
     runner=Mock()
     with self.assertRaises(ValueError):reverify_oidc(bad,root,runner=runner)
     runner.assert_not_called()
 def test_identical_raw_content_recovers_observation_without_alias_or_registry_merge(self):
  s=fixture();p=profile(s);raw=gzip.decompress(base64.b64decode(s['raw_gzip_b64']))
  h={**p['pedigree'],'runs':parse_horse_history(raw,s['content_type'])['runs'],
     'raw_sha256':s['raw_sha256'],'profile_token_sha256':digest_bytes(p['profile_token'].encode())}
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);directory=root/'runtime/pedigree_corpus';directory.mkdir(parents=True)
   obj={'official':True,'source':'www.jra.go.jp','harvested_at':'2026-10-18T00:00:00+00:00','horses':[h]}
   def save():
    obj['sha256']=digest_bytes(json.dumps({k:v for k,v in obj.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode())
    (directory/'fixture.json').write_text(json.dumps(obj))
   save()
   source=next((ROOT/'runtime/executions/KM-JRA-TKY-20261018-R10-LIVE-R1/SOURCE/runs').glob('*/source_receipt_envelope.json'))
   path=root/source.relative_to(ROOT);path.parent.mkdir(parents=True);path.write_bytes(source.read_bytes())
   baseline=recover(root);exact=baseline['resolved'][0]
   equivalent=copy.deepcopy(h);equivalent['profile_token_sha256']='a'*64
   different=copy.deepcopy(equivalent);different['raw_sha256']='b'*64
   mismatch=copy.deepcopy(equivalent);mismatch['sire']='UNMATCHED_EXACT_PEDIGREE'
   obj['horses'].extend([equivalent,different,mismatch]);save();out=recover(root)
   self.assertEqual(out['counts']['profile_locator_resolved_observations'],2)
   self.assertEqual(out['counts']['raw_content_equivalent_resolved_observations'],1)
   self.assertEqual(out['resolved'][0],exact)
   recovered=out['resolved'][1]
   self.assertEqual(recovered['recovery_method'],'RAW_CONTENT_EQUIVALENT_PROFILE_NAVIGATION')
   self.assertNotEqual(recovered['profile_token_sha256'],digest_bytes(recovered['official_profile_token'].encode()))
   self.assertTrue(recovered['original_raw_bytes_equal']);self.assertIsNone(recovered['permanent_horse_id'])
   self.assertTrue(verify_recovery_bindings(out,root))
   for kind in ('remove_method','false_method','wrong_locator','false_availability'):
    bad=copy.deepcopy(out);row=bad['resolved'][1]
    if kind=='remove_method':row.pop('recovery_method')
    elif kind=='false_method':row['recovery_method']='NAME_ONLY'
    elif kind=='wrong_locator':row['official_profile_token']='pw01dud102015104189/6E'
    else:row['earliest_content_available_at']='2000-01-01T00:00:00+00:00'
    bad['sha256']=sha_obj({k:v for k,v in bad.items() if k!='sha256'})
    with self.subTest(kind=kind),self.assertRaises(ValueError):verify_recovery_bindings(bad,root)
   late=recover(root,target_cutoff='2026-10-17T09:00:00+09:00')
   self.assertFalse(late['resolved'][1]['chronology_before_target'])
   # Real stored SOURCE/Raw binding remains mandatory even when every clock is
   # after the target. Zero CLI calls here are NOT a claim of real OIDC success.
   runner=Mock()
   qualification=reverify_oidc(late,root,runner=runner)
   runner.assert_not_called()
   self.assertEqual(qualification['file_verifications'],{})
   self.assertEqual(qualification['qualified_profile_locator_observations'],0)
   self.assertEqual(qualification['qualified_result_locator_runs'],0)
   bad=copy.deepcopy(late);bad['resolved'][0]['earliest_content_available_at']='2000-01-01T00:00:00+00:00'
   bad['sha256']=sha_obj({k:v for k,v in bad.items() if k!='sha256'})
   with self.assertRaisesRegex(ValueError,'RECOVERY_BINDING_PROFILE'):reverify_oidc(bad,root,runner=runner)
   runner.assert_not_called()
   # Post-cutoff is not permission to skip the original byte/hash check.
   future_tamper=json.loads((directory/'fixture.json').read_text())
   future_tamper['harvested_at']='2026-10-18T00:00:01+00:00'
   future_tamper['sha256']=digest_bytes(json.dumps({k:v for k,v in future_tamper.items() if k!='sha256'},ensure_ascii=False,sort_keys=True).encode())
   (directory/'fixture.json').write_text(json.dumps(future_tamper))
   with self.assertRaisesRegex(ValueError,'RECOVERY_BINDING_CORPUS'):reverify_oidc(late,root,runner=runner)
   runner.assert_not_called()


def oidc_fixture(root):
 for n in ('corpus.json','source.json'):(root/n).write_text(n)
 out={'target_cutoff':'2026-10-24T09:00:00+09:00','corpus_files':{'corpus.json':{'file_sha256':digest_bytes((root/'corpus.json').read_bytes())}},
      'source_files':{'source.json':digest_bytes((root/'source.json').read_bytes())},
      'raw_proofs':{'proof':{'source_envelope':'source.json','github_code_sha':'a'*40}},
      'resolved':[{'corpus_file':'corpus.json','observation_index':0,'official_profile_token':'opaque',
                   'identity_namespace':'NOT_PERMANENT','proof':'proof','chronology_before_target':True,
                   'run_bindings':[{'proof':'proof','chronology_before_target':True}]}]}
 out['sha256']=sha_obj(out);return out

class OidcRecoveryTest(unittest.TestCase):
 def test_only_potentially_qualifying_dependencies_use_the_verifier(self):
  # Synthetic clocks isolate target selection, not real attestation trust.
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);r=oidc_fixture(root)
   for name in ('parent.json','run_only_source.json','future_source.json','future_corpus.json'):
    (root/name).write_text(name)
   r['source_files'].update({name:digest_bytes((root/name).read_bytes())
     for name in ('parent.json','run_only_source.json','future_source.json')})
   r['corpus_files']['future_corpus.json']={'file_sha256':digest_bytes((root/'future_corpus.json').read_bytes())}
   for proof,name in (('parent','parent.json'),('run_only','run_only_source.json'),('future','future_source.json')):
    r['raw_proofs'][proof]={'source_envelope':name,'github_code_sha':'a'*40}
   r['resolved'][0]['parent_profile_proofs']={'sire':'parent'}
   # A post-cutoff profile can still reference an independently eligible run;
   # do not prune whole rows merely because the profile clock is too late.
   row=copy.deepcopy(r['resolved'][0]);row['observation_index']=1
   row['proof']='future';row['chronology_before_target']=False
   row['parent_profile_proofs']={'sire':'future'}
   row['run_bindings']=[{'proof':'run_only','chronology_before_target':True},
                        {'proof':'future','chronology_before_target':False}]
   r['resolved'].append(row)
   future=copy.deepcopy(row);future['corpus_file']='future_corpus.json';future['observation_index']=0
   future['run_bindings']=[{'proof':'future','chronology_before_target':False}]
   r['resolved'].append(future)
   r['sha256']=sha_obj({k:v for k,v in r.items() if k!='sha256'})
   # Reference the previous superset's eligibility conditions. A failure of an
   # eligible file must affect the same counts with or without target pruning.
   for failed in (None,'source.json','run_only_source.json','corpus.json'):
    all_qualified={name:name!=failed for name in (*r['corpus_files'],*r['source_files'])}
    expected_profiles=sum(all_qualified[x['corpus_file']] and x['chronology_before_target']
      and all_qualified[r['raw_proofs'][x['proof']]['source_envelope']] for x in r['resolved'])
    expected_runs=sum(all_qualified[x['corpus_file']] and run['chronology_before_target']
      and all_qualified[r['raw_proofs'][run['proof']]['source_envelope']]
      for x in r['resolved'] for run in x['run_bindings'])
    def cli(command,**kwargs):
     name=Path(command[3]).name
     when='2026-10-25T13:00:00Z' if name==failed else '2026-10-18T13:00:00Z'
     data=[{'verificationResult':{'verifiedTimestamps':[{'timestamp':when}]}}]
     return Mock(returncode=0,stdout=json.dumps(data),stderr='')
    runner=Mock(side_effect=cli)
    with self.subTest(failed=failed),patch('jra_pedigree_identity_recovery.verify_recovery_bindings',return_value=True) as binding:
     out=reverify_oidc(r,root,runner=runner)
     binding.assert_called_once_with(r,root)
     self.assertEqual(set(out['file_verifications']),{'corpus.json','source.json','parent.json','run_only_source.json'})
     self.assertEqual({Path(call.args[0][3]).name for call in runner.call_args_list},set(out['file_verifications']))
     self.assertEqual(out['qualified_profile_locator_observations'],expected_profiles)
     self.assertEqual(out['qualified_result_locator_runs'],expected_runs)
     self.assertFalse(out['stopped_on_refusal']);self.assertFalse(out['production_eligible'])

 def test_actual_verifier_result_and_times_are_required_for_identity_lookup_only(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);r=oidc_fixture(root)
   for when,expected in [('2026-10-18T13:00:00Z',1),('2026-10-25T13:00:00Z',0)]:
    data=[{'verificationResult':{'verifiedTimestamps':[{'timestamp':when}]}}]
    runner=Mock(return_value=Mock(returncode=0,stdout=json.dumps(data),stderr=''))
    # Synthetic files isolate CLI/OIDC metadata parsing; real content rebinding
    # and forged valid-locator rejection are tested above with a signed SOURCE.
    with patch('jra_pedigree_identity_recovery.verify_recovery_bindings',return_value=True):out=reverify_oidc(r,root,runner=runner)
    self.assertEqual(out['qualified_profile_locator_observations'],expected)
    self.assertFalse(out['research_training_eligible']);self.assertFalse(out['production_eligible'])
    self.assertTrue(all('--signer-workflow' in x.args[0] for x in runner.call_args_list))
    self.assertTrue(all('--source-ref' in x.args[0] and 'refs/heads/main' in x.args[0] for x in runner.call_args_list))
    self.assertIn('--source-digest',runner.call_args_list[-1].args[0])
 def test_permission_refusal_is_not_retried_or_routed_elsewhere(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);r=oidc_fixture(root)
   runner=Mock(return_value=Mock(returncode=1,stdout='',stderr='HTTP 403 permission denied'))
   with patch('jra_pedigree_identity_recovery.verify_recovery_bindings',return_value=True):out=reverify_oidc(r,root,runner=runner)
   self.assertTrue(out['stopped_on_refusal']);self.assertEqual(runner.call_count,1)
   self.assertEqual(out['qualified_profile_locator_observations'],0)
 def test_modified_attested_bytes_are_refused_before_network(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);r=oidc_fixture(root);(root/'corpus.json').write_text('changed');runner=Mock()
   with patch('jra_pedigree_identity_recovery.verify_recovery_bindings',return_value=True),self.assertRaisesRegex(ValueError,'FILE_CHANGED'):reverify_oidc(r,root,runner=runner)
   runner.assert_not_called()
