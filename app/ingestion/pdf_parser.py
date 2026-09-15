import os
import pdfplumber
import sys

LINE_TOP_TOLERANCE = 3
MIN_COLUMN_GAP = 8
MIN_GAP_FRACTION = 0.25
COLUMN_CLUSTER_TOLERANCE = 25
MIN_SIDE_FRACTION = 0.20

def group_words_into_lines(words):
    lines = []

    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        for line in lines:
            if abs(line[0]["top"] - word["top"]) < LINE_TOP_TOLERANCE:
                line.append(word)
                break
        else:
            lines.append([word])

    return lines

def detect_column_split(words, page_width):
    if not words:
        return None

    lines = group_words_into_lines(words)

    if len(lines) < 4:
        return None

    min_x = page_width * 0.30
    max_x = page_width * 0.70

    candidates = []

    for line in lines:
        words_on_line = sorted(line, key=lambda w: w["x0"])

        if len(words_on_line) < 2:
            continue

        largest_gap = 0
        gap_position = None

        for left, right in zip(words_on_line, words_on_line[1:]):
            gap = right["x0"] - left["x1"]
            midpoint = (left["x1"] + right["x0"]) / 2

            if gap > largest_gap:
                largest_gap = gap
                gap_position = midpoint

        if (
            largest_gap >= MIN_COLUMN_GAP
            and gap_position is not None
            and min_x <= gap_position <= max_x
        ):
            candidates.append(gap_position)

    if len(candidates) / len(lines) < MIN_GAP_FRACTION:
        return None

    candidates.sort()
    median = candidates[len(candidates) // 2]

    clustered = [
        x for x in candidates
        if abs(x - median) <= COLUMN_CLUSTER_TOLERANCE
    ]

    if len(clustered) / len(lines) < MIN_GAP_FRACTION:
        return None

    split_x = sum(clustered) / len(clustered)

    left_count = sum(w["x0"] < split_x for w in words)
    right_count = len(words) - left_count

    total = len(words)

    if left_count / total < MIN_SIDE_FRACTION:
        return None

    if right_count / total < MIN_SIDE_FRACTION:
        return None

    return split_x

def words_to_text(words):
    words = sorted(words, key=lambda w: (round(w["top"]), w["x0"]))

    lines = []
    current_line = []
    current_top = None

    for word in words:
        top = round(word["top"])

        if current_top is not None:
            if abs(top - current_top) > LINE_TOP_TOLERANCE:
                lines.append(" ".join(current_line))
                current_line = []

        current_line.append(word["text"])
        current_top = top

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)

def extract_page_text(page):
    page = page.filter(
        lambda obj: (
            obj.get("object_type") != "char"
            or obj.get("upright", True)
        )
    )

    words = page.extract_words(x_tolerance=1.5)
    split_x = detect_column_split(words, page.width)

    if split_x is None:
        return page.extract_text(
            x_tolerance=1.5,
            y_tolerance=3
        ) or ""

    left_words = [
        word for word in words
        if word["x0"] < split_x
    ]

    right_words = [
        word for word in words
        if word["x0"] >= split_x
    ]

    left_text = words_to_text(left_words)
    right_text = words_to_text(right_words)

    return left_text + "\n" + right_text

def parse_pdf(pdf_path):
    source_file = os.path.basename(pdf_path)
    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = extract_page_text(page)

            pages.append({
                "source_file": source_file,
                "page_num": page_num,
                "text": text,
            })

    return pages

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    pages = parse_pdf(pdf_path)

    print(f"Parsed {len(pages)} pages")
    print(f"Source: {os.path.basename(pdf_path)}")

    if pages:
        print("\n--- Page 1 ---")
        print(pages[0]["text"][:500])