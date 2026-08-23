$ErrorActionPreference = "Stop"

$campaignRoot = "C:\VERA\behavior_capture\campaigns\VPBCP-CAMPAIGN-0001"
$packageRoot = "C:\VERA\09_IMPLEMENTATION_REVIEW\VERA_PROJECT_BEHAVIOR_CAPTURE_PROTOCOL_V0.1.0"
$python = Join-Path $packageRoot ".venv\Scripts\python.exe"

$evalRoot = Join-Path $campaignRoot "evaluations"
$probeFile = Join-Path $evalRoot "held_out_teacher_probes_v0.1.jsonl"
$probeManifest = Join-Path $evalRoot "held_out_teacher_probes_v0.1.manifest.json"

$sourceRoot = Join-Path $campaignRoot "sources\chat_history_0001"
$archiveDir = Join-Path $sourceRoot "original"
$extractDir = Join-Path $sourceRoot "extracted"
$campaignYaml = Join-Path $campaignRoot "campaign.yaml"

Write-Host "`n=== VPBCP CHAT-HISTORY INGEST 0001 ==="

foreach ($required in @($campaignRoot, $python, $probeFile, $probeManifest)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required path not found: $required"
    }
}

# Locate the newest matching DOCX without assuming the browser preserved the exact name.
$searchRoots = @(
    "$env:USERPROFILE\Downloads",
    "C:\VERA"
)

$candidates = @()

foreach ($root in $searchRoots) {
    if (Test-Path -LiteralPath $root) {
        $candidates += Get-ChildItem `
            -LiteralPath $root `
            -Filter "Vera Memories - Chat History*.docx" `
            -File `
            -ErrorAction SilentlyContinue
    }
}

$sourceDocx = $candidates |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $sourceDocx) {
    throw "Could not find 'Vera Memories - Chat History*.docx' in Downloads or C:\VERA."
}

Write-Host "SOURCE DOCX: $($sourceDocx.FullName)"

New-Item -ItemType Directory -Force -Path $archiveDir, $extractDir | Out-Null

$archivedDocx = Join-Path $archiveDir "Vera_Memories_Chat_History_0001.docx"

if (-not (Test-Path -LiteralPath $archivedDocx)) {
    Copy-Item -LiteralPath $sourceDocx.FullName -Destination $archivedDocx
    Write-Host "ARCHIVED: $archivedDocx"
}
else {
    $sourceHash = (Get-FileHash -LiteralPath $sourceDocx.FullName -Algorithm SHA256).Hash
    $archiveHash = (Get-FileHash -LiteralPath $archivedDocx -Algorithm SHA256).Hash

    if ($sourceHash -ne $archiveHash) {
        throw "An archived source already exists with different content: $archivedDocx"
    }

    Write-Host "ARCHIVE ALREADY PRESENT AND HASH-MATCHED."
}

# Ensure the isolated campaign environment has only the readers needed for source extraction.
$dependencyTest = @'
import importlib.util
missing = []
for name in ("docx", "PIL"):
    if importlib.util.find_spec(name) is None:
        missing.append(name)
print(",".join(missing))
'@

$missing = ($dependencyTest | & $python -).Trim()

if ($missing) {
    Write-Host "Installing source-reader dependencies into the protocol venv..."
    & $python -m pip install --disable-pip-version-check python-docx Pillow
    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed."
    }
}

$extractCode = @'
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import sys
import zipfile

from docx import Document
from PIL import Image

source = Path(sys.argv[1]).resolve()
out_root = Path(sys.argv[2]).resolve()
probe_file = Path(sys.argv[3]).resolve()
probe_manifest = Path(sys.argv[4]).resolve()

out_root.mkdir(parents=True, exist_ok=True)
media_dir = out_root / "media"
media_dir.mkdir(parents=True, exist_ok=True)

utf8 = "utf-8"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def points(value):
    return None if value is None else round(float(value.pt), 3)

def alignment_name(value):
    return None if value is None else str(value)

