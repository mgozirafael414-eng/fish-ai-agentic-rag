
from pathlib import Path
import random
import shutil
import csv


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = Path(
    r"C:\Users\HomePC\Documents\fish_dataset_clean"
)

OUTPUT_DIR = Path(
    r"C:\Users\HomePC\Documents\fish_dataset_split"
)

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


# ============================================================
# SPLIT POLICY
# ============================================================

def calculate_split(count):
    """
    Calculate train / validation / test distribution.

    Important:
    We NEVER duplicate images between splits.
    """

    if count == 1:
        return 1, 0, 0

    if count == 2:
        return 1, 0, 1

    if count == 3:
        return 1, 1, 1

    if count == 4:
        return 2, 1, 1

    if count == 5:
        return 3, 1, 1

    if count == 6:
        return 4, 1, 1

    if count == 7:
        return 5, 1, 1

    if count == 8:
        return 6, 1, 1

    if count == 9:
        return 7, 1, 1

    # 10 or more
    train_count = round(count * 0.70)
    val_count = round(count * 0.15)
    test_count = count - train_count - val_count

    if val_count < 1:
        val_count = 1

    if test_count < 1:
        test_count = 1

    train_count = count - val_count - test_count

    return train_count, val_count, test_count


# ============================================================
# FIND IMAGES
# ============================================================

def get_class_images(class_dir):
    """
    Return valid images from a class directory.
    """

    images = []

    for file in class_dir.iterdir():

        if (
            file.is_file()
            and file.suffix.lower() in IMAGE_EXTENSIONS
        ):
            images.append(file)

    return images


# ============================================================
# COPY IMAGE
# ============================================================

def copy_image(source, destination_dir):

    destination_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = destination_dir / source.name

    shutil.copy2(
        source,
        destination
    )


# ============================================================
# CREATE ALL CLASS DIRECTORIES
# ============================================================

