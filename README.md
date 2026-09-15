# PURA website: how to update and publish it

This is the Quarto source for [kohker.org](https://kohker.org). Edit the `.qmd` files in this repository; Quarto builds the website into `docs/`. GitHub Pages serves `docs/` from the `main` branch after you push it. The `CNAME` file keeps the custom domain attached. **You do not need `quarto publish` for this site.**

Run the commands below in PowerShell from the repository root.

For text-only edits, you need Quarto, Python (only if regenerating the gallery), and Git. Media uploads also need the local `urban-modelling` Conda environment with Pillow and the configured rclone executable in `scripts/`.

## The usual build-and-publish routine

1. Edit the relevant `.qmd` source files. If you added project photos, run the media sync described below first.
2. If you changed `media/gallery-objects.txt`, regenerate the gallery:

   ```powershell
   python generate_photos_page.py
   ```

3. Build the site and review the changed files:

   ```powershell
   quarto render
   git status --short
   ```

4. Commit the source **and** generated `docs/` files, then push:

   ```powershell
   git add .
   git commit -m "Update site"
   git push origin main
   ```

Use a more specific commit message if you can. If `git status --short` shows no changes after rendering, there is nothing new to commit. The live site may take a little time to update after the push.

## Where things live

| What | File or folder |
| --- | --- |
| Home page | `index.qmd` |
| Team page | `team.qmd` |
| Publication cards | `publications.qmd` |
| Update cards | `updates.qmd` |
| Individual update articles | `updates/*.qmd` |
| Gallery image list | `media/gallery-objects.txt` |
| Generated gallery page | `photos.qmd` |
| Site navigation and output settings | `_quarto.yml` |
| Card and page styling | `styles.css` |
| Built website, committed to Git | `docs/` |

The website domain is `kohker.org`. Project photos are served from the Cloudflare R2 bucket `kohker-media` through **`https://media.wccarleton.org`**. This image hostname is separate from the website domain. For example, local `images/fieldwork/photo.jpg` becomes `https://media.wccarleton.org/fieldwork/photo.jpg` after syncing. The R2 S3 API URL is for tools, not for links on the website.

## Add a publication

1. Open `publications.qmd` and copy the existing `<article class="publication-card">...</article>` block. Add the new block inside `<div class="publication-grid">` with the correct title, authors, year, journal, article URL, and image alt text. The cards are laid out for phones by `styles.css`.
2. Use a suitable image you have permission to display. A project image can go through R2 as described below; link to its public `https://media.wccarleton.org/...` URL. If you use a publisher-hosted image, check that it is permitted and actually loads on the live site.
3. If there is a related project story, create its `.qmd` file under `updates/`, add a card for it to `updates.qmd`, and point the publication card's `publication-update-link` to its rendered `updates/your-story.html`. A short “coming soon” article is fine until the story is ready.
4. Run `quarto render`, check the publication card and both links, then commit and push using the routine above.

## Add or revise an update

1. Create `updates/update-your-topic.qmd` for a new article, or edit an existing article there. Follow an existing article's heading and `[← All field updates](../updates.qmd)` back link. Write the article in Quarto Markdown.
2. Add or edit its card in `updates.qmd`. Copy an existing `<article class="update-card">...</article>` block inside the raw HTML section. Set its image, category/date, title, short description, and links. Links from the card use the rendered path `updates/update-your-topic.html`.
3. If the update is about a publication, link to the article from the update and link back to the update from its publication card.
4. For project photos in the article, sync them to R2 first and use their public `https://media.wccarleton.org/...` URLs. Add useful alt text or captions. Render, open the card and article, then commit and push.

The update articles are separate files under `updates/`; the card list on `updates.qmd` is maintained manually. Adding an article file alone does **not** add its card.

## Add gallery or other project photos

1. Put local files under `images/fieldwork/` or another project folder within `images/`. These project files stay on your computer and are ignored by Git. Keep the handful of core map and partner-logo assets in Git.
2. Prepare and upload project media:

   ```powershell
   powershell -File scripts/sync-media.ps1
   ```

   The script uses the local `urban-modelling` Conda environment with Pillow and the local rclone executable/configuration. It leaves images at or below **2000 pixels on each edge and 1 MB** alone. Larger images are resized and recompressed before upload; full-resolution originals are archived locally in `media-originals/`, which is not uploaded or tracked by Git. JPEG names stay the same. Oversized PNGs become `.webp`, so use the new filename in site links. The core map and logos are excluded from the R2 upload.
3. For a gallery image, add one object key per line to `media/gallery-objects.txt`, such as `fieldwork/photo.jpg`. Use the **post-sync** filename if conversion changed it. Then run `python generate_photos_page.py` to rebuild `photos.qmd`.
4. Check a new image's public URL in a browser before publishing the page. Run `quarto render`, then commit and push.

See [media/README.md](media/README.md) for a shorter explanation of the media setup. The sync script uses `rclone copy`, so it does not remove old objects from R2. It also never uploads `media-originals/`.

## Change the navigation or add a page

Create or edit a `.qmd` file in the repository, then add its link under `website.navbar` in `_quarto.yml` if it should appear in the top navigation. Run `quarto render` and commit both the source and `docs/` output.

## Update the team page

Edit `team.qmd` to change a profile or copy one of its existing grid blocks to add a person. Put a new portrait in `images/`, sync it to R2, and use its public media URL in the profile. Render and check the page on a narrow screen before committing and pushing.

## If something looks wrong

- **The live site still shows old text:** check that you ran `quarto render` and committed the changed `docs/` files before pushing.
- **An R2 image is missing:** check its exact object key and extension against the public `https://media.wccarleton.org/...` URL. If a PNG became WebP, update the link. Run the sync script again if it was never uploaded.
- **A new gallery photo is absent:** add its key to `media/gallery-objects.txt`, regenerate `photos.qmd`, render, and push.
- **A new update article is absent from the card list:** add its card to `updates.qmd` and link to the article's `.html` path.
- **The custom website domain stops working:** keep `CNAME` set to `kohker.org`; Quarto copies it into `docs/CNAME`. The domain's DNS and GitHub Pages settings are managed outside this repository.
