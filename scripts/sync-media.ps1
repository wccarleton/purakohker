$ErrorActionPreference = "Stop"

# Repo root is the parent of /scripts
$repoRoot = Split-Path -Parent $PSScriptRoot

# Paths
$imageDir = Join-Path $repoRoot "images"
$archiveDir = Join-Path $repoRoot "media-originals"
$rclone   = Join-Path $PSScriptRoot "rclone-v1.75.1-windows-amd64\rclone.exe"

# Prepare web-sized copies before uploading. Full-resolution originals stay in
# media-originals/, outside the upload folder and outside Git.
conda run --no-capture-output -n urban-modelling python (Join-Path $PSScriptRoot "optimize-media.py") --images $imageDir --archive $archiveDir
if ($LASTEXITCODE -ne 0) { throw "Media optimization failed; upload cancelled." }

if (-not (Test-Path -LiteralPath $rclone)) { throw "rclone.exe is missing: $rclone" }

# Upload project media only; core branding remains in the GitHub site.
& $rclone copy $imageDir "r2:kohker-media" `
    --progress `
    --exclude "kk_site_area.png" `
    --exclude "kk_site_area.webp" `
    --exclude "kk_site_area_900.webp" `
    --exclude "logo_napv.png" `
    --exclude "logo_mpggea.jpg" `
    --exclude "Thumbs.db" `
    --exclude ".DS_Store"
if ($LASTEXITCODE -ne 0) { throw "R2 upload failed." }
