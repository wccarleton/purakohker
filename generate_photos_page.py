import os

# Paths
image_folder = "images/fieldwork"
output_file = "photos.qmd"

# Header for the photos page
header = """---
title: Fieldwork Photos
lightbox: true
---

"""

# Collect image files
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
image_files.sort()

# Generate Markdown lines
lines = []
for img in image_files:
    path = f"{image_folder}/{img}"
    # Create lightbox link with group
    line = f'![]({path}){{group="my-gallery"}}'
    lines.append(line)

# Combine
content = header + "\n\n".join(lines) + "\n"

# Write file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated {output_file} with {len(image_files)} images, grouped as a gallery.")
