# Committed derived bundles — manifest-aware readers

The derived builder still writes current_view.json and semantic_index.sqlite
at the top level for existing consumers. These two legacy paths are NOT one
atomic transaction. Readers needing a coherent pair must instead use the
new current_bundle.json commit manifest and the immutable generation files
under .semanticatlas-generations/<generation>/.

From a trusted checkout, import build/build_current_view.py, invoke
load_committed_bundle(outdir), and use its verified view plus database path.
The manifest is read once; the reader checks both SHA-256 digests before
returning. A partially published legacy export cannot change the committed
generation. Builds with interrupted legacy replacement do not commit a new
manifest. Multiple writers may interleave legacy exports but any accepted
manifest refers to exactly one immutable generation.

Generation directories are retained intentionally: never delete an older
generation while a reader may still reference it. This protects application
reader consistency on cooperating, trusted local filesystems. The code does
not defend against an adversary that changes generation files after the
reader's digest check, nor does it independently attest a power-loss-safe
directory sync or a remote SMB transaction. Host-managed immutable storage,
writer coordination and forensic provenance are separate contracts.

source subject: Semantic Atlas direct materializer. No identity/consent or
model effect authority follows from a materialization receipt.
