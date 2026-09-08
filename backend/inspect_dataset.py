
import os
import re
import hashlib
from pathlib import Path
from collections import Counter, defaultdict


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_FOLDERS = [
    Path(r"C:\Users\HomePC\Documents\images\cropped"),
    Path(r"C:\Users\HomePC\Documents\images\numbered"),
    Path(r"C:\Users\HomePC\Documents\images\raw_images"),
]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}

REPORT_FILE = Path("dataset_inspection_report.txt")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_image_file(path: Path):
    """Check whether a file is an image."""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def extract_species(filename: str):
    """
    Extract species name from filenames such as:

        acanthaluteres_brownii_1.png
        acanthaluteres_brownii_2.png
        A73EGS-P_1.png

    Expected pattern:

        species_name_number.extension
    """

    stem = Path(filename).stem

    # Remove the final _number
    match = re.match(r"^(?P<species>.+)_(?P<number>\d+)$", stem)

    if match:
        species = match.group("species")
        image_number = match.group("number")

        return species, image_number

    return None, None


def calculate_sha256(file_path: Path):
    """Calculate SHA-256 hash for duplicate detection."""

    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except Exception as error:
        print(f"Could not hash file: {file_path}")
        print(f"Error: {error}")

        return None


# ============================================================
# MAIN INSPECTION
# ============================================================

