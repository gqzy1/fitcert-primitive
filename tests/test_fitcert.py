"""Scripted host tests. No live model call, consensus node or chain transaction."""
import copy
import importlib.util
import itertools
import json
import sys
import types
import unittest
from pathlib import Path

class Return:
    def __init__(self, calldata): self.calldata = calldata

class Map:
    def __class_getitem__(cls, _): return cls

class Contract:
    def __init_subclass__(cls):
        for name in cls.__annotations__: setattr(cls, name, None)

host = types.SimpleNamespace(message=types.SimpleNamespace(sender_address='0x'+'a'*40),
    public=types.SimpleNamespace(write=lambda f:f,view=lambda f:f),Contract=Contract,
    vm=types.SimpleNamespace(Return=Return),nondet=types.SimpleNamespace())
fake=types.ModuleType('genlayer')
fake.__dict__.update(gl=host,TreeMap=Map,u32=int)
sys.modules['genlayer']=fake
spec=importlib.util.spec_from_file_location('fit_cert',Path(__file__).parents[1]/'contracts/fit_cert.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

INPUT={'scope':'Fictional workshop equipment allocation.',
       'items':['One laptop: HDMI output and USB-C output.','One laptop: HDMI output only; no USB-C output.'],
       'requests':['One laptop with HDMI output.','One laptop with USB-C output.']}
MATRIX={'matrix':[['FIT','FIT'],['FIT','NO']]}

def brute(edges, columns):
    best=0
    for assignment in itertools.product(range(-1,columns),repeat=len(edges)):
        used=[i for i in assignment if i>=0]
        if len(set(used))==len(used) and all(i<0 or edges[r][i] for r,i in enumerate(assignment)):
            best=max(best,len(used))
    return best

class MatchingTests(unittest.TestCase):
    def test_every_three_by_three_graph(self):
        for bits in range(512):
            edges=[[bool(bits & (1 << (r*3+i))) for i in range(3)] for r in range(3)]
            proof=m.maximum(edges,3)
            self.assertEqual(proof['size'],brute(edges,3))
            m.verify_proof(edges,3,proof)
    def test_rectangular_graphs(self):
        for rows,cols in [(1,6),(6,1),(2,3),(3,2)]:
            for bits in range(1<<(rows*cols)):
                edges=[[bool(bits&(1<<(r*cols+i))) for i in range(cols)] for r in range(rows)]
                proof=m.maximum(edges,cols)
                self.assertEqual(proof['size'],brute(edges,cols));m.verify_proof(edges,cols,proof)
    def test_greedy_trap(self):
        p=m.derive(MATRIX['matrix']);self.assertEqual(p['supported']['matching'],[[0,1],[1,0]])
    def test_canonical_tie(self):
        self.assertEqual(m.maximum([[True]*2]*2,2)['matching'],[[0,0],[1,1]])
    def test_unknown_can_be_irrelevant(self):
        self.assertEqual(m.derive([['FIT','UNKNOWN'],['NO','FIT']])['status'],'COMPLETE')
    def test_unresolved(self):
        self.assertEqual(m.derive([['FIT','NO'],['UNKNOWN','UNKNOWN']])['status'],'UNRESOLVED')
    def test_shortage_even_if_unknown_resolved(self):
        p=m.derive([['FIT','NO'],['UNKNOWN','NO']]);self.assertEqual(p['status'],'SHORTAGE')
        self.assertEqual(p['possible']['hall'],{'requests':[0,1],'neighbors':[0],'deficit':1})
    def test_six_by_six(self):
        for edges in [[[True]*6]*6,[[False]*6]*6,[[i==r for i in range(6)] for r in range(6)]]:
            m.verify_proof(edges,6,m.maximum(edges,6))
    def test_tampered_certificate(self):
        edges=[[True,True],[True,False]];p=m.maximum(edges,2)
        p['matching']=[[0,0],[1,0]]
        with self.assertRaises(Exception):m.verify_proof(edges,2,p)
    def test_tampered_cover(self):
        edges=[[True,True],[True,False]];p=m.maximum(edges,2);p['cover']={'requests':[],'items':[]}
        with self.assertRaises(Exception):m.verify_proof(edges,2,p)

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.c=m.FitCert();self.c.records={};self.c.counts={}
        host.message.sender_address='0x'+'a'*40
        self.calls=0
        self.reply=MATRIX
        self.other=MATRIX
        def prompt(*a,**kw): self.calls+=1;return copy.deepcopy(self.reply if self.calls%2 else self.other)
        host.nondet.exec_prompt=prompt
        def boundary(leader,validator):
            result=leader()
            if not validator(Return(copy.deepcopy(result))):raise Exception('DISAGREE')
            return result
        host.vm.run_nondet_unsafe=boundary
        self.key=self.c.seal('sample',json.dumps(INPUT))
    def test_full_lifecycle(self):
        r=json.loads(self.c.assess(self.key,0));self.assertEqual(r['state'],'COMPLETE')
        r=json.loads(self.c.certify(self.key,1));self.assertEqual(r['state'],'CERTIFIED')
        self.assertEqual(r['certificate_hash'],m.sha(r['certificate']));self.assertEqual(self.calls,2)
    def test_unknown_blocks_certify(self):
        self.reply=self.other={'matrix':[['FIT','NO'],['UNKNOWN','UNKNOWN']]}
        self.c.assess(self.key,0)
        with self.assertRaisesRegex(Exception,'NOT_COMPLETE'):self.c.certify(self.key,1)
    def test_shortage_blocks_certify(self):
        self.reply=self.other={'matrix':[['FIT','NO'],['FIT','NO']]}
        self.c.assess(self.key,0)
        with self.assertRaisesRegex(Exception,'NOT_COMPLETE'):self.c.certify(self.key,1)
    def test_disagreement_is_atomic(self):
        before=self.c.get_record(self.key);self.other={'matrix':[['FIT','NO'],['FIT','NO']]}
        with self.assertRaisesRegex(Exception,'DISAGREE'):self.c.assess(self.key,0)
        self.assertEqual(self.c.get_record(self.key),before)
    def test_same_size_different_cells_rejected(self):
        self.other={'matrix':[['FIT','NO'],['NO','FIT']]}
        with self.assertRaisesRegex(Exception,'DISAGREE'):self.c.assess(self.key,0)
    def test_no_reassessment(self):
        self.c.assess(self.key,0)
        with self.assertRaisesRegex(Exception,'ALREADY_ASSESSED'):self.c.assess(self.key,1)
    def test_stale(self):
        with self.assertRaisesRegex(Exception,'STALE_REVISION'):self.c.assess(self.key,1)
    def test_owner(self):
        host.message.sender_address='0x'+'b'*40
        with self.assertRaisesRegex(Exception,'OWNER_ONLY'):self.c.assess(self.key,0)
    def test_isolation(self):
        host.message.sender_address='0x'+'b'*40
        self.assertNotEqual(self.key,self.c.seal('sample',json.dumps(INPUT)))
    def test_idempotent_seal(self):
        self.assertEqual(self.c.seal('sample',json.dumps(INPUT,indent=2)),self.key)
        self.assertEqual(self.c.counts['0x'+'a'*40],1)
    def test_changed_payload(self):
        data=copy.deepcopy(INPUT);data['scope']='Another fictional allocation.'
        with self.assertRaisesRegex(Exception,'ID_CONFLICT'):self.c.seal('sample',json.dumps(data))
    def test_limit(self):
        for i in range(15):self.c.seal('test-'+str(i),json.dumps(INPUT))
        with self.assertRaisesRegex(Exception,'OWNER_LIMIT'):self.c.seal('one-too-many',json.dumps(INPUT))
    def test_certify_terminal(self):
        self.c.assess(self.key,0);self.c.certify(self.key,1)
        with self.assertRaisesRegex(Exception,'NOT_COMPLETE'):self.c.certify(self.key,2)
    def test_model_error_not_business_unknown(self):
        self.reply={'matrix':[['FIT']]}
        before=self.c.get_record(self.key)
        with self.assertRaises(Exception):self.c.assess(self.key,0)
        self.assertEqual(self.c.get_record(self.key),before)
    def test_reads_empty(self):self.assertEqual(self.c.get_record('missing'),'')

class BoundaryTests(unittest.TestCase):
    def test_validator_rejects_errors(self):self.assertFalse(m.equivalent(object(),lambda:MATRIX,2,2))
    def test_validator_rejects_malformed(self):self.assertFalse(m.equivalent(Return({'matrix':[]}),lambda:MATRIX,2,2))
    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(Exception,'DUPLICATE_JSON_KEY'):m.decode('{"matrix":[],"matrix":[]}')
    def test_wrong_model_shapes(self):
        for bad in [[],None,{'matrix':[['FIT','NO'],['YES','NO']]},{'matrix':[['FIT','NO'],['FIT',True]]},{'matrix':MATRIX['matrix'],'extra':1}]:
            with self.assertRaises(Exception):m.matrix_result(bad,2,2)
    def test_input_bounds(self):
        for data in [{},dict(INPUT,items=[]),dict(INPUT,requests=['too short']),dict(INPUT,scope='x'),dict(INPUT,items=INPUT['items']*4),dict(INPUT,items=['Identical item.','Identical item.'])]:
            with self.assertRaises(Exception):m.input_data(json.dumps(data))
    def test_input_control_characters(self):
        with self.assertRaises(Exception):m.input_data(json.dumps(dict(INPUT,scope='A bad\x00scope here.')))
    def test_good_json_string_model_output(self):self.assertEqual(m.matrix_result(json.dumps(MATRIX),2,2),MATRIX)

if __name__=='__main__':unittest.main()
