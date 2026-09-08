
from pathlib import Path
import hashlib


# ============================================================
# DATASET FOLDERS
# ============================================================

DATASET_FOLDERS = [
    Path(r"C:\Users\HomePC\Documents\images\cropped"),
    Path(r"C:\Users\HomePC\Documents\images\numbered"),
    Path(r"C:\Users\HomePC\Documents\images\raw_images"),
]


# ============================================================
# SUPPORTED IMAGE FORMATS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}


# ============================================================
# CREATE FILE HASH
# ============================================================

def calculate_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash for a file.
    """

    hasher = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


# ============================================================
# FIND DUPLICATES
# ============================================================

def find_duplicates():

    print("\n" + "=" * 60)
    print("FISH DATASET DUPLICATE SCANNER")
    print("=" * 60 + "\n")

    # Store hash -> list of files
    file_hashes = {}

    total_images = 0

    # --------------------------------------------------------
    # SCAN FOLDERS
    # --------------------------------------------------------

    for folder in DATASET_FOLDERS:

        print(f"Scanning: {folder}")

        if not folder.exists():

            print("WARNING: Folder does not exist!\n")

            continue

        for file_path in folder.rglob("*"):

            if (
                file_path.is_file()
                and file_path.suffix.lower()
                in IMAGE_EXTENSIONS
            ):

                total_images += 1

                try:

                    file_hash = calculate_hash(
                        file_path
                    )

                    if file_hash not in file_hashes:

                        file_hashes[file_hash] = []

                    file_hashes[file_hash].append(
                        file_path
                    )

                except Exception as error:

                    print(
                        f"Could not read: {file_path}"
                    )

                    print(
                        f"Error: {error}"
                    )

    # --------------------------------------------------------
    # FIND DUPLICATE GROUPS
    # --------------------------------------------------------

    duplicate_groups = {

        file_hash: files

        for file_hash, files

        in file_hashes.items()

        if len(files) > 1
    }

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)

    print(
        f"\nTotal images scanned: "
        f"{total_images}"
    )

    print(
        f"Duplicate groups found: "
        f"{len(duplicate_groups)}"
    )

    # --------------------------------------------------------
    # SAVE REPORT
    # --------------------------------------------------------

    report_path = Path(
        "duplicate_report.txt"
    )

    duplicate_file_count = 0

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "FISH DATASET DUPLICATE REPORT\n"
        )

        report.write(
            "=" * 60 + "\n\n"
        )

        report.write(
            f"Total images scanned: "
            f"{total_images}\n"
        )

        report.write(
            f"Duplicate groups found: "
            f"{len(duplicate_groups)}\n\n"
        )

        for index, (
            file_hash,
            files

        ) in enumerate(
            duplicate_groups.items(),
            start=1
        ):

            report.write(
                f"\nDUPLICATE GROUP {index}\n"
            )

            report.write(
                "-" * 50 + "\n"
            )

            for file_path in files:

                report.write(
                    f"{file_path}\n"
                )

            # All except one file
            # are duplicates.

            duplicate_file_count += (
                len(files) - 1
            )

    print(
        f"Duplicate files: "
        f"{duplicate_file_count}"
    )

    print(
        f"\nReport saved as: "
        f"{report_path.resolve()}"
    )

    print(
        "\nIMPORTANT: "
        "No images were deleted."
    )

    print("\n" + "=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    find_duplicates()
