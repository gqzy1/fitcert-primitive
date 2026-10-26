# Protocol

`fitcert-1` has two view methods and three write methods. Every returned record is canonical JSON. Addresses in keys are lowercased actual transaction senders. There is no administrator.

| Method | Arguments | Effect |
| --- | --- | --- |
| `protocol` | none | Version, bounds and exact semantic rules |
| `get_record` | record ID | Current JSON record or empty string |
| `seal` | slug, JSON payload | Immutable input and input commitment; returns record ID |
| `assess` | record ID, expected revision 0 | Independent matrix consensus and deterministic proofs; revision 1 |
| `certify` | record ID, expected revision 1 | COMPLETE only; terminal certificate; revision 2 |

Slug: 3–32 ASCII lowercase letters, digits or hyphens. Payload keys are exactly `scope`, `items`, `requests`. Scope: 10–240 characters. Each list has 1–6 distinct descriptions of 10–500 characters. Surrounding whitespace, invalid UTF-8, control characters other than tab/newline and duplicate JSON keys reject. Payload limit: 9,000 characters. Per-owner limit: 16 records. All limits count Unicode code points unless stated otherwise.

Sealing the same canonical input under the same owner/slug returns the existing ID without another record. Changing that input rejects. Only the owner may assess or certify. Explicit revisions prevent stale writes. One accepted assessment per record prevents selective replacement of an unfavorable result. To describe changed facts, create a new record; the original stays readable.

## Consensus boundary

For each pair the label is FIT only if the item's explicit declaration supports every request requirement; NO if an explicit fact contradicts any requirement; otherwise UNKNOWN. NO dominates missing facts. No external default capability is assumed. Requests each demand one item, and each item is indivisible. Scope is descriptive context, never a higher-priority instruction.

Leader and each validator independently run the complete extraction against the same immutable input. Exact cell-vector equality is required. Validators receive no leader-chosen subset. Errors and malformed outputs disagree, rather than producing UNKNOWN or accepting matching errors. Schema checks are supplementary to independent semantic agreement. The equivalence function is not a format-only validator.

## Matching and proof

Rows are requests; columns are items; indexes are zero-based. For a fixed graph, bounded DP enumerates request choices while keeping the lexicographically smallest assignment per used-item bitmask. It selects greatest cardinality, then smallest assignment. Unmatched sorts after all item indexes. At most 64 bitmasks exist. This tie-break is deterministic and is not a fairness rule.

Alternating reachability begins at unmatched requests, follows unmatched request-to-item edges and matched item-to-request edges. With reachable sets ZL/ZR, the minimum vertex cover is `(all requests minus ZL) union ZR`. Every edge must be covered and cover size must equal matching size. A matching lower-bounds optimum; an equally sized vertex cover upper-bounds it, proving optimality without trusting the solver.

The reachable requests form a Hall witness. Its neighbor list is recomputed from all graph edges. `deficit = |requests| - |neighbors|` equals total requests minus maximum matching size. For a complete graph matching, the witness is empty with deficit zero. A SHORTAGE certificate uses the **possible** graph's positive deficit, so uncertainty cannot falsely be blamed for a proven shortage. The supported graph's witness describes only currently supported availability.

Both proof objects are checked before storage. `certify` recomputes them and hashes `{version,input_hash,assessment_hash,matching}`. `input_hash` binds version and all input; `assessment_hash` binds that input hash, every accepted cell and both proof objects. Certifying is a publication, not a resource transfer or reservation.
