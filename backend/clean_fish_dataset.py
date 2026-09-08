
import csv
import hashlib
import re
import shutil
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_ROOT = Path(r"C:\Users\HomePC\Documents\images")

CROPPED_DIR = SOURCE_ROOT / "cropped"
RAW_DIR = SOURCE_ROOT / "raw_images"

# IMPORTANT:
# This is a NEW directory.
# Original dataset will NOT be modified.
OUTPUT_DIR = Path(r"C:\Users\HomePC\Documents\fish_dataset_clean")

REPORT_DIR = OUTPUT_DIR / "reports"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
    ".tif",
    ".tiff",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_sha256(file_path: Path) -> str:
    """
    Calculate SHA-256 hash for an image.
    Used to detect exact duplicate files.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def normalize_species(species: str) -> str:
    """
    Normalize species names conservatively.

    Examples:

    acanthopagrus _latus
        ->
    acanthopagrus_latus

    gymnocranius_ microdon
        ->
    gymnocranius_microdon
    """

    species = species.strip()

    # Convert repeated spaces to one space
    species = re.sub(r"\s+", " ", species)

    # Remove spaces around underscore
    species = re.sub(r"\s*_\s*", "_", species)

    # Replace remaining spaces with underscore
    species = species.replace(" ", "_")

    # Remove repeated underscores
    species = re.sub(r"_+", "_", species)

    # Lowercase for consistent directory names
    species = species.lower()

    return species


def extract_species(file_path: Path):
    """
    Extract species name from filenames such as:

        acanthaluteres_brownii_1.png
        acanthistius_cinctus_25.jpg

    Expected pattern:

        species_number.extension
    """

    stem = file_path.stem.strip()

    match = re.match(r"^(?P<species>.+)_(?P<number>\d+)$", stem)

    if not match:
        return None

    species = match.group("species")

    return normalize_species(species)


def is_image(file_path: Path) -> bool:
    """
    Check whether file is a supported image.
    """

    return file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS


def safe_copy(source: Path, destination: Path):
    """
    Copy image while preserving original.
    """

    destination.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source, destination)


# ============================================================
# MAIN CLEANING FUNCTION
# ============================================================

def main():

    print("=" * 70)
    print("FISH DATASET CLEANING & DEDUPLICATION")
    print("=" * 70)

    print()
    print(f"Source: {SOURCE_ROOT}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # --------------------------------------------------------
    # Validate source folders
    # --------------------------------------------------------

    if not CROPPED_DIR.exists():
        print(f"ERROR: Folder not found:")
        print(CROPPED_DIR)
        return

    if not RAW_DIR.exists():
        print(f"ERROR: Folder not found:")
        print(RAW_DIR)
        return

    # --------------------------------------------------------
    # Create output folders
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # IMPORTANT SAFETY CHECK
    # --------------------------------------------------------

    if OUTPUT_DIR.resolve() == SOURCE_ROOT.resolve():
        print("ERROR: Output directory cannot be source directory.")
        return

    # --------------------------------------------------------
    # Collect images
    # --------------------------------------------------------

    source_directories = [
        ("cropped", CROPPED_DIR),
        ("raw_images", RAW_DIR),
    ]

    all_images = []

    print("Scanning source folders...")
    print()

    for source_name, source_dir in source_directories:

        print(f"Scanning: {source_dir}")

        images = [
            path
            for path in source_dir.rglob("*")
            if is_image(path)
        ]

        print(f"Images found: {len(images)}")
        print()

        for image_path in images:
            all_images.append(
                {
                    "source": source_name,
                    "path": image_path,
                }
            )

    print("=" * 70)
    print(f"TOTAL CANDIDATE IMAGES: {len(all_images)}")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    seen_hashes = {}

    class_counts = Counter()

    duplicate_count = 0
    invalid_filename_count = 0
    copied_count = 0

    report_rows = []

    # --------------------------------------------------------
    # Process cropped first
    #
    # This means if the same exact image exists in cropped
    # and raw_images, cropped gets priority.
    # --------------------------------------------------------

    for index, item in enumerate(all_images, start=1):

        source_name = item["source"]
        image_path = item["path"]

        print(
            f"[{index}/{len(all_images)}] "
            f"Processing: {image_path.name}"
        )

        # ----------------------------------------------------
        # Extract species
        # ----------------------------------------------------

        species = extract_species(image_path)

        if species is None:

            invalid_filename_count += 1

            report_rows.append(
                {
                    "source": source_name,
                    "original_path": str(image_path),
                    "filename": image_path.name,
                    "species": "",
                    "sha256": "",
                    "status": "INVALID_FILENAME",
                    "clean_path": "",
                }
            )

            continue

        # ----------------------------------------------------
        # Calculate SHA-256
        # ----------------------------------------------------

        try:
            file_hash = calculate_sha256(image_path)

        except Exception as error:

            report_rows.append(
                {
                    "source": source_name,
                    "original_path": str(image_path),
                    "filename": image_path.name,
                    "species": species,
                    "sha256": "",
                    "status": f"HASH_ERROR: {error}",
                    "clean_path": "",
                }
            )

            continue

        # ----------------------------------------------------
        # Duplicate detection
        # ----------------------------------------------------

        if file_hash in seen_hashes:

            original = seen_hashes[file_hash]

            duplicate_count += 1

            report_rows.append(
                {
                    "source": source_name,
                    "original_path": str(image_path),
                    "filename": image_path.name,
                    "species": species,
                    "sha256": file_hash,
                    "status": "DUPLICATE",
                    "clean_path": original["clean_path"],
                }
            )

            print(
                f"    DUPLICATE -> "
                f"{original['original_path']}"
            )

            continue

        # ----------------------------------------------------
        # Create species directory
        # ----------------------------------------------------

        species_dir = OUTPUT_DIR / species

        species_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # Generate safe destination filename
        # ----------------------------------------------------

        destination = species_dir / image_path.name

        # Avoid accidental filename collision
        if destination.exists():

            counter = 1

            while True:

                new_name = (
                    f"{image_path.stem}_copy{counter}"
                    f"{image_path.suffix}"
                )

                candidate = species_dir / new_name

                if not candidate.exists():
                    destination = candidate
                    break

                counter += 1

        # ----------------------------------------------------
        # Copy image
        # ----------------------------------------------------

        try:

            safe_copy(
                image_path,
                destination
            )

            copied_count += 1

        except Exception as error:

            report_rows.append(
                {
                    "source": source_name,
                    "original_path": str(image_path),
                    "filename": image_path.name,
                    "species": species,
                    "sha256": file_hash,
                    "status": f"COPY_ERROR: {error}",
                    "clean_path": "",
                }
            )

            continue

        # ----------------------------------------------------
        # Save hash information
        # ----------------------------------------------------

        seen_hashes[file_hash] = {
            "source": source_name,
            "original_path": str(image_path),
            "clean_path": str(destination),
        }

        class_counts[species] += 1

        report_rows.append(
            {
                "source": source_name,
                "original_path": str(image_path),
                "filename": image_path.name,
                "species": species,
                "sha256": file_hash,
                "status": "COPIED",
                "clean_path": str(destination),
            }
        )

    # ========================================================
    # SAVE IMAGE REPORT
    # ========================================================

    image_report = REPORT_DIR / "dataset_cleaning_report.csv"

    with open(
        image_report,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source",
                "original_path",
                "filename",
                "species",
                "sha256",
                "status",
                "clean_path",
            ],
        )

        writer.writeheader()

        writer.writerows(report_rows)

    # ========================================================
    # SAVE CLASS COUNTS
    # ========================================================

    class_report = REPORT_DIR / "class_distribution.csv"

    sorted_classes = sorted(
        class_counts.items(),
        key=lambda x: (x[1], x[0])
    )

    with open(
        class_report,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "species",
                "image_count",
                "status",
            ]
        )

        for species, count in sorted_classes:

            if count < 10:
                status = "LOW_COUNT_REVIEW"

            else:
                status = "OK"

            writer.writerow(
                [
                    species,
                    count,
                    status,
                ]
            )

    # ========================================================
    # SAVE LOW COUNT CLASSES
    # ========================================================

    low_count_report = REPORT_DIR / "low_count_classes.txt"

    low_count_classes = [
        (species, count)
        for species, count in sorted_classes
        if count < 10
    ]

    with open(
        low_count_report,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "FISH DATASET - LOW COUNT CLASSES\n"
        )

        file.write(
            "=" * 60 + "\n\n"
        )

        for species, count in low_count_classes:

            file.write(
                f"{species}: {count} images\n"
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("CLEANING COMPLETED")
    print("=" * 70)

    print()
    print(f"Candidate images scanned : {len(all_images)}")
    print(f"Unique images copied     : {copied_count}")
    print(f"Duplicate images skipped : {duplicate_count}")
    print(f"Invalid filenames        : {invalid_filename_count}")
    print(f"Species/classes          : {len(class_counts)}")
    print(f"Low-count classes (<10)  : {len(low_count_classes)}")

    print()
    print("Clean dataset:")
    print(OUTPUT_DIR)

    print()
    print("Reports:")

    print(image_report)
    print(class_report)
    print(low_count_report)

    print()
    print("=" * 70)
    print("IMPORTANT")
    print("=" * 70)

    print(
        """
Original images were NOT deleted or moved.

The clean dataset was created in a NEW directory.

We have NOT removed low-count species yet.
They are only marked for review.

We have NOT trained a model yet.
"""
    )

    print("=" * 70)

    # ========================================================
    # TOP / BOTTOM CLASS SUMMARY
    # ========================================================

    print()
    print("CLASSES WITH FEWEST IMAGES")
    print("-" * 70)

    for species, count in sorted_classes[:30]:

        print(
            f"{species:<45} {count:>5}"
        )

    print()
    print("CLASSES WITH MOST IMAGES")
    print("-" * 70)

    for species, count in sorted(
        class_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:30]:

        print(
            f"{species:<45} {count:>5}"
        )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()
