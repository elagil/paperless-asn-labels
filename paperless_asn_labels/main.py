"""Generator for archive serial number (ASN) label sheets."""

from fpdf import FPDF
from pathlib import Path
import click
import io
import segno

from paperless_asn_labels.sheet import SHEETS


@click.command()
@click.option(
    "-f", "--first-asn", default=1, type=click.IntRange(1), help="The archive serial number to start the sheet at."
)
@click.option("-d", "--dir", default=".", help="The output directory for the generated file.")
@click.option("-s", "--sheet-name", required=True, type=click.Choice(SHEETS.keys(), case_sensitive=False))
def generate(first_asn: int, dir: "str", sheet_name: str):
    """Generates a PDF file, suitable for printing to a label sheet.

    The sheet contains QR codes of archive serial numbers (ASNs), alongside their human-readable representations.
    """
    output_dir = Path(dir)
    sheet = SHEETS[sheet_name]
    qr_code_width_mm = min(sheet.available_cell_size_mm)

    pdf = FPDF()
    pdf.add_page(format=sheet.page_format)
    pdf.set_font("helvetica", size=14)

    for index, center in enumerate(sheet.cell_centers):
        asn = index + first_asn
        qr_code_string = f"ASN{asn}"
        readable_string = f"{asn}"

        qr_code_buffer = io.BytesIO()
        qr_code = segno.make_qr(qr_code_string)
        qr_code.save(qr_code_buffer, kind="svg", border=0, omitsize=True)

        # x/y determine top left of the QR code
        pdf.image(
            qr_code_buffer,
            x=sheet.get_cell_edge_distance_mm(center, "left"),
            y=sheet.get_cell_edge_distance_mm(center, "top"),
            w=qr_code_width_mm,
        )

        # x/y determine bottom left of the label text
        pdf.text(
            x=sheet.get_cell_edge_distance_mm(center, "left") + qr_code_width_mm + 2.0,  # Add some spacing
            y=sheet.get_cell_edge_distance_mm(center, "bottom"),
            text=readable_string,
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf.output(output_dir / f"{sheet_name}_ASN_{first_asn}_to_{first_asn+sheet.cell_count-1}.pdf")


if __name__ == "__main__":
    generate()
