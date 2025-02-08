import os
import pypandoc
import shutil
import panflute as pf

base_path = ""

def update_image_paths(elem, doc):
    """
    Panflute filter that updates image URLs.
    If an image URL is relative (and does not start with 'http'),
    it is replaced with an absolute path based on the global base_path.
    """
    if isinstance(elem, pf.Image):
        if not os.path.isabs(elem.url) and not elem.url.startswith("http"):
            new_url = os.path.abspath(os.path.join(base_path, elem.url))
            new_url = new_url.replace(os.sep, "/")  # Use forward slashes for consistency
            pf.debug(f"Updating image: {elem.url} -> {new_url}")
            elem.url = new_url

os.environ["PATH"] = "/Library/TeX/texbin:" + "/opt/homebrew/bin:" + os.environ.get("PATH", "")

os.environ['PYPANDOC_PANDOC'] = '/opt/homebrew/bin/pandoc'

# Get the directory where this script resides.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths based on the script's location:
# - Source Markdown files are in "../test_data/report_test/"
# - The custom template is in "../agentbox/doc/template/pandoc_report.tex"
# - Output PDF should be written to "test/output" (i.e. an "output" folder inside the current test directory)
source_dir = os.path.abspath(os.path.join(script_dir, "..", "test_data", "report_test"))

staging_dir = os.path.abspath(os.path.join(script_dir, "..", "test_data", "report_staging"))

base_path = staging_dir

template_path = os.path.abspath(os.path.join(script_dir, "..", "agentbox", "doc", "template", "pandoc_report.tex"))

output_dir = os.path.abspath(os.path.join(script_dir, "output"))

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

if os.path.exists(staging_dir):
    shutil.rmtree(staging_dir)

# copy source files into staging directory
# the files in staging will be modified and then used for pdf generation
shutil.copytree(source_dir, staging_dir)

# Sorting is used to maintain a consistent chapter order.
markdown_files = sorted([os.path.join(staging_dir, f) for f in os.listdir(staging_dir) if f.endswith('.md')])

for md_file in markdown_files:
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    # Convert Markdown to panflute AST tokens.
    tokens = pf.convert_text(md_content, input_format="markdown", output_format="panflute")
    # Wrap tokens in a Doc object to get access to walk().
    doc = pf.Doc(*tokens)
    # Update image paths.
    doc.walk(update_image_paths)
    # Render the modified AST back to Markdown.
    updated_md = pf.convert_text(doc, input_format="panflute", output_format="markdown")
    # Overwrite the Markdown file in staging.
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(updated_md)


# Combine the contents of all Markdown files.
combined_markdown = ""
for md_file in markdown_files:
    with open(md_file, 'r', encoding='utf-8') as file:
        combined_markdown += file.read() + "\n\n"

# Add YAML front matter metadata to be injected into the template.
metadata = (
    "---\n"
    "title: 'My Report Title'\n"
    "author: 'Author Name'\n"
    "date: '2025-02-08'\n"
    "---\n\n"
)

combined_markdown = metadata + combined_markdown

# Define extra arguments for Pandoc:
#  - Use the custom template file at template_path.
#  - Use the tectonic PDF engine (change as needed).
#  - Generate a Table of Contents with a specified depth.
extra_args = [
    f'--template={template_path}',
    '--pdf-engine=latexmk',
    '--pdf-engine-opt=-pdf',
    '--verbose'
]

pdf_output_path = os.path.join(output_dir, 'combined_report.pdf')

# Convert the combined Markdown to PDF.
# When using outputfile, pypandoc writes the file directly to disk.

try:
    pypandoc.convert_text(
        combined_markdown,
        to='pdf',
        format='md',
        outputfile=pdf_output_path,
        extra_args=extra_args
    )
except RuntimeError as e:
    print("Error during conversion:", e)
    raise

print(f"PDF generated successfully: {pdf_output_path}")
