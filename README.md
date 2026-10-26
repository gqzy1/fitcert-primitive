# FitCert

A standalone GenLayer Intelligent Contract for **provable one-to-one allocation from natural-language compatibility**.

Two requests need laptops. Both laptops have HDMI, but only the first has USB-C. Assigning the first laptop to the HDMI request wastes the only fit for the USB-C request. FitCert independently validates the complete compatibility matrix, then computes a maximum matching and a checkable optimality certificate. The model never chooses the allocation.

**Deployed:** [Stable Studionet contract](https://explorer-studio.genlayer.com/address/0xb69c3E2fe1b78cF7d0Ef23d5a5f3bE05bE694331). Four successful finalized transactions cover deployment, sealing, real semantic consensus and terminal certification. [Evidence](EVIDENCE.md).

## Mechanism

1. `seal` fixes 1–6 indivisible item descriptions and 1–6 single-item requests under the sender's namespace.
2. `assess` asks the leader and validators to independently label **every** request/item pair `FIT`, `NO` or `UNKNOWN`. All cells must agree, including cells irrelevant to one candidate matching. Model errors cannot become business uncertainty.
3. Deterministic dynamic programming calculates maximum matchings in the supported graph (`FIT`) and possible graph (`FIT` or `UNKNOWN`). Each matching includes a minimum vertex cover of equal size, certifying optimality. A Hall witness explains a shortage.
4. If the supported graph covers every request, `certify` publishes the canonical allocation and its SHA256 commitment. Certification is terminal. Uncertainty elsewhere cannot block an already supported complete allocation.

| State | Meaning |
| --- | --- |
| `SEALED` | Fixed inputs, not assessed |
| `COMPLETE` | A full allocation exists using only FIT edges |
| `UNRESOLVED` | Full allocation requires resolving at least one UNKNOWN |
| `SHORTAGE` | Even treating every UNKNOWN as FIT cannot cover every request |
| `CERTIFIED` | Immutable complete allocation and certificate hash |

The bounds and proofs are exact for the **accepted graph**, not proof that the declarations or semantic labels are objectively true.

## Use

Deploy [contracts/fit_cert.py](contracts/fit_cert.py), no constructor arguments, on **Stable Studionet, chain 61999**. Select **Normal (Full Consensus)**. The exact SDK runner is pinned in the first line.

Use `examples/workshop.json` as the JSON string argument to:

```text
seal("workshop", payload)
assess("<lowercase-sender>:workshop", 0)
certify("<lowercase-sender>:workshop", 1)
get_record("<lowercase-sender>:workshop")
```

Wait for each transaction's successful finalized receipt and matching readback before the next write. No paid API, backend, token or frontend is needed. [API and proofs](PROTOCOL.md) · [Security](SECURITY.md) · [Verification](EVIDENCE.md).

## Test

Python 3.12+:

```sh
python -m unittest discover -s tests -v
pip install -r requirements-dev.txt
genvm-lint check contracts/fit_cert.py --json
python tools/sdk_check.py
```

The unit suite uses a scripted host and explicitly invokes the validator. It includes all 512 3×3 binary graphs, rectangular graphs, proof tampering, the greedy trap, uncertainty, owner isolation and terminal state checks. `sdk_check.py` uses official SDK storage and calldata with a mocked model; it is **not network consensus**. The contract retains the same pinned runner found in the SDK artifact release selected by that helper.

## Scope

Useful as a small allocation-certificate primitive for declared equipment or other non-sensitive resources. Item index is physical-slot identity **within one record**: declare each actual unit once. Descriptions must be distinct; add stable unit IDs for otherwise identical items. There is no global inventory, reservation, custody, transfer, identity verification, priority policy, fairness guarantee, multi-item bundle fulfillment or physical delivery. Two records can describe the same item; consumers must enforce cross-record inventory separately. All inputs are public.

MIT license.
