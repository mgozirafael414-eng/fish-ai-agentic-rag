
import os


# ==========================================
# PATHS
# ==========================================

CLEAN_DATASET = r"C:\Users\HomePC\Documents\fish_dataset_clean"
SPLIT_DATASET = r"C:\Users\HomePC\Documents\fish_dataset_split"

TRAIN_DIR = os.path.join(SPLIT_DATASET, "train")
VAL_DIR = os.path.join(SPLIT_DATASET, "val")
TEST_DIR = os.path.join(SPLIT_DATASET, "test")


# ==========================================
# GET CLASS FOLDERS
# ==========================================

def get_classes(folder):
    if not os.path.exists(folder):
        return set()

    return {
        name
        for name in os.listdir(folder)
        if os.path.isdir(os.path.join(folder, name))
        and name != "reports"
    }


# ==========================================
# GET IMAGE COUNT
# ==========================================

def count_images(folder):
    if not os.path.exists(folder):
        return 0

    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff",
    )

    count = 0

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(extensions):
                count += 1

    return count


# ==========================================
# COLLECT CLASSES
# ==========================================

clean_classes = get_classes(CLEAN_DATASET)

train_classes = get_classes(TRAIN_DIR)
val_classes = get_classes(VAL_DIR)
test_classes = get_classes(TEST_DIR)


split_classes = train_classes | val_classes | test_classes


# ==========================================
# DISPLAY COUNTS
# ==========================================

print("=" * 60)
print("FISHAI DATASET CLASS AUDIT")
print("=" * 60)

print("\nCLASS COUNTS")
print("-" * 60)

print(f"Clean dataset classes : {len(clean_classes)}")
print(f"Train classes        : {len(train_classes)}")
print(f"Validation classes   : {len(val_classes)}")
print(f"Test classes         : {len(test_classes)}")
print(f"Combined split       : {len(split_classes)}")


# ==========================================
# MISSING CLASSES
# ==========================================

missing_from_split = clean_classes - split_classes

extra_in_split = split_classes - clean_classes


print("\nCLASSES MISSING FROM SPLIT")
print("-" * 60)

if missing_from_split:
    for class_name in sorted(missing_from_split):
        print(class_name)
else:
    print("None")


print("\nEXTRA CLASSES IN SPLIT")
print("-" * 60)

if extra_in_split:
    for class_name in sorted(extra_in_split):
        print(class_name)
else:
    print("None")


# ==========================================
# EMPTY CLASSES
# ==========================================

print("\nEMPTY CLASSES")
print("-" * 60)

empty_train = []
empty_val = []
empty_test = []

for class_name in sorted(split_classes):

    train_count = count_images(
        os.path.join(TRAIN_DIR, class_name)
    )

    val_count = count_images(
        os.path.join(VAL_DIR, class_name)
    )

    test_count = count_images(
        os.path.join(TEST_DIR, class_name)
    )

    if train_count == 0:
        empty_train.append(class_name)

    if val_count == 0:
        empty_val.append(class_name)

    if test_count == 0:
        empty_test.append(class_name)


print(f"Empty train classes : {len(empty_train)}")
print(f"Empty val classes   : {len(empty_val)}")
print(f"Empty test classes  : {len(empty_test)}")


# ==========================================
# SHOW EMPTY VALIDATION CLASSES
# ==========================================

print("\nEMPTY VALIDATION CLASSES")
print("-" * 60)

if empty_val:
    for class_name in empty_val:
        print(class_name)
else:
    print("None")


# ==========================================
# SHOW EMPTY TEST CLASSES
# ==========================================

print("\nEMPTY TEST CLASSES")
print("-" * 60)

if empty_test:
    for class_name in empty_test:
        print(class_name)
else:
    print("None")


# ==========================================
# IMAGE COUNTS
# ==========================================

print("\nIMAGE COUNTS")
print("-" * 60)

print(
    f"Clean dataset images : "
    f"{count_images(CLEAN_DATASET)}"
)

print(
    f"Train images         : "
    f"{count_images(TRAIN_DIR)}"
)

print(
    f"Validation images    : "
    f"{count_images(VAL_DIR)}"
)

print(
    f"Test images          : "
    f"{count_images(TEST_DIR)}"
)


# ==========================================
# FINAL
# ==========================================

print("\n" + "=" * 60)
print("DATASET CLASS AUDIT COMPLETED")
print("=" * 60)
