"""Contains a class that represents a label sheet, and specific sheets."""

from collections.abc import Generator

from dataclasses import dataclass
from itertools import product
from typing import Literal

Dimensions = tuple[float, float]


@dataclass
class Sheet:
    """A class that represents a label sheet's properties."""

    column_count: int  # The number of label columns.
    row_count: int  # The number of label rows.
    cell_dimensions_mm: Dimensions  # The x and y dimensions of a cell in mm.
    cell_margins_mm: Dimensions  # The distance in x and y between two cells.
    page_margins_mm: Dimensions  # The distance in x and y between a sheet edge and the closest cell.
    cell_paddings_mm: Dimensions  # The distance in x and y between a cell edge and the content within a cell.
    page_format: Literal["A4"]  # The page format.

    def get_cell_edge_distance_mm(
        self,
        cell_center_mm: Dimensions,
        edge: Literal["left", "right", "top", "bottom"],
    ) -> float:
        """Get the distance of a cell's chosen edge from the cell's center.

        For left and right edges, calculate the distance in x direction, for top and bottom in y direction.

        Args:
            cell_center_mm (Dimensions): The center of the cell, for which to find the distance.
            edge (Literal["left", "right", "top", "bottom"]): The edge to get the distance for.

        Returns:
            float: The distance in mm.
        """
        if edge == "left":
            return cell_center_mm[0] - self.cell_dimensions_mm[0] / 2 + self.cell_paddings_mm[0]

        if edge == "right":
            return cell_center_mm[0] + self.cell_dimensions_mm[0] / 2 - self.cell_paddings_mm[0]

        if edge == "top":
            return cell_center_mm[1] - self.cell_dimensions_mm[1] / 2 + self.cell_paddings_mm[1]

        if edge == "bottom":
            return cell_center_mm[1] + self.cell_dimensions_mm[1] / 2 - self.cell_paddings_mm[1]

        raise ValueError("Unknown edge.")

    @property
    def available_cell_size_mm(self) -> Dimensions:
        """The available cell size, taking into account padding."""
        return (
            self.cell_dimensions_mm[0] - 2 * self.cell_paddings_mm[0],
            self.cell_dimensions_mm[1] - 2 * self.cell_paddings_mm[1],
        )

    def _get_cell_center_position(self, row_index: int, column_index: int) -> Dimensions:
        x = (
            self.page_margins_mm[0]
            + (column_index + 0.5) * self.cell_dimensions_mm[0]
            + column_index * self.cell_margins_mm[0]
        )

        y = (
            self.page_margins_mm[1]
            + (row_index + 0.5) * self.cell_dimensions_mm[1]
            + row_index * self.cell_margins_mm[1]
        )

        return (x, y)

    @property
    def cell_count(self) -> int:
        """The total number of cells on the sheet."""
        return self.column_count * self.row_count

    @property
    def cell_centers(self) -> Generator[Dimensions, None, None]:
        """The center locations of labels on the sheet.

        Yields:
            Generator[Dimensions, None, None]: A generator of center locations.
        """
        return (
            self._get_cell_center_position(row_index, column_index)
            for row_index, column_index in product(range(self.row_count), range(self.column_count))
        )


# Supported label sheets
SHEETS = {
    "L4731": Sheet(
        column_count=7,
        row_count=27,
        cell_dimensions_mm=(25.4, 10.0),
        cell_margins_mm=(2.5, 0),
        cell_paddings_mm=(1.5, 1.5),
        page_margins_mm=(9, 13.5),
        page_format="A4",
    )
}