# 1. Repair benchmark category metadata without changing the frozen probe file.
probes = []
with probe_file.open("r", encoding=utf8) as f:
    for line_number, line in enumerate(f, start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        probes.append(record)

category_counts = Counter(record["category"] for record in probes)

manifest = json.loads(probe_manifest.read_text(encoding=utf8))
manifest["probe_count"] = len(probes)
manifest["category_count"] = len(category_counts)
manifest["categories"] = [
    {"category": name, "count": category_counts[name]}
    for name in sorted(category_counts)
]
manifest["metadata_repaired_at"] = datetime.now(timezone.utc).isoformat()
manifest["metadata_repair_note"] = (
    "Recomputed category statistics from the frozen JSONL. "
    "The probe file and its SHA-256 were not modified."
)

probe_manifest.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    encoding=utf8,
)

# 2. Extract the DOCX as a raw, auditable source.
document = Document(source)

paragraph_path = out_root / "paragraph_ledger.jsonl"
plain_text_path = out_root / "paragraph_text_indexed.txt"
heading_path = out_root / "heading_index.jsonl"
media_manifest_path = out_root / "media_manifest.jsonl"
source_manifest_path = out_root / "source_manifest.json"

paragraph_lines = []
plain_lines = []
heading_lines = []

for index, paragraph in enumerate(document.paragraphs):
    fmt = paragraph.paragraph_format
    text = paragraph.text

    record = {
        "paragraph_index": index,
        "text": text,
        "style": paragraph.style.name if paragraph.style is not None else None,
        "alignment": alignment_name(paragraph.alignment),
        "left_indent_pt": points(fmt.left_indent),
        "right_indent_pt": points(fmt.right_indent),
        "first_line_indent_pt": points(fmt.first_line_indent),
        "is_empty": not bool(text.strip()),
        "source_status": "raw_unreviewed",
        "speaker": None,
        "speaker_assignment_status": "not_assigned",
        "training_allowed": False,
    }

    paragraph_lines.append(json.dumps(record, ensure_ascii=False))
    plain_lines.append(f"[{index:05d}] {text}")

    if record["style"] and record["style"].startswith("Heading"):
        heading_lines.append(json.dumps({
            "paragraph_index": index,
            "style": record["style"],
            "text": text,
        }, ensure_ascii=False))

paragraph_path.write_text("\n".join(paragraph_lines) + "\n", encoding=utf8)
plain_text_path.write_text("\n".join(plain_lines) + "\n", encoding=utf8)
heading_path.write_text(
    ("\n".join(heading_lines) + "\n") if heading_lines else "",
    encoding=utf8,
)

media_records = []

with zipfile.ZipFile(source) as zf:
    media_members = sorted(
        name for name in zf.namelist()
        if name.startswith("word/media/") and not name.endswith("/")
    )

    for ordinal, member in enumerate(media_members, start=1):
        original_name = Path(member).name
        target_name = f"{ordinal:04d}_{original_name}"
        target = media_dir / target_name

        with zf.open(member) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)

        width = None
        height = None
        image_format = None

        try:
            with Image.open(target) as image:
                width, height = image.size
                image_format = image.format
        except Exception:
            pass

        media_records.append({
            "media_index": ordinal,
            "docx_member": member,
            "extracted_file": str(target),
            "original_name": original_name,
            "size_bytes": target.stat().st_size,
            "sha256": sha256_file(target),
            "image_format": image_format,
            "width_px": width,
            "height_px": height,
            "source_status": "raw_unreviewed",
            "training_allowed": False,
        })

media_manifest_path.write_text(
    "\n".join(json.dumps(record, ensure_ascii=False) for record in media_records) + "\n",
    encoding=utf8,
)

