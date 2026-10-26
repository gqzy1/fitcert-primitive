"""Verify an exported FitCert record's hashes, matrix proofs and certificate offline.
Does not authenticate that a record came from a blockchain. Obtain a trusted finalized readback first.
"""
import ast
import json
import sys
from pathlib import Path

source = Path(__file__).resolve().parents[1] / 'contracts/fit_cert.py'
tree = ast.parse(source.read_text())
tree.body = [node for node in tree.body if not isinstance(node, ast.ClassDef)
             and not (isinstance(node, ast.ImportFrom) and node.module == 'genlayer')]
namespace = {}
exec(compile(tree, str(source), 'exec'), namespace)

def verify(record):
    n = namespace
    data = n['input_data'](n['pack'](record['input']))
    assert record['input_hash'] == n['sha']({'version': n['VERSION'], 'input': data}), 'input hash'
    if record['state'] == 'SEALED':
        assert record['revision'] == 0
        return
    matrix = n['matrix_result']({'matrix': record['matrix']}, len(data['requests']), len(data['items']))['matrix']
    proof = n['derive'](matrix)
    assert proof == record['proof'], 'proof or canonical matching'
    assert record['assessment_hash'] == n['sha']({'input_hash':record['input_hash'],'matrix':matrix,'proof':proof}), 'assessment hash'
    if record['state'] == 'CERTIFIED':
        assert proof['status'] == 'COMPLETE' and record['revision'] == 2
        expected = {'version': n['VERSION'], 'input_hash': record['input_hash'],
                    'assessment_hash': record['assessment_hash'], 'matching': proof['supported']['matching']}
        assert record['certificate'] == expected, 'certificate binding'
        assert record['certificate_hash'] == n['sha'](expected), 'certificate hash'
    else:
        assert record['state'] == proof['status'] and record['revision'] == 1

if __name__ == '__main__':
    record = json.loads(Path(sys.argv[1]).read_text())
    verify(record)
    print('PASS: internal hashes and matching proofs. Chain provenance must be verified separately.')
