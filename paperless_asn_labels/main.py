from fpdf import FPDF
import io
import segno
from dataclasses import dataclass
from typing import Generator, Literal
from itertools import product

Dimensions = tuple[float, float]


@dataclass
class LabelSheet:
    column_count: int
    row_count: int
    cell_dimensions_mm: Dimensions
    cell_margins_mm: Dimensions
    page_margins_mm: Dimensions
    cell_paddings_mm: Dimensions
    page_format: Literal["A4"]

    @property
    def cell_count(self):
        return self.column_count * self.row_count

    @property
    def width(self):
        return self.column_count * self.cell_width_mm

    @property
    def height(self):
        return self.row_count * self.cell_height_mm

    def get_cell_edge(
        self,
        cell_center_mm: Dimensions,
        edge: Literal["left", "right", "top", "bottom"],
    ):
        if edge == "left":
            return (
                cell_center_mm[0]
                - self.cell_dimensions_mm[0] / 2
                + self.cell_paddings_mm[0]
            )

        if edge == "right":
            return (
                cell_center_mm[0]
                + self.cell_dimensions_mm[0] / 2
                - self.cell_paddings_mm[0]
            )

        if edge == "top":
            return (
                cell_center_mm[1]
                - self.cell_dimensions_mm[1] / 2
                + self.cell_paddings_mm[1]
            )

        if edge == "bottom":
            return (
                cell_center_mm[1]
                + self.cell_dimensions_mm[1] / 2
                - self.cell_paddings_mm[1]
            )

    @property
    def available_cell_size_mm(self) -> Dimensions:
        return (
            self.cell_dimensions_mm[0] - 2 * self.cell_paddings_mm[0],
            self.cell_dimensions_mm[1] - 2 * self.cell_paddings_mm[1],
        )

    def _get_cell_center_position(
        self, row_index: int, column_index: int
    ) -> Dimensions:
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
    def cell_centers(self) -> Generator[Dimensions, None, None]:
        return (
            self._get_cell_center_position(row_index, column_index)
            for row_index, column_index in product(
                range(self.row_count), range(self.column_count)
            )
        )


L4731 = LabelSheet(
    column_count=7,
    row_count=27,
    cell_dimensions_mm=(25.4, 10.0),
    cell_margins_mm=(2.5, 0),
    cell_paddings_mm=(1.5, 1.5),
    page_margins_mm=(9, 13.5),
    page_format="A4",
)


def main():
    start_asn = 258
    sheet = L4731
    qr_code_width_mm = min(sheet.available_cell_size_mm)

    pdf = FPDF()
    pdf.add_page(format=sheet.page_format)
    pdf.set_font("helvetica", size=16)

    for index, center in enumerate(sheet.cell_centers):
        asn = index + start_asn
        qr_code_string = f"ASN{asn}"
        readable_string = f"{asn}"

        qr_code_buffer = io.BytesIO()
        qr_code = segno.make_qr(qr_code_string)
        qr_code.save(qr_code_buffer, kind="svg", border=0, omitsize=True)

        # x/y determine top left of the QR code
        pdf.image(
            qr_code_buffer,
            x=sheet.get_cell_edge(center, "left"),
            y=sheet.get_cell_edge(center, "top"),
            w=qr_code_width_mm,
        )

        # x/y determine bottom left of the label text
        pdf.text(
            x=sheet.get_cell_edge(center, "left")
            + qr_code_width_mm
            + 2.0,  # Add some spacing
            y=sheet.get_cell_edge(center, "bottom"),
            text=readable_string,
        )

    pdf.output("qrcode.pdf")


if __name__ == "__main__":
    main()
