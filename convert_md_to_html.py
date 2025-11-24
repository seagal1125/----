
import markdown
import os

def create_html_from_md(md_path, html_path, title):
    """Reads a markdown file, converts it to HTML, and wraps it in a styled template."""
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML, enabling the 'tables' extension
    html_body = markdown.markdown(md_content, extensions=['tables'])

    # Define the CSS and HTML template
    html_template = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif;
            line-height: 1.6;
            background-color: #fdfdfd;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            background: #fff;
            border: 1px solid #eaeaea;
            border-radius: 4px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            color: #111;
            font-weight: 600;
        }}
        h1 {{ text-align: center; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 2rem; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            font-size: 0.9rem;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background-color: #f7f7f7;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #fcfcfc;
        }}
        p {{ margin: 1rem 0; }}
        li {{ margin: 0.5rem 0; }}
        blockquote {{
            border-left: 4px solid #ccc;
            padding-left: 1rem;
            margin-left: 0;
            color: #666;
        }}
        code {{
            background-color: #f0f0f0;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "Courier New", Courier, monospace;
        }}
        footer {{
            text-align: center; 
            margin-top: 3rem; 
            padding-top: 1rem;
            border-top: 1px solid #eee;
            color: #888;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body}
        <footer>
            Generated from Markdown. This is a data analysis report, not investment advice.
        </footer>
    </div>
</body>
</html>
    '''

    # Combine template and converted HTML
    full_html = html_template.format(title=title, body=html_body)

    # Write to file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

def main():
    source_md = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_完整分析報告.md"
    target_html = "/Users/david/Library/Mobile Documents/com~apple~CloudDocs/0notebook-fromGithub/資產配置/分析報告/2008_FortuneTop100_vs_VT_報告(文檔版).html"
    report_title = "2008 財富100強 vs. VT 績效分析 (文檔版)"

    if not os.path.exists(source_md):
        print(f"Error: Source file not found at {source_md}")
        return

    create_html_from_md(source_md, target_html, report_title)
    print(f"HTML report successfully generated at: {target_html}")

if __name__ == "__main__":
    main()
