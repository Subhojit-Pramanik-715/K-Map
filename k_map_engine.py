# =========================================================
# 4-VARIABLE K-MAP SIMPLIFIER ENGINE
# =========================================================

# =========================================================
# 1. K-MAP LAYOUT
# =========================================================

KMAP = [
    [0, 1, 3, 2],
    [4, 5, 7, 6],
    [12, 13, 15, 14],
    [8, 9, 11, 10]
]

GROUP_SHAPES = [
    (1, 1),
    (1, 2),
    (1, 4),
    (2, 1),
    (2, 2),
    (2, 4),
    (4, 1),
    (4, 2),
    (4, 4)
]


# =========================================================
# 2. CREATE K-MAP VALUES
# =========================================================

def create_kmap_values(minterms):
    kmap_values = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    for row in range(4):
        for column in range(4):
            minterm = KMAP[row][column]

            # Mark the K-map cell as 1 if its minterm is required.

            if minterm in minterms:
                kmap_values[row][column] = 1

    return kmap_values


# =========================================================
# 3. FIND POSITION OF A MINTERM
# =========================================================

def find_position(minterm):
    for row in range(4):
        for column in range(4):

            # Return the row and column where the minterm is located.

            if KMAP[row][column] == minterm:
                return (row, column)

    return None


# =========================================================
# 4. GET NEIGHBOR MINTERMS
# =========================================================

def get_neighbor_minterms(row, column):
    neighbors = []

    # Calculate neighboring positions using wrap-around.

    up = (row - 1) % 4
    down = (row + 1) % 4
    left = (column - 1) % 4
    right = (column + 1) % 4

    neighbors.append(KMAP[up][column])
    neighbors.append(KMAP[down][column])
    neighbors.append(KMAP[row][left])
    neighbors.append(KMAP[row][right])

    return neighbors


# =========================================================
# 5. GENERATE GROUP CELLS
# =========================================================

def get_group_cells(start_row, start_column, height, width):
    cells = []

    for row_offset in range(height):
        for column_offset in range(width):
            # Use modulo 4 so groups can wrap around K-map edges.
            row = (start_row + row_offset) % 4
            column = (start_column + column_offset) % 4

            cells.append((row, column))

    return cells


# =========================================================
# 6. CHECK WHETHER A GROUP IS VALID
# =========================================================

def is_valid_group(cells, kmap_values):
    for row, column in cells:

        # A valid group may contain only cells whose K-map value is 1.

        if kmap_values[row][column] != 1:
            return False

    return True


# =========================================================
# 7. FIND ALL VALID GROUPS
# =========================================================

def find_valid_groups(kmap_values):
    groups = set()

    for height, width in GROUP_SHAPES:
        for start_row in range(4):
            for start_column in range(4):
                cells = get_group_cells(
                    start_row,
                    start_column,
                    height,
                    width
                )

                # Store only groups containing entirely valid K-map cells.

                if is_valid_group(cells, kmap_values):
                    groups.add(frozenset(cells))

    return groups


# =========================================================
# 8. FIND PRIME IMPLICANTS
# =========================================================

def find_prime_groups(groups):
    prime_groups = set()

    for group in groups:
        is_prime = True

        for other_group in groups:

            # A group is not prime if it can be expanded into a larger
            # valid group that already contains all of its cells.

            if len(other_group) > len(group):
                if group.issubset(other_group):
                    is_prime = False
                    break

        if is_prime:
            prime_groups.add(group)

    return prime_groups


# =========================================================
# 9. CONVERT GROUP CELLS TO MINTERMS
# =========================================================

def get_group_minterms(cells):
    minterms = []

    for row, column in cells:

        # Convert each K-map cell position back to its minterm number.

        minterm = KMAP[row][column]
        minterms.append(minterm)

    return set(minterms)


# =========================================================
# 10. BUILD PRIME IMPLICANT CHART
# =========================================================

def build_prime_chart(prime_groups, minterms):
    chart = {}

    for minterm in minterms:
        chart[minterm] = []

        for group in prime_groups:
            group_minterms = get_group_minterms(group)

            # Record every prime group that covers this minterm.

            if minterm in group_minterms:
                chart[minterm].append(group)

    return chart


