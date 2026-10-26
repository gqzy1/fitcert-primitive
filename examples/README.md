# Examples

Both JSON files are synthetic declarations, not actual inventory.

`workshop.json` demonstrates a greedy trap: request 0 must receive item 1 and request 1 item 0. The expected matrix is `[[FIT,FIT],[FIT,NO]]`, but the live model result must always be read from the finalized contract record rather than assumed from this fixture.

`shortage.json` is an offline scenario: both requests need USB-C and only one listed item provides it. Unless independently documented in EVIDENCE.md, this file is not a live consensus test.
