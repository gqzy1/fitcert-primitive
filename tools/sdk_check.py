"""Official SDK storage, calldata and callback check with a scripted model response."""
import json
from pathlib import Path
from gltest.direct import VMContext, deploy_contract, create_address

root = Path(__file__).resolve().parents[1]
vm = VMContext()
vm.sender = create_address('fitcert-sdk-test')
with vm.activate():
    contract = deploy_contract(root / 'contracts/fit_cert.py', vm, sdk_version='v0.3.0-rc7')
    vm.check_pickling = True
    vm.mock_llm('.*', json.dumps({'matrix': [['FIT', 'FIT'], ['FIT', 'NO']]}))
    data = {'scope': 'Fictional workshop equipment allocation.',
            'items': ['One laptop: HDMI output and USB-C output.', 'One laptop: HDMI output only; no USB-C output.'],
            'requests': ['One laptop with HDMI output.', 'One laptop with USB-C output.']}
    key = contract.seal('sdk-example', json.dumps(data))
    assessed = json.loads(contract.assess(key, 0))
    assert assessed['state'] == 'COMPLETE'
    assert assessed['proof']['supported']['matching'] == [[0, 1], [1, 0]]
    certified = json.loads(contract.certify(key, 1))
    assert json.loads(contract.get_record(key)) == certified
    assert certified['state'] == 'CERTIFIED'
    print('PASS: official SDK storage/calldata/callback serialization and lifecycle; model mocked, no network consensus.')