# =========================================================
# 11. FIND ESSENTIAL PRIME IMPLICANTS
# =========================================================

def find_essential_groups(chart):
    essential_groups = set()

    for minterm, groups in chart.items():

        # If only one prime group covers a minterm, that group is essential.

        if len(groups) == 1:
            essential_group = groups[0]
            essential_groups.add(essential_group)

    return essential_groups


# =========================================================
# 12. SELECT BEST REMAINING GROUP
# =========================================================

def select_best_group(prime_groups, selected_groups, uncovered):
    best_group = None
    best_score = (-1, -1)

    for group in prime_groups:
        if group in selected_groups:
            continue

        group_minterms = get_group_minterms(group)

        # Count how many currently uncovered minterms this group can cover.

        newly_covered = group_minterms & uncovered

        coverage_score = len(newly_covered)
        size_score = len(group)

        # Prefer maximum coverage first, then prefer the larger group.

        score = (coverage_score, size_score)

        if score > best_score:
            best_score = score
            best_group = group

    return best_group


# =========================================================
# 13. SELECT GROUPS TO COVER ALL MINTERMS
# =========================================================

def select_groups(prime_groups, minterms):
    chart = build_prime_chart(
        prime_groups,
        minterms
    )

    essential_groups = find_essential_groups(chart)
    selected_groups = set(essential_groups)

    covered_minterms = set()

    for group in selected_groups:
        covered_minterms.update(
            get_group_minterms(group)
        )

    uncovered = set(minterms) - covered_minterms

    # Keep selecting the best available group until every required
    # minterm is covered or no suitable group remains.

    while uncovered:
        best_group = select_best_group(
            prime_groups,
            selected_groups,
            uncovered
        )

        if best_group is None:
            break

        selected_groups.add(best_group)

        covered_minterms.update(
            get_group_minterms(best_group)
        )

        uncovered = set(minterms) - covered_minterms

    return selected_groups


# =========================================================
# 14. CONVERT MINTERM TO 4-BIT BINARY
# =========================================================

def minterm_to_binary(minterm):

    # Convert the minterm into a fixed 4-bit binary representation.

    return format(minterm, "04b")


# =========================================================
# 15. GENERATE BOOLEAN TERM FROM GROUP
# =========================================================

def get_group_term(group_minterms):

    # If every K-map cell is included, all variables are eliminated.

    if len(group_minterms) == 16:
        return "1"

    binaries = []

    for minterm in group_minterms:
        binaries.append(
            minterm_to_binary(minterm)
        )

    variables = ["A", "B", "C", "D"]
    term = ""

    for position in range(4):
        bits = []

        for binary in binaries:
            bits.append(
                binary[position]
            )

        unique_bits = set(bits)

        # A constant 0 at this position contributes the complemented variable.

        if unique_bits == {"0"}:
            term += variables[position] + "'"

        # A constant 1 at this position contributes the normal variable.

        elif unique_bits == {"1"}:
            term += variables[position]

    return term


# =========================================================
# 16. BUILD FINAL BOOLEAN EXPRESSION
# =========================================================

def build_expression(selected_groups):
    terms = []

    for group in selected_groups:
        group_minterms = get_group_minterms(group)
        term = get_group_term(group_minterms)

        # Prevent the same Boolean term from appearing more than once.

        if term not in terms:
            terms.append(term)

    terms.sort()

    expression = " + ".join(terms)

    return expression


# =========================================================
# 17. CONVERT GROUP TO JSON-FRIENDLY FORMAT
# =========================================================

def format_group(group):
    cells = []

    for row, column in group:
        cells.append([
            row,
            column
        ])

    cells.sort()

    minterms = sorted(
        get_group_minterms(group)
    )

    return {
        "cells": cells,
        "minterms": minterms
    }


# =========================================================
# 18. FORMAT ALL SELECTED GROUPS
# =========================================================

