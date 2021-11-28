import logging
from os import path
import random
import string
from typing import List, Optional

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, PackageLoader, select_autoescape

from api.schemas import RecipeInDB

FILENAME_LENGTH = 40


logger = logging.getLogger(__name__)
env = Environment(loader=PackageLoader("api.cookbooks"))
template_dir = path.abspath(path.join(path.curdir, "api", "cookbooks", "templates"))


def generate_filename() -> str:
    return (
        "".join(
            random.choices(string.ascii_lowercase + string.digits, k=FILENAME_LENGTH)
        )
        + ".pdf"
    )


def generate_pdf_from_recipes(
    recipes: List[RecipeInDB],
    html_template_name: str = "html/recipe-card.html",
    css_template_name: str = "css/recipe-card.css",
) -> bytes:
    """Generates a byte stream of a PDF file containing the given recipes
    formatted to the given template"""

    html_template = env.get_template(html_template_name)
    css_template = env.get_template(css_template_name)
    # Put CSS in style tag of the HTML.
    css_content = css_template.render(template_dir=template_dir)

    html = html_template.render(
        cookbook_name="Franklin's Family Cookbook",
        by_line="By Franklin van Nes",
        recipes=recipes, template_base_url=template_dir, css_content=css_content
    )

    font_config = FontConfiguration()

    logger.debug(f"Generated HTML: {html}")

    pdf: Optional[bytes] = HTML(string=html).write_pdf(
        font_config=font_config,
    )

    if pdf:
        return pdf
    else:
        raise Exception("Failed to generate PDF")
