# Verification

## Offline checks

- Python 3.12.14: 32 unit tests pass. Two exhaustive tests include all 512 binary 3×3 graphs and all 256 graphs of sizes 1×6, 6×1, 2×3 and 3×2. Each optimum is independently compared with brute force; every cover and Hall witness is checked.
- Official `genvm-linter==0.11.0`: AST checks and SDK semantic validation pass. ABI: no constructor arguments, two views, three writes. Informational warning I200 reports a newer runner; this contract deliberately pins the Studio-compatible runner.
- Official SDK Direct Mode: storage, calldata roundtrips, callback serialization and the seal/assess/certify/read lifecycle pass with a scripted model response. SDK artifact container: `v0.3.0-rc7`; runner is the exact dependency hash in the contract header. This test is not a simulator node, live model result or network consensus.

`python tools/verify_record.py <export.json>` recomputes every commitment and both graph proofs. It validates internal consistency only: JSON from an untrusted source can be fabricated. Bind readbacks to the correct source-verified deployment and finalized transaction separately.

## Network evidence

Contract: [`0xb69c3E2fe1b78cF7d0Ef23d5a5f3bE05bE694331`](https://explorer-studio.genlayer.com/address/0xb69c3E2fe1b78cF7d0Ef23d5a5f3bE05bE694331). Stable Studionet, chain 61999. All four transactions used Normal / full consensus, finalized with SUCCESS and MAJORITY_AGREE, and recorded zero rotations.

| Method | Transaction |
| --- | --- |
| deploy | [`0xae27e0a2ab...`](https://explorer-studio.genlayer.com/tx/0xae27e0a2abdda1aa062cdbc681bff328671754e61301a482c504738741f675ea) |
| seal | [`0xa112db5142...`](https://explorer-studio.genlayer.com/tx/0xa112db514221cd55b34f5f07f34b380b29b11586c96dbe322737f1f960cd00b4) |
| assess | [`0x293c8911e1...`](https://explorer-studio.genlayer.com/tx/0x293c8911e123c864dacef628ab792f6e160bcfa5a4f18f21174dc084989f88b2) |
| certify | [`0xf42e28fee3...`](https://explorer-studio.genlayer.com/tx/0xf42e28fee35c6c93d2aa379ad332ad673af2e3ce55434c316fcce9f97ebcf465) |

The real `assess` result is `[[FIT,FIT],[FIT,NO]]`. Its maximum matching is `[[0,1],[1,0]]`, size 2, with a minimum request-side vertex cover of size 2. The record reached CERTIFIED, revision 2. The certificate hash is `8eacfcc3c4015c31279d8fb0aa2667262051fa248e4fe14bf921d1ba19222097`.

Three completed assessment results agreed. Two validator executions were cancelled after quorum. Those cancellation rows appear as ERROR / Idle in Studio; they are not successful votes and are not suppressed. The transaction itself finalized successfully. Other fixtures and rejection cases remain offline tests; no live shortage or adversarial-input coverage is claimed.

### Provenance and reproduction

- [deployment.json](deployment.json) contains full transaction hashes and source identity.
- [source-identity.json](evidence/source-identity.json) records byte identity between the local source and the RLP-decoded deployment `tx_data` displayed by Studio: 10,735 bytes, SHA256 `934eaf1be7543f28bd8ba0a35eeb9529d9f84db6b1dbb1cbd68d5ad7990bdc68`.
- `evidence/*-observed.txt` are text captures of official transaction dialogs. Nested objects may remain collapsed; these are not raw JSON-RPC responses. The deployment observation includes complete encoded transaction data for independent source comparison.
- [finalized-record.json](evidence/finalized-record.json) was obtained through `get_record` with Studio's read state explicitly set to **Finalized**. It matches the `certify` transaction output and passes the offline proof/hash verifier.
- The public Explorer independently displayed exactly four transactions, each FINALIZED / SUCCESS / Accepted.

Import the deployed address into the official Studio, select read state Finalized, and call `get_record("0x32783b8e5a9fa8f27e743639c8f907764f59ea92:workshop")`. Reading requires no new transaction. Run `python tools/verify_record.py evidence/finalized-record.json` to verify every stored commitment and graph proof.

The terminal's official POST checks for `eth_chainId` and `eth_gasPrice` returned HTTP 403; direct terminal access is not claimed resolved. Studio's normal browser interface and public Explorer worked and supplied the live evidence above. The network's transaction schema reports nullable gasPrice/chainId fields; those nulls are not numeric preflight results. No alternate chain or unofficial proxy was used. No paid service, funded signer, retry or appeal was used.