def create_class_directories(
    class_dirs,
    train_dir,
    val_dir,
    test_dir
):
    """
    Create every class folder in all three splits.

    This is important because torchvision ImageFolder
    builds class_to_idx from folder names.
    """

    for class_dir in class_dirs:

        class_name = class_dir.name

        (train_dir / class_name).mkdir(
            parents=True,
            exist_ok=True
        )

        (val_dir / class_name).mkdir(
            parents=True,
            exist_ok=True
        )

        (test_dir / class_name).mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FISH DATASET TRAIN / VALIDATION / TEST SPLITTER")
    print("=" * 70)

    print()
    print(f"Source dataset : {SOURCE_DIR}")
    print(f"Output dataset : {OUTPUT_DIR}")
    print(f"Random seed    : {RANDOM_SEED}")
    print()

    # ========================================================
    # CHECK SOURCE
    # ========================================================

    if not SOURCE_DIR.exists():

        print("ERROR:")
        print("Source dataset does not exist:")
        print(SOURCE_DIR)

        return

    # ========================================================
    # PROTECT AGAINST OVERWRITE
    # ========================================================

    if OUTPUT_DIR.exists():

        print("ERROR:")
        print("Output directory already exists:")
        print(OUTPUT_DIR)

        print()
        print(
            "Delete the existing fish_dataset_split folder "
            "before running this corrected splitter."
        )

        return

    # ========================================================
    # CREATE OUTPUT DIRECTORIES
    # ========================================================

    train_dir = OUTPUT_DIR / "train"
    val_dir = OUTPUT_DIR / "val"
    test_dir = OUTPUT_DIR / "test"

    train_dir.mkdir(parents=True)
    val_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)

    # ========================================================
    # RANDOM GENERATOR
    # ========================================================

    rng = random.Random(RANDOM_SEED)

    # ========================================================
    # FIND CLASS DIRECTORIES
    # ========================================================

    class_dirs = sorted(
        [
            item
            for item in SOURCE_DIR.iterdir()
            if item.is_dir()
        ],
        key=lambda x: x.name.lower()
    )

    print(
        f"Species/classes found: {len(class_dirs)}"
    )

    print()

    # ========================================================
    # CREATE EVERY CLASS IN ALL SPLITS
    # ========================================================

    print("Creating class directories...")

    create_class_directories(
        class_dirs,
        train_dir,
        val_dir,
        test_dir
    )

    print("Class directory structure created.")
    print()

    # ========================================================
    # REPORT DATA
    # ========================================================

    report_rows = []

    total_images = 0
    total_train = 0
    total_val = 0
    total_test = 0

    single_image_classes = 0
    two_image_classes = 0
    low_count_classes = 0

    # ========================================================
    # PROCESS EACH CLASS
    # ========================================================

    for index, class_dir in enumerate(
        class_dirs,
        start=1
    ):

        class_name = class_dir.name

        images = get_class_images(
            class_dir
        )

        image_count = len(images)

        # ----------------------------------------------------
        # EMPTY CLASS
        # ----------------------------------------------------

        if image_count == 0:

            report_rows.append(
                {
                    "class": class_name,
                    "total": 0,
                    "train": 0,
                    "val": 0,
                    "test": 0,
                    "status": "EMPTY_CLASS",
                }
            )

            continue

        # ----------------------------------------------------
        # SHUFFLE
        # ----------------------------------------------------

        rng.shuffle(images)

        # ----------------------------------------------------
        # CALCULATE SPLIT
        # ----------------------------------------------------

        (
            train_count,
            val_count,
            test_count
        ) = calculate_split(
            image_count
        )

        # ----------------------------------------------------
        # SPLIT IMAGES
        # ----------------------------------------------------

        train_images = images[
            :train_count
        ]

        val_start = train_count

        val_end = (
            train_count
            + val_count
        )

        val_images = images[
            val_start:val_end
        ]

        test_images = images[
            val_end:
            val_end + test_count
        ]

        # ----------------------------------------------------
        # COPY TRAIN
        # ----------------------------------------------------

        for image in train_images:

            copy_image(
                image,
                train_dir / class_name
            )

        # ----------------------------------------------------
        # COPY VALIDATION
        # ----------------------------------------------------

        for image in val_images:

            copy_image(
                image,
                val_dir / class_name
            )

        # ----------------------------------------------------
        # COPY TEST
        # ----------------------------------------------------

        for image in test_images:

            copy_image(
                image,
                test_dir / class_name
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if image_count == 1:

            status = "SINGLE_IMAGE_CLASS"

            single_image_classes += 1

        elif image_count == 2:

            status = "TWO_IMAGE_CLASS"

            two_image_classes += 1

        elif image_count < 10:

            status = "LOW_COUNT_CLASS"

            low_count_classes += 1

        else:

            status = "NORMAL_SPLIT"

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        report_rows.append(
            {
                "class": class_name,
                "total": image_count,
                "train": train_count,
                "val": val_count,
                "test": test_count,
                "status": status,
            }
        )

        total_images += image_count
        total_train += train_count
        total_val += val_count
        total_test += test_count

        # ----------------------------------------------------
        # PROGRESS
        # ----------------------------------------------------

        print(
            f"[{index:03d}/{len(class_dirs):03d}] "
            f"{class_name:<45} "
            f"total={image_count:<3} "
            f"train={train_count:<3} "
            f"val={val_count:<2} "
            f"test={test_count:<2}"
        )

    # ========================================================
    # REPORT DIRECTORY
    # ========================================================

    reports_dir = OUTPUT_DIR / "reports"

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ========================================================
    # SAVE SPLIT REPORT
    # ========================================================

    report_file = (
        reports_dir / "split_report.csv"
    )

    with report_file.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "class",
                "total",
                "train",
                "val",
                "test",
                "status",
            ]
        )

        writer.writeheader()

        writer.writerows(
            report_rows
        )

    # ========================================================
    # SAVE SUMMARY
    # ========================================================

    summary_file = (
        reports_dir / "split_summary.txt"
    )

    with summary_file.open(
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "FISH DATASET SPLIT SUMMARY\n"
        )

        file.write(
            "=" * 60 + "\n\n"
        )

        file.write(
            f"Total classes: {len(class_dirs)}\n"
        )

        file.write(
            f"Total images: {total_images}\n\n"
        )

        file.write(
            f"Training images: {total_train}\n"
        )

        file.write(
            f"Validation images: {total_val}\n"
        )

        file.write(
            f"Testing images: {total_test}\n\n"
        )

        file.write(
            f"Single-image classes: "
            f"{single_image_classes}\n"
        )

        file.write(
            f"Two-image classes: "
            f"{two_image_classes}\n"
        )

        file.write(
            f"Other low-count classes (<10): "
            f"{low_count_classes}\n"
        )

        file.write(
            f"\nRandom seed: {RANDOM_SEED}\n"
        )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()

    print("=" * 70)
    print("DATASET SPLIT COMPLETED")
    print("=" * 70)

    print()

    print(
        f"Total classes      : "
        f"{len(class_dirs)}"
    )

    print(
        f"Total images       : "
        f"{total_images}"
    )

    print()

    print(
        f"Training images    : "
        f"{total_train}"
    )

    print(
        f"Validation images  : "
        f"{total_val}"
    )

    print(
        f"Testing images     : "
        f"{total_test}"
    )

    print()

    print(
        f"Single-image class : "
        f"{single_image_classes}"
    )

    print(
        f"Two-image classes  : "
        f"{two_image_classes}"
    )

    print(
        f"Low-count classes  : "
        f"{low_count_classes}"
    )

    print()

    print("Dataset created at:")
    print(OUTPUT_DIR)

    print()

    print("Train:")
    print(train_dir)

    print()

    print("Validation:")
    print(val_dir)

    print()

    print("Test:")
    print(test_dir)

    print()

    print("Reports:")
    print(report_file)
    print(summary_file)

    print()

    print("IMPORTANT:")
    print(
        "- Original clean dataset was NOT modified."
    )

    print(
        "- Images were COPIED, not moved."
    )

    print(
        "- Classes with very few images were NOT deleted."
    )

    print(
        "- Empty class folders may exist in some splits."
    )

    print(
        "- We have NOT trained the model yet."
    )

    print()

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