def main():

    print("=" * 70)
    print("FISHAI DATASET INSPECTOR")
    print("STEP 7.6.3B")
    print("=" * 70)

    all_images = []

    images_by_folder = Counter()
    images_by_extension = Counter()
    species_counter = Counter()

    species_by_folder = defaultdict(Counter)

    invalid_files = []

    hash_to_files = defaultdict(list)

    # ========================================================
    # SCAN DATASET
    # ========================================================

    for folder in DATASET_FOLDERS:

        print()
        print("-" * 70)
        print(f"SCANNING FOLDER:")
        print(folder)
        print("-" * 70)

        if not folder.exists():

            print("WARNING: Folder does not exist.")

            continue

        folder_images = 0

        for file_path in folder.rglob("*"):

            if not is_image_file(file_path):
                continue

            folder_images += 1

            all_images.append(file_path)

            # Folder statistics
            images_by_folder[folder.name] += 1

            # Extension statistics
            images_by_extension[file_path.suffix.lower()] += 1

            # ------------------------------------------------
            # Extract species
            # ------------------------------------------------

            species, image_number = extract_species(file_path.name)

            if species:

                species_counter[species] += 1

                species_by_folder[folder.name][species] += 1

            else:

                invalid_files.append(file_path)

            # ------------------------------------------------
            # Duplicate detection
            # ------------------------------------------------

            file_hash = calculate_sha256(file_path)

            if file_hash:

                hash_to_files[file_hash].append(file_path)

        print(f"Images found in folder: {folder_images}")

    # ========================================================
    # DUPLICATES
    # ========================================================

    duplicate_groups = {}

    duplicate_file_count = 0

    for file_hash, files in hash_to_files.items():

        if len(files) > 1:

            duplicate_groups[file_hash] = files

            # Keep one original.
            duplicate_file_count += len(files) - 1

    # ========================================================
    # REPORT SUMMARY
    # ========================================================

    total_images = len(all_images)

    total_species = len(species_counter)

    # ========================================================
    # DISPLAY SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)

    print(f"Total images scanned       : {total_images}")
    print(f"Unique species             : {total_species}")
    print(f"Duplicate groups           : {len(duplicate_groups)}")
    print(f"Duplicate files            : {duplicate_file_count}")
    print(f"Invalid filenames          : {len(invalid_files)}")

    # ========================================================
    # IMAGES BY FOLDER
    # ========================================================

    print()
    print("=" * 70)
    print("IMAGES BY SOURCE FOLDER")
    print("=" * 70)

    for folder_name, count in images_by_folder.items():

        print(f"{folder_name:<25}: {count}")

    # ========================================================
    # FILE EXTENSIONS
    # ========================================================

    print()
    print("=" * 70)
    print("FILE EXTENSIONS")
    print("=" * 70)

    for extension, count in sorted(images_by_extension.items()):

        print(f"{extension:<25}: {count}")

    # ========================================================
    # SPECIES DISTRIBUTION
    # ========================================================

    print()
    print("=" * 70)
    print("SPECIES DISTRIBUTION")
    print("=" * 70)

    if species_counter:

        for species, count in species_counter.most_common():

            print(f"{species:<45}: {count}")

    else:

        print("No species detected.")

    # ========================================================
    # SPECIES BY FOLDER
    # ========================================================

    print()
    print("=" * 70)
    print("SPECIES BY FOLDER")
    print("=" * 70)

    for folder_name in images_by_folder:

        print()
        print(f"[{folder_name}]")

        folder_species = species_by_folder.get(folder_name, {})

        for species, count in sorted(folder_species.items()):

            print(f"  {species:<43}: {count}")

    # ========================================================
    # SMALL CLASSES
    # ========================================================

    print()
    print("=" * 70)
    print("SPECIES WITH FEW IMAGES")
    print("=" * 70)

    small_classes = {
        species: count
        for species, count in species_counter.items()
        if count < 10
    }

    if small_classes:

        for species, count in sorted(
            small_classes.items(),
            key=lambda item: item[1]
        ):

            print(f"{species:<45}: {count}")

    else:

        print("No species with fewer than 10 images.")

    # ========================================================
    # INVALID FILENAMES
    # ========================================================

    print()
    print("=" * 70)
    print("INVALID FILENAMES")
    print("=" * 70)

    if invalid_files:

        for file_path in invalid_files[:100]:

            print(file_path)

        if len(invalid_files) > 100:

            print(
                f"... and {len(invalid_files) - 100} more invalid files."
            )

    else:

        print("No invalid filenames found.")

    # ========================================================
    # DUPLICATE GROUPS
    # ========================================================

    print()
    print("=" * 70)
    print("EXACT DUPLICATE GROUPS")
    print("=" * 70)

    if duplicate_groups:

        group_number = 1

        for file_hash, files in duplicate_groups.items():

            print()
            print(f"DUPLICATE GROUP {group_number}")
            print(f"SHA256: {file_hash}")

            for file_path in files:

                print(f"  {file_path}")

            group_number += 1

            # Avoid producing an extremely large terminal output
            if group_number > 50:

                remaining = len(duplicate_groups) - 49

                print()
                print(
                    f"... and {remaining} more duplicate groups."
                )

                break

    else:

        print("No exact duplicate groups found.")

    # ========================================================
    # TRAINING DATA ANALYSIS
    # ========================================================

    usable_images = total_images - len(invalid_files)

    print()
    print("=" * 70)
    print("PRELIMINARY TRAINING DATA ANALYSIS")
    print("=" * 70)

    print(f"Total image files           : {total_images}")
    print(f"Potential usable images     : {usable_images}")
    print(f"Potential excluded images   : {len(invalid_files)}")
    print(f"Detected species/classes    : {total_species}")

    print()
    print("IMPORTANT:")
    print("No files were deleted.")
    print("No files were moved.")
    print("No dataset structure was changed.")
    print("This is inspection only.")

    # ========================================================
    # SAVE REPORT
    # ========================================================

    with open(REPORT_FILE, "w", encoding="utf-8") as report:

        report.write("=" * 70 + "\n")
        report.write("FISHAI DATASET INSPECTION REPORT\n")
        report.write("STEP 7.6.3B\n")
        report.write("=" * 70 + "\n\n")

        report.write("DATASET SUMMARY\n")
        report.write("-" * 70 + "\n")

        report.write(
            f"Total images scanned: {total_images}\n"
        )

        report.write(
            f"Unique species: {total_species}\n"
        )

        report.write(
            f"Duplicate groups: {len(duplicate_groups)}\n"
        )

        report.write(
            f"Duplicate files: {duplicate_file_count}\n"
        )

        report.write(
            f"Invalid filenames: {len(invalid_files)}\n"
        )

        report.write("\n")

        report.write("IMAGES BY FOLDER\n")
        report.write("-" * 70 + "\n")

        for folder_name, count in images_by_folder.items():

            report.write(
                f"{folder_name}: {count}\n"
            )

        report.write("\n")

        report.write("FILE EXTENSIONS\n")
        report.write("-" * 70 + "\n")

        for extension, count in sorted(
            images_by_extension.items()
        ):

            report.write(
                f"{extension}: {count}\n"
            )

        report.write("\n")

        report.write("SPECIES DISTRIBUTION\n")
        report.write("-" * 70 + "\n")

        for species, count in species_counter.most_common():

            report.write(
                f"{species}: {count}\n"
            )

        report.write("\n")

        report.write("SPECIES WITH FEW IMAGES\n")
        report.write("-" * 70 + "\n")

        if small_classes:

            for species, count in sorted(
                small_classes.items(),
                key=lambda item: item[1]
            ):

                report.write(
                    f"{species}: {count}\n"
                )

        else:

            report.write(
                "No species with fewer than 10 images.\n"
            )

        report.write("\n")

        report.write("INVALID FILENAMES\n")
        report.write("-" * 70 + "\n")

        if invalid_files:

            for file_path in invalid_files:

                report.write(
                    f"{file_path}\n"
                )

        else:

            report.write(
                "No invalid filenames found.\n"
            )

        report.write("\n")

        report.write("DUPLICATE GROUPS\n")
        report.write("-" * 70 + "\n")

        if duplicate_groups:

            group_number = 1

            for file_hash, files in duplicate_groups.items():

                report.write(
                    f"\nDUPLICATE GROUP {group_number}\n"
                )

                report.write(
                    f"SHA256: {file_hash}\n"
                )

                for file_path in files:

                    report.write(
                        f"  {file_path}\n"
                    )

                group_number += 1

        else:

            report.write(
                "No exact duplicate groups found.\n"
            )

        report.write("\n")

        report.write("TRAINING DATA ANALYSIS\n")
        report.write("-" * 70 + "\n")

        report.write(
            f"Total images: {total_images}\n"
        )

        report.write(
            f"Potential usable images: {usable_images}\n"
        )

        report.write(
            f"Potential excluded images: {len(invalid_files)}\n"
        )

        report.write(
            f"Detected species/classes: {total_species}\n"
        )

        report.write("\n")

        report.write(
            "No files were deleted.\n"
        )

        report.write(
            "No files were moved.\n"
        )

        report.write(
            "No dataset structure was changed.\n"
        )

    # ========================================================
    # FINISHED
    # ========================================================

    print()
    print("=" * 70)
    print("INSPECTION COMPLETED")
    print("=" * 70)

    print()
    print("Report saved to:")
    print(REPORT_FILE.resolve())

    print()
    print("No files were deleted or moved.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
