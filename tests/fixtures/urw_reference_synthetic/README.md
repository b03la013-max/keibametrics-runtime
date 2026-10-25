TEST_SYNTHETIC_ONLY — parser and immutable readback contract fixtures.

`factual_cells.json` retains extracted factual table cells and race metadata.
It contains no original NAR page markup, styles, scripts or compressed pages.
The factory authors a minimal table document, feeds the existing snapshot
builder/parser, and compiles an unsigned reference with an injected test clock.
All generated source and prediction artifacts carry `TEST_SYNTHETIC_ONLY`.
The URL and official-class fields are parser inputs in this isolated test;
they do not attest a real acquisition. The factory never makes a network call,
signs a receipt, sends Runtime requests or writes into repository Runtime trees.

The real source fixtures and historical 428-test evidence remain separate.
Synthetic contract success is not live race, predictive quality, delivery or
Production acceptance. Existing signed fixtures on main are unchanged.
