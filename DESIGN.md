# Design decisions

## A proof-producing allocation primitive

Pairwise semantic classification alone does not allocate a scarce item. A locally sensible greedy assignment can prevent another request from being fulfilled. FitCert therefore separates two jobs: independent interpretation of all declared compatibility pairs, followed by exact graph optimization with a certificate another developer can check.

The output is not a circular service exchange, a comparison of bilateral clause families, a procedure dependency graph, or a shared financial-capacity ledger. Its primitive is a single sealed bipartite allocation problem, with one-unit exclusion inside that problem, optimal cardinality, deterministic tie-breaking, a matching/cover dual certificate and a conservative Hall shortage witness.

## Two graphs instead of one verdict

Unknown compatibility is not incompatibility. Computing only the FIT graph can falsely describe an information gap as a physical shortage. Computing only the possible graph can allocate an unsupported item. The lower and upper graphs preserve both boundaries:

- Full supported matching: a complete certificate can be published even if unused cells remain unknown.
- Incomplete possible matching: a shortage is proven relative to the accepted declarations, even if missing facts later turn positive.
- Otherwise: more information is needed; no complete certificate is available.

## Small and independently reusable

Six requests and six items permit a 64-mask dynamic program and cheap proof verification. The deployment has no constructor parameters, administrator, companion frontend or application backend. Reads do not call a model. Items and requests are immutable so later readers can recompute the exact same proof.

A consumer needing reservations, external inventory authentication or fair priority must supply those separately. A certificate is a mathematical allocation over declared facts, not authority to take an item.
