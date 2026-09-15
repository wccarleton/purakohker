The public image host is `https://media.wccarleton.org`. The `kohker-media` R2 bucket stores files with the same path relative to the local `images/` folder. For example, `images/fieldwork/photo.jpg` is served at `https://media.wccarleton.org/fieldwork/photo.jpg` after syncing.

Keep local media in `images/` for the local R2 sync script. Git ignores that folder except for the Koh Ker hero map and partner logos. The generated copies under `docs/images/` follow the same rule, so local files stay available while GitHub Pages serves gallery and team photos from R2.

For a new gallery photo, add its object key (such as `fieldwork/photo.jpg`) to `gallery-objects.txt`, then run `python generate_photos_page.py` and `quarto render`. For images in a post, use the public R2 URL directly in the `.qmd` file. Check that each new URL opens publicly before publishing the page.
