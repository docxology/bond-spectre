"""SPECTRE brotherhood — criminal-organization intelligence model.

The SPECTRE organisation in ``Spectre`` (2015) is a secretive brotherhood: a
single leader at the apex, an executive layer beneath, and a network of
*isolated cells* whose members only know their own cell. This module models
that intelligence structure with real, deterministic algorithms:

* **hierarchy** — the command tree (parent -> subordinate); depths and height,
  and proof that every operative is reachable from the apex (chain of command);
* **cells** — a partition of operatives into isolated cells, with
  compartmentalization measured as the fraction of cross-cell pairs that are
  *not* directly linked (perfect cell separation on a true cell structure);
* **exposure** — the set of operatives compromised if a given operative is
  turned (their cellmates plus their direct superior/subordinates).

Pure and infrastructure-free: ``numpy`` + the standard library only.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


__all__ = [
    "Brotherhood",
    "HierarchyStats",
    "build_org",
    "hierarchy_stats",
    "cell_membership",
    "compartmentalization",
    "command_reachability",
    "exposure",
]

#: Sentinel cell label for operatives with no declared cell.
NO_CELL = "_none_"


@dataclass(frozen=True)
class Brotherhood:
    """A criminal organisation: cell assignments + command hierarchy.

    ``cell_of`` maps each operative to a cell id; ``parent_of`` maps each
    subordinate to their single commanding superior (``None`` for the apex).
    ``operatives`` is the canonical ordered tuple of all members.
    """

    operatives: tuple[str, ...]
    cell_of: dict[str, str]
    parent_of: dict[str, str | None]
    leadership: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class HierarchyStats:
    """Aggregate command-structure metrics."""

    depth: dict[str, int]
    height: int
    reachable_from_apex: int
    total_members: int

    @property
    def chain_complete(self) -> bool:
        """True when every operative is reachable from the apex leadership."""
        return self.reachable_from_apex == self.total_members


def build_org(
    operatives: Sequence[str],
    cell_of: Mapping[str, str],
    parent_of: Mapping[str, str | None],
    leadership: Iterable[str] = (),
) -> Brotherhood:
    """Build and validate a :class:`Brotherhood`.

    Args:
        operatives: Ordered, unique operative labels.
        cell_of: Operative -> cell id.
        parent_of: Operative -> their superior (``None`` marks an apex).
        leadership: Operatives designated as leadership (must be a subset of
            ``operatives``).

    Raises:
        ValueError: If operatives are not unique, a mapping references an
            unknown operative/superior, an operative reports to themselves, or
            leadership names an unknown operative.
    """
    ordered = tuple(operatives)
    if len(set(ordered)) != len(ordered):
        raise ValueError("operatives must be unique")
    known = set(ordered)
    if not known:
        raise ValueError("an organisation requires at least one operative")
    for member, cell in cell_of.items():
        if member not in known:
            raise ValueError(f"unknown operative {member!r} in cell_of")
        if not isinstance(cell, str) or not cell.strip():
            raise ValueError(f"cell id for {member!r} must be a non-empty string")
    resolved_cells = {member: cell for member, cell in cell_of.items()}

    resolved_parents: dict[str, str | None] = {}
    for member, parent in parent_of.items():
        if member not in known:
            raise ValueError(f"unknown operative {member!r} in parent_of")
        if parent is not None and parent not in known:
            raise ValueError(f"unknown superior {parent!r} for {member!r}")
        if parent == member:
            raise ValueError(f"operative {member!r} cannot report to themselves")
        resolved_parents[member] = parent

    leadership_set = set(leadership)
    unknown_leadership = leadership_set - known
    if unknown_leadership:
        raise ValueError(f"unknown leadership operatives: {sorted(unknown_leadership)}")

    return Brotherhood(
        operatives=ordered,
        cell_of=resolved_cells,
        parent_of=resolved_parents,
        leadership=frozenset(leadership_set),
    )


def hierarchy_stats(brotherhood: Brotherhood) -> HierarchyStats:
    """Compute per-operative command depth and the tree height.

    Depth is the number of command links between an operative and the nearest
    apex (0 for leadership, or for operatives with no assigned superior).
    """
    operatives = brotherhood.operatives
    parent = brotherhood.parent_of
    leadership = brotherhood.leadership or {m for m in operatives if parent.get(m) is None}
    depth: dict[str, int] = {}
    order: list[str] = []
    for member in operatives:
        if member in leadership or member not in parent:
            depth[member] = 0
            order.append(member)
            continue
        path: list[str] = []
        cursor: str | None = member
        visited: set[str] = set()
        while cursor is not None and cursor not in depth:
            if cursor in visited:  # guard against malformed cycles
                break
            visited.add(cursor)
            path.append(cursor)
            cursor = parent.get(cursor)
        offset = depth.get(cursor, 0) if cursor is not None else 0
        for i, node in enumerate(reversed(path)):
            depth[node] = offset + i + 1
            order.append(node)
    reachable = sum(1 for m in operatives if m in depth)
    return HierarchyStats(
        depth=depth,
        height=max(depth.values(), default=0),
        reachable_from_apex=reachable,
        total_members=len(operatives),
    )


def cell_membership(brotherhood: Brotherhood) -> dict[str, tuple[str, ...]]:
    """Map each cell id to its ordered member tuple (skips unassigned operatives)."""
    grouped: dict[str, list[str]] = {}
    for member in brotherhood.operatives:
        cell = brotherhood.cell_of.get(member)
        if cell is None or cell == NO_CELL:
            continue
        grouped.setdefault(cell, []).append(member)
    return {cell: tuple(members) for cell, members in grouped.items()}


def compartmentalization(brotherhood: Brotherhood) -> float:
    """Fraction of distinct operative pairs in *different* cells with no direct link.

    On a true cell structure (members of one cell never linked to members of
    another) this is ``1.0`` — perfect separation. If the hierarchy leaks
    cross-cell command edges, the value drops below 1, quantifying the leak.
    """
    members = brotherhood.operatives
    cell_of = brotherhood.cell_of
    same_cell: dict[str, set[str]] = {}
    for member in members:
        cell = cell_of.get(member, NO_CELL)
        same_cell.setdefault(cell, set()).add(member)

    cross_pairs = 0
    linked_cross_pairs = 0
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            if same_cell.get(cell_of.get(a, NO_CELL)) == same_cell.get(cell_of.get(b, NO_CELL)):
                continue
            cross_pairs += 1
            linked = brotherhood.parent_of.get(a) == b or brotherhood.parent_of.get(b) == a
            if linked:
                linked_cross_pairs += 1
    if cross_pairs == 0:
        return 1.0
    return float(1.0 - linked_cross_pairs / cross_pairs)


def command_reachability(brotherhood: Brotherhood) -> set[str]:
    """All operatives reachable from the leadership apex via the command tree.

    Uses a BFS over the ``parent -> subordinate`` edges (the reverse of the
    superior relation).
    """
    subordinates: dict[str, list[str]] = {}
    for member, superior in brotherhood.parent_of.items():
        if superior is not None:
            subordinates.setdefault(superior, []).append(member)
    leadership = brotherhood.leadership or {m for m in brotherhood.operatives if brotherhood.parent_of.get(m) is None}
    reached: set[str] = set()
    queue: deque[str] = deque(sorted(leadership))
    while queue:
        node = queue.popleft()
        if node in reached:
            continue
        reached.add(node)
        for child in subordinates.get(node, []):
            queue.append(child)
    return reached


def exposure(brotherhood: Brotherhood, operative: str) -> set[str]:
    """Operatives compromised if ``operative`` is turned.

    A turned operative inherently implicates their cellmates (compartmentalized
    knowledge) plus their direct superior and direct subordinates (command
    knowledge). The result includes the operative themselves.

    Raises:
        ValueError: If ``operative`` is not a member of the organisation.
    """
    if operative not in set(brotherhood.operatives):
        raise ValueError(f"unknown operative {operative!r}")
    turned: set[str] = {
        operative,
        brotherhood.parent_of.get(operative) or "",
    }
    for member, superior in brotherhood.parent_of.items():
        if superior == operative:
            turned.add(member)
    cell = brotherhood.cell_of.get(operative)
    if cell is not None:
        for member, member_cell in brotherhood.cell_of.items():
            if member_cell == cell:
                turned.add(member)
    turned.discard("")
    return turned