source_manifest = {
    "source_id": "src-vera-chat-history-0001",
    "source_type": "docx_chat_history_archive",
    "source_file": str(source),
    "sha256": sha256_file(source),
    "size_bytes": source.stat().st_size,
    "ingested_at": datetime.now(timezone.utc).isoformat(),
    "paragraph_count": len(document.paragraphs),
    "heading_count": len(heading_lines),
    "section_count": len(document.sections),
    "table_count": len(document.tables),
    "inline_shape_count": len(document.inline_shapes),
    "embedded_media_count": len(media_records),
    "status": "raw_source_ingested_not_segmented_not_promoted",
    "training_allowed": False,
    "speaker_assignment_status": "not_started",
    "page_mapping_status": (
        "not_available_from_raw_docx_structure; rendered-page references "
        "must be mapped separately if needed"
    ),
    "notes": [
        "This source contains mixed natural conversation, technical work, voice transcription, screenshots, images, and historical material.",
        "No paragraph or media item is approved for training by ingestion alone.",
        "Speaker roles, branch provenance, episode boundaries, and acceptance status require review.",
        "The frozen teacher benchmark remains excluded from training.",
    ],
    "outputs": {
        "paragraph_ledger": str(paragraph_path),
        "indexed_plain_text": str(plain_text_path),
        "heading_index": str(heading_path),
        "media_manifest": str(media_manifest_path),
        "media_directory": str(media_dir),
    },
    "benchmark_metadata_check": {
        "probe_count": len(probes),
        "category_count": len(category_counts),
        "category_counts": dict(sorted(category_counts.items())),
        "frozen_probe_sha256_unchanged": sha256_file(probe_file),
    },
}

source_manifest_path.write_text(
    json.dumps(source_manifest, indent=2, ensure_ascii=False) + "\n",
    encoding=utf8,
)

print("SOURCE INGEST: PASS")
print(f"Source SHA-256: {source_manifest['sha256']}")
print(f"Paragraphs:     {source_manifest['paragraph_count']}")
print(f"Headings:       {source_manifest['heading_count']}")
print(f"Sections:       {source_manifest['section_count']}")
print(f"Media assets:   {source_manifest['embedded_media_count']}")
print(f"Benchmark:      {len(probes)} probes / {len(category_counts)} categories")
print(f"Manifest:       {source_manifest_path}")
'@

Write-Host "`nRepairing benchmark metadata and ingesting DOCX..."

# The benchmark probe file stays frozen; only the manifest metadata is repaired.
attrib -R $probeManifest

$extractCode | & $python - `
    $archivedDocx `
    $extractDir `
    $probeFile `
    $probeManifest

if ($LASTEXITCODE -ne 0) {
    throw "Chat-history ingestion failed."
}

# Restore read-only status on the frozen benchmark artifacts.
attrib +R $probeFile
attrib +R $probeManifest

if (Test-Path -LiteralPath $campaignYaml) {
    $yaml = [System.IO.File]::ReadAllText($campaignYaml)

    $fields = [ordered]@{
        chat_history_source_status = "raw_ingested_unreviewed"
        chat_history_source_id = "src-vera-chat-history-0001"
        benchmark_category_count = "12"
        next_required_action = "segment_and_review_high_value_teacher_interactions_from_chat_history_0001"
    }

    foreach ($entry in $fields.GetEnumerator()) {
        $pattern = "(?m)^" + [regex]::Escape($entry.Key) + ":\s*.*$"
        $replacement = "$($entry.Key): $($entry.Value)"

        if ($yaml -match $pattern) {
            $yaml = [regex]::Replace($yaml, $pattern, $replacement)
        }
        else {
            $yaml += "`r`n$replacement"
        }
    }

    [System.IO.File]::WriteAllText(
        $campaignYaml,
        $yaml.TrimEnd() + "`r`n",
        [System.Text.UTF8Encoding]::new($false)
    )
}

Write-Host "`n=== INGEST COMPLETE ==="
Write-Host "Source archive: $archivedDocx"
Write-Host "Extraction:     $extractDir"
Write-Host "Status:         RAW SOURCE INGESTED, NOT TRAINING-APPROVED"
Write-Host "Next:           Segment and review high-value teacher interactions."
