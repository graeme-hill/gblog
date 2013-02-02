import markdown2, os, re

DEFAULT_SOURCE_CONTENT_PATH = 'source_content'
DEFAULT_COMPILED_CONTENT_PATH = 'compiled_content'
ARTICLES_REL_PATH = 'articles'
TEMPLATES_REL_PATH = 'templates'
MAIN_TEMPLATE_FILE_NAME = 'main'
HTML_FILE_EXTENSION = '.html'
HEADER_LABEL_RE = re.compile('[^:]+:\\s*')
HEADER_BODY_SPLIT_RE = re.compile('\\n\\s*\\n\\s*')

def strip_extension(file_name):
	return file_name.rsplit('.', 1)[0]

def load_templates(source_path):
	template_dir = pathify(source_path, TEMPLATES_REL_PATH)
	return {strip_extension(f): read_text(pathify(template_dir, f)) for f in os.listdir(template_dir)}

def load_articles(source_path):
	articles_dir = pathify(source_path, ARTICLES_REL_PATH)
	return [compile_article(read_text(pathify(articles_dir, f)), f) for f in os.listdir(articles_dir)]

def pathify(*parts):
	return os.path.normpath(os.path.join(parts))

def write_text(file_path, text):
	f = open(file_path, 'w')
	f.write(text)
	f.close()

def read_text(file_path):
	f = open(file_path, 'r')
	result = f.read()
	f.close()
	return result

def render_template(template_text, data):
	result = template_text
	for key in data:
		result = result.replace('${%s}' % key, data[key])
	return result

def write_article_page(article, destination_dir, templates):
	file_path = pathify(destination_dir, article.slug) + HTML_FILE_EXTENSION
	html = render_template(templates[MAIN_TEMPLATE_NAME], { title: article.metadata.title, content: article.html })
	write_text(file_path, html)

def get_article_header_properties(header_text):
	properties = {}
	for line in header_text.split('\\n'):
		parts = HEADER_LABEL_RE.split(line, 1)
		if len(parts) == 2:
			properties[parts[0]] = parts[1]
	return properties

def markdown_to_html(markdown_text):
	return markdown2.markdown(markdown_text)

def compile_article(article_text, file_name):
	header_text, body_text = HEADER_BODY_SPLIT_RE.split(article_text, 1)
	return {
		slug: strip_extension(file_name),
		metadata: get_article_header_properties(header_text),
		html: markdown_to_html(body_text)
	}

def build_website(source_path, compiled_path):
	templates = load_templates(source_path)
	articles = load_articles(source_path)

	for article in articles:
		write_article_page(article, compiled_path, templates)

if __name__ == '__main__':
	build_website(DEFAULT_SOURCE_CONTENT_PATH, DEFAULT_COMPILED_CONTENT_PATH)