def format_groups(groups):
    formatted_groups = []

    for group in groups:
        formatted_groups.append(
            format_group(group)
        )

    # Display larger groups first, with minterm order used as a tie-breaker.

    formatted_groups.sort(
        key=lambda group: (
            len(group["minterms"]),
            group["minterms"]
        ),
        reverse=True
    )

    return formatted_groups


# =========================================================
# 19. GENERATE SOLUTION STEPS
# =========================================================

def generate_steps(
    minterms,
    valid_groups,
    prime_groups,
    selected_groups,
    expression
):
    steps = []

    steps.append(
        f"Given minterms: Σm({', '.join(map(str, sorted(minterms)))})"
    )

    steps.append(
        "The minterms were placed into the 4-variable K-map using Gray-code ordering."
    )

    steps.append(
        f"{len(valid_groups)} valid groups were identified."
    )

    steps.append(
        f"{len(prime_groups)} prime implicants were obtained."
    )

    steps.append(
        f"{len(selected_groups)} group(s) were selected to cover all required minterms."
    )

    # Handle the special case where no minterms are present.

    if expression == "":
        steps.append(
            "No minterms are present, so the Boolean function is 0."
        )

    # Handle the special case where every possible minterm is present.

    elif expression == "1":
        steps.append(
            "All 16 minterms are present, so the Boolean function is 1."
        )

    else:
        steps.append(
            f"The simplified Boolean expression is: {expression}"
        )

    return steps


# =========================================================
# 20. MAIN K-MAP SOLVER
# =========================================================

def solve_kmap(minterms):

    # Remove duplicate minterms and arrange them in ascending order.

    minterms = sorted(set(minterms))

    # -----------------------------------------------------
    # EDGE CASE: NO MINTERMS
    # -----------------------------------------------------

    if len(minterms) == 0:
        return {
            "minterms": [],
            "kmap": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "groups": [],
            "expression": "0",
            "steps": [
                "No minterms were provided.",
                "Therefore, the Boolean function is 0."
            ]
        }

    # -----------------------------------------------------
    # EDGE CASE: ALL MINTERMS
    # -----------------------------------------------------

    if len(minterms) == 16:
        kmap_values = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ]

        # Represent every cell in the K-map as one complete group.

        all_cells = frozenset(
            (row, column)
            for row in range(4)
            for column in range(4)
        )

        return {
            "minterms": minterms,
            "kmap": kmap_values,
            "groups": [
                format_group(all_cells)
            ],
            "expression": "1",
            "steps": [
                "All 16 minterms are present.",
                "Therefore, the entire K-map forms one group.",
                "All variables are eliminated.",
                "The simplified Boolean expression is: 1"
            ]
        }

    # -----------------------------------------------------
    # STEP 1: CREATE K-MAP
    # -----------------------------------------------------

    kmap_values = create_kmap_values(minterms)

    # -----------------------------------------------------
    # STEP 2: FIND VALID GROUPS
    # -----------------------------------------------------

    valid_groups = find_valid_groups(
        kmap_values
    )

    # -----------------------------------------------------
    # STEP 3: FIND PRIME GROUPS
    # -----------------------------------------------------

    prime_groups = find_prime_groups(
        valid_groups
    )

    # -----------------------------------------------------
    # STEP 4: SELECT GROUPS
    # -----------------------------------------------------

    selected_groups = select_groups(
        prime_groups,
        minterms
    )

    # -----------------------------------------------------
    # STEP 5: BUILD BOOLEAN EXPRESSION
    # -----------------------------------------------------

    expression = build_expression(
        selected_groups
    )

    # -----------------------------------------------------
    # STEP 6: FORMAT GROUPS
    # -----------------------------------------------------

    formatted_groups = format_groups(
        selected_groups
    )

    # -----------------------------------------------------
    # STEP 7: GENERATE SOLUTION STEPS
    # -----------------------------------------------------

    steps = generate_steps(
        minterms,
        valid_groups,
        prime_groups,
        selected_groups,
        expression
    )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {
        "minterms": minterms,
        "kmap": kmap_values,
        "groups": formatted_groups,
        "expression": expression,
        "steps": steps
    }

