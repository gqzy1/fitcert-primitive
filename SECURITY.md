# Security and limits

- **Declared facts.** Consensus does not authenticate inventory, ownership, capabilities, or real-world availability. Public consumers must not treat a certificate as possession or permission.
- **Semantic error.** Independent model judgments can share bias or obey malicious text. Data/instruction separation, conservative UNKNOWN and complete-vector agreement mitigate this; they do not prove prompt-injection resistance or objective correctness.
- **Deterministic guarantee.** Matching, minimum-cover and Hall certificates are exact relative to the accepted matrix. This separates semantic uncertainty from combinatorial correctness.
- **No cross-record exclusion.** Each record is a sealed allocation problem, not a shared stock ledger. One item may be declared again elsewhere. No payment, escrow, role assignment or delivery occurs.
- **No hidden retry.** One accepted assessment per record. Contract errors revert; clients must inspect a failed transaction before proposing any new write. Do not use leader-only mode, appeal, or automatically resubmit writes.
- **Authority.** Sender namespaces, owner-only transitions and revisions protect records. Per-address quotas do not prevent Sybil behavior. All records and declarations are public; use non-sensitive fixtures.
- **Identity.** Distinct array indexes represent distinct units. The contract rejects identical descriptions but cannot detect duplicated physical items described differently. Use stable unit identifiers in descriptions.
- **Economics.** Stable Studionet only, official RPC `https://studio.genlayer.com/api`. Developer clients must check chain ID 61999 and zero gas price before zero-value writes. Never fund a demonstration signer.
