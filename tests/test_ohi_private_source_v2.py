"""Genuine R02 regression plus labelled contract mutations, never Live claims."""
import copy,hashlib,json,os,unittest
from pathlib import Path
from runtime import ohi_nankan_private_source as v1
from runtime import ohi_nankan_private_source_v2 as v2
from runtime.urw_nankan_reference_source import url_scope,Client,NankanError,DOM,decode

class IsolatedTransport(unittest.TestCase):
    def test_ohi_odds_scope_does_not_expand_urw_client(self):
        u=v1.ORIGIN+'/odds/202610262011010201.do'
        with self.assertRaises(NankanError):Client.validate_url(u)
        self.assertEqual('/odds/202610262011010201.do',v2.OhiClient.validate_url(u).path)
        for bad in (u.replace('www.nankankeiba.com','example.com'),u+'?x=1',u.replace('010201','011301')):
            with self.subTest(url=bad),self.assertRaises(NankanError):v2.OhiClient.validate_url(bad)

@unittest.skipUnless(os.environ.get('KM_OHI_PRIVATE_FIXTURE'),'genuine private R02 required')
class GenuineR02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Path(os.environ['KM_OHI_PRIVATE_FIXTURE'])/'live-r02-v1.source'
        cls.raw={n:(cls.p/(n+'.raw.html')).read_bytes() for n in ('calendar','program','card','changes')}
        cls.meta={n:json.loads((cls.p/(n+'.receipt.json')).read_text()) for n in cls.raw}
        cls.races=v1.parse_program(cls.raw['program'],cls.meta['program']['url'],'2026-10-26');cls.race=cls.races[1]
    def observation(self,card=None,changes=None,odds=None):
        raw={**self.raw,'card':card or self.raw['card'],'changes':changes or self.raw['changes']}
        meta={k:{**self.meta[k],'raw_sha256':hashlib.sha256(v).hexdigest()} for k,v in raw.items()}
        return v2.observe(self.race,raw['card'],meta['card'],raw['changes'],meta['changes'],list(meta.values()),program_races=self.races,odds=odds)
    def changed_raw(self,row):
        return decode(self.raw['changes']).replace('<p class="nk23_c-text02">本日開催に変更情報がありません</p>',row).encode('cp932')
    def change_row(self,race_no,kind='出走取消',runner='1',horse=None,name=None):
        facts=self.observation()['facts'];f=next(x for x in facts if x['runner_id']==runner)
        return f'<li class="nk23_c-block01__list__item" id="{race_no:02d}"><span class="nk23_c-block01__label">{race_no}R</span><a href="/syousai/{self.race["provider_day_id"]}{race_no:02d}.do">Race</a><div class="nk23_c-block01__list2__item"><p class="nk23_c-block01__tag">{kind}</p><span class="nk23_c-block01__txt2">{runner}番</span><a href="/uma_info/{horse or f["provider_horse_id"]}.do">{name or f["name"]}</a></div></li>'
    def test_real_first_start_panels_are_not_history(self):
        o=self.observation();self.assertEqual(14,len(o['facts']));self.assertEqual(v2.SOURCE_PROFILE,o['source_profile'])
        for i in ('3','5','7','9'):
            f=next(x for x in o['facts'] if x['runner_id']==i);self.assertEqual([],f['starts'])
            self.assertTrue(any(h['reason']=='FIRST_START_STATISTICS_NOT_RACE_HISTORY' and h['record'] is None for h in f['history_observations']))
        self.assertTrue(all(f['odds'] is None for f in o['facts']))
    def test_other_race_change_is_observation_not_no_change(self):
        o=self.observation(changes=self.changed_raw(self.change_row(3)))
        self.assertEqual('OTHER_RACE_CHANGES_OBSERVED_TARGET_UNLISTED',o['changes']['status']);self.assertFalse(o['changes']['absence_is_no_change'])
    def test_target_cancellation_must_match_card_and_excludes_runner(self):
        text=decode(self.raw['card']);dom=DOM(text).root
        # Mutation is derived from genuine Card; not an actual cancellation.
        row=next(r for r in dom.all('tr') if r.all('td','umaban') and r.all('td','umaban')[0].text()=='1')
        self.assertTrue(row.all('td','cs-odds'))
        # Direct decoded replacement within its unique odds cell.
        import re
        text,n=re.subn(r'(<td[^>]*class="[^"]*cs-odds[^"]*"[^>]*>).*?(</td>)',r'\1取消\2',text,count=1,flags=re.S)
        self.assertEqual(1,n)
        o=self.observation(card=text.encode('cp932'),changes=self.changed_raw(self.change_row(2)))
        self.assertNotIn('1',[f['runner_id'] for f in o['facts']]);self.assertEqual(13,len(o['facts']))
        with self.assertRaisesRegex(NankanError,'CONTRADICTION'):self.observation(changes=self.changed_raw(self.change_row(2)))
    def test_unidentified_change_missing_list_and_abandoned_reject(self):
        with self.assertRaisesRegex(NankanError,'IDENTITY'):self.observation(changes=self.changed_raw(self.change_row(2,horse='9999999999')))
        with self.assertRaisesRegex(NankanError,'UNKNOWN'):self.observation(changes=self.changed_raw(''))
        with self.assertRaisesRegex(NankanError,'ABANDONED'):self.observation(changes=self.changed_raw(self.change_row(2,kind='競走取り止め')))
    def test_enabled_link_requires_observation_and_no_fabricated_prices(self):
        raw=decode(self.raw['card']);import re
        raw,n=re.subn(r'<a(?=[^>]*data-menu="odds")[^>]*>',f'<a data-menu="odds" href="/odds/{self.race["provider_race_id"]}01.do">',raw,count=1)
        self.assertEqual(1,n)
        with self.assertRaisesRegex(NankanError,'ODDS_REQUIRED'):self.observation(card=raw.encode('cp932'))
    def test_old_v1_still_rejects_new_history_shape(self):
        with self.assertRaisesRegex(NankanError,'DESCRIPTOR_NOT_UNIQUE'):v1.parse_single_card(self.raw['card'],self.race,self.meta['card']['url'])
    def test_odds_prices_are_explicit_finite_audit_only(self):
        facts=self.observation()['facts']
        def market(value):
            rows=''.join(f'<tr><td>{f["runner_id"]}</td><td>{f["name"]}</td><td>{value}</td><td>1.0-2.0</td></tr>' for f in facts)
            raw=decode(self.raw['card']).replace('</main>',f'<table class="nk23_c-table04__table">{rows}</table></main>').encode('cp932')
            meta={**self.meta['card'],'url':v1.ORIGIN+'/odds/'+self.race['provider_race_id']+'01.do','raw_sha256':hashlib.sha256(raw).hexdigest()}
            return v2.observed_market(raw,meta,self.race,facts)
        good=market('2.5');self.assertFalse(good['prices_consumed']);self.assertEqual(14,len(good['rows']))
        for bad in ('THIS_IS_NOT_AN_ODDS','9'*400,'0'):
            with self.subTest(value=bad),self.assertRaises(NankanError):market(bad)
    def test_mixed_race_link_rejected(self):
        row=self.change_row(2).replace('</li>','<a href="/syousai/'+self.race['provider_day_id']+'01.do">Other</a></li>')
        with self.assertRaisesRegex(NankanError,'RACE_LINK_IDENTITY'):self.observation(changes=self.changed_raw(row))
    def test_unnumbered_cancel_binding_must_restore_unique_universe(self):
        import re
        card,n=re.subn(r'(<td[^>]*class="[^"]*umaban[^"]*"[^>]*>)\s*1\s*(</td>)',r'\1取消\2',decode(self.raw['card']),count=1)
        self.assertEqual(1,n)
        good=self.changed_raw(self.change_row(2))
        accepted=self.observation(card=card.encode('cp932'),changes=good)
        self.assertEqual(13,len(accepted['facts']))
        for number in ('2','15'):
            bad=decode(good).replace('1番',number+'番').encode('cp932')
            with self.subTest(number=number),self.assertRaisesRegex(NankanError,'DUPLICATE_OR_GAP'):
                self.observation(card=card.encode('cp932'),changes=bad)
    def test_material_receipt_changes_do_not_recompute_input(self):
        from runtime.ohi_single_race_research import material_input_sha256
        old=self.observation();other=copy.deepcopy(old)
        other['source']['fetched_at']='2099-01-01T00:00:00+00:00'
        other['facts'][0]['history_observations'][0]['provenance']['source_raw_sha256']='different'
        self.assertEqual(material_input_sha256(old),material_input_sha256(other))
        other['facts'][0]['current_body_weight']=501
        self.assertNotEqual(material_input_sha256(old),material_input_sha256(other))
        corrected=copy.deepcopy(old);corrected['race']['race_name']='B2'
        self.assertNotEqual(material_input_sha256(old),material_input_sha256(corrected))
    def test_jockey_direction_not_link_order(self):
        f=self.observation()['facts'][0];old=f['current_jockey']
        row=self.change_row(2,kind='騎手変更').replace('</div></li>',f'<p class="nk23_c-block01__text2">変更後 <a href="/kis_info/8888.do">新騎手</a></p><p class="nk23_c-block01__text2">変更前 <a href="/kis_info/9999.do">{old}</a></p></div></li>')
        with self.assertRaisesRegex(NankanError,'JOCKEY_DIRECTION'):self.observation(changes=self.changed_raw(row))

if __name__=='__main__':unittest.main()
