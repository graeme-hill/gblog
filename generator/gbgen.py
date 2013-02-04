import markdown2, os, re, shutil, datetime, calendar, sys, PyRSS2Gen, html.parser

# configuration section
MAIN_TITLE = 'Graeme Hill\'s Dev Blog'
RSS_TITLE = MAIN_TITLE
RSS_DESCRIPTION = 'My random thoughts on software development'
HOME_URL = 'http://graemehill.ca'
DEFAULT_SOURCE_CONTENT_PATH = 'source_content'
DEFAULT_COMPILED_CONTENT_PATH = 'www'
ARTICLES_REL_PATH = 'articles'
TEMPLATES_REL_PATH = 'templates'
CATEGORY_REL_PATH = 'category'
FEED_REL_PATH = ''
FEED_FILE_NAME = 'feed'
STATIC_CONTENT_SOURCE_PATH = 'resources'
STATIC_CONTENT_DEST_PATH = 'resources'
ROOT_FILE_NAME = 'index.html'
SLUG_SEP = '-'
BREAK_STR = '<!--break-->'
MAIN_TEMPLATE_NAME = 'main'
ARTICLE_TEMPLATE_NAME = 'article'
ARTICLE_SUMMARY_WRAPPER_TEMPLATE_NAME = 'article_summary_wrapper'

# pre-compiled regular expression constants
HEADER_LABEL_RE = re.compile(':\\s*')
HEADER_BODY_SPLIT_RE = re.compile('\\n\\s*\\n\\s*')
LABEL_SEP_RE = re.compile(',\\s*')
WHITESPACE_RE = re.compile('\\s+')

class MLStripper(html.parser.HTMLParser):
    """ Helper class for removing HTML tags from a string """
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Article:
    def __init__(self, slug, date, metadata, short_html, long_html, short_version_is_full_article):
        self.slug = slug
        self.date = date
        self.metadata = metadata
        self.short_html = short_html + ('...' if short_version_is_full_article else '')
        self.long_html = long_html
        self.short_version_is_full_article = short_version_is_full_article
        self.description = strip_tags(self.short_html)

class ArticleMetadata:
    def __init__(self, properties):
        self.title = properties['title']
        self.labels = [Label(l) for l in LABEL_SEP_RE.split(properties['labels'])]

class Label:
    def __init__(self, label_str):
        self.name = label_str
        self.slug = label_name_to_slug(self.name)

class Category:
    def __init__(self, label, articles):
        self.label = label
        self.articles = articles

def create_rss_item(article):
    url = urlify(HOME_URL, absolute_url(article.slug))
    return PyRSS2Gen.RSSItem(
        title=article.metadata.title,
        link=url,
        description=article.description,
        guid=url,
        pubDate=yearday_to_date(article.date))

def create_rss_feed(articles):
    return PyRSS2Gen.RSS2(
        title=RSS_TITLE,
        link=HOME_URL,
        description=RSS_DESCRIPTION,
        lastBuildDate=datetime.datetime.utcnow(),
        items=[create_rss_item(article) for article in articles])

def write_rss_feed(compiled_path, rss):
    feed_dir = pathify(compiled_path, FEED_REL_PATH)
    feed_path = pathify(feed_dir, FEED_FILE_NAME)
    if not os.path.exists(feed_dir):
        os.makedirs(feed_dir)
    with open(feed_path, 'w') as f:
        rss.write_xml(f)

def get_month_day_offset(month, year):
    result = 0
    for month_index in range(1, month):
        result += calendar.monthrange(year, month_index)[1]
    return result

def get_month_and_day_from_offset(offset, year):
    day = offset
    month = 1
    for month_index in range(1, 13):
        days_in_month = calendar.monthrange(year, month_index)[1]
        if days_in_month < day:
            day -= days_in_month
            month += 1
        else:
            return (month, day)
    raise 'Error: could not find day "%d" in year "%d"' % (offset, year)

def yearday_to_date(year_day):
    year, offset = [int(x) for x in year_day.split('.')]
    month, day = get_month_and_day_from_offset(offset, year)
    return datetime.datetime(year, month, day)

def datestr_to_yearday(date_str):
    """
    date_str is expected to be in form 'Feb 9 2012'
    result is in form '2012.040'
    """
    date = datetime.datetime.strptime(date_str, '%b %d %Y')
    day_of_year = get_month_day_offset(date.month, date.year) + date.day
    return '%d.%03d' % (date.year, day_of_year)

def copy_static_content(source_path, compiled_path):
    source_dir = pathify(source_path, STATIC_CONTENT_SOURCE_PATH)
    destination_dir = pathify(compiled_path, STATIC_CONTENT_DEST_PATH)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    for filename in os.listdir(source_dir):
        source_file = pathify(source_dir, filename)
        destination_file = pathify(destination_dir, filename)
        if os.path.isdir(source_file):
            shutil.copytree(source_file, destination_file)
        else:
            shutil.copy(source_file, destination_file)

def label_name_to_slug(label_name):
    modified = label_name.lower().replace('#', ' sharp ').replace('.', ' dot ')
    return re.sub(WHITESPACE_RE, SLUG_SEP, modified.strip())

def setup_output_dir(compiled_path):
    if not os.path.isdir(compiled_path):
        os.makedirs(compiled_path)
    for filename in os.listdir(compiled_path):
        file_path = pathify(compiled_path, filename)
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.unlink(file_path)

def strip_extension(file_name):
    return file_name.rsplit('.', 1)[0]

def load_templates(source_path):
    template_dir = pathify(source_path, TEMPLATES_REL_PATH)
    return {strip_extension(f): read_text(pathify(template_dir, f)) for f in os.listdir(template_dir)}

def load_articles(source_path):
    articles_dir = pathify(source_path, ARTICLES_REL_PATH)
    articles = [compile_article(read_text(pathify(articles_dir, f)), f) for f in os.listdir(articles_dir)]
    return sorted(articles, key=lambda x: x.date, reverse=True)

def pathify(*parts):
    return os.path.normpath(os.path.join(*parts))

def urlify(*parts):
    return '/'.join([s.strip('/') for s in parts])

def write_text(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)

def read_text(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def write_article_stub(file_path):
    with open(file_path, 'w') as f:
        f.write('title:\nlabels:\n\nto do: put article here')

def render_template(template_text, data):
    result = template_text
    for key in data:
        result = result.replace('${%s}' % key, data[key])
    return result

def absolute_url(url):
    return url if url[0] == '/' else '/' + url

def write_article_page(article, compiled_path, templates):
    file_dir = pathify(compiled_path, article.slug)
    file_path = pathify(file_dir, ROOT_FILE_NAME)
    os.makedirs(file_dir)
    article_html = render_template(templates[ARTICLE_TEMPLATE_NAME], { 
        'title': article.metadata.title, 
        'content': article.long_html, 
        'date': article.date,
        'article_url': absolute_url(article.slug) })
    html = render_template(templates[MAIN_TEMPLATE_NAME], { 
        'title': article.metadata.title, 
        'content': article_html })
    write_text(file_path, html)

def write_category_page(category, compiled_path, templates):
    file_dir = pathify(compiled_path, CATEGORY_REL_PATH, category.label.slug)
    file_path = pathify(file_dir, ROOT_FILE_NAME)
    os.makedirs(file_dir)
    articles_html = ''
    for article in category.articles:
        articles_html += render_template(templates[ARTICLE_SUMMARY_WRAPPER_TEMPLATE_NAME], {
            'title': article.metadata.title,
            'content': article.short_html,
            'date': article.date,
            'article_url': absolute_url(article.slug) })
    html = render_template(templates[MAIN_TEMPLATE_NAME], {
        'title': category.label.name + ' - ' + MAIN_TITLE,
        'content': articles_html })
    write_text(file_path, html)

def write_index(articles, compiled_path, templates):
    file_path = pathify(compiled_path, ROOT_FILE_NAME)
    articles_html = ''
    for article in sorted(articles, key=lambda a: a.date, reverse=True):
        articles_html += render_template(templates[ARTICLE_SUMMARY_WRAPPER_TEMPLATE_NAME], { 
            'title': article.metadata.title, 
            'content': article.short_html, 
            'date': article.date,
            'article_url': absolute_url(article.slug) })
    html = render_template(templates[MAIN_TEMPLATE_NAME], {
        'title': MAIN_TITLE,
        'content': articles_html })
    write_text(file_path, html)

def get_article_header_properties(header_text):
    properties = {}
    for line in header_text.split('\n'):
        parts = HEADER_LABEL_RE.split(line, 1)
        if len(parts) == 2:
            properties[parts[0]] = parts[1]
    return properties

def markdown_to_html(markdown_text):
    return markdown2.markdown(markdown_text)

def compile_article(article_text, file_name):
    header_text, body_text = HEADER_BODY_SPLIT_RE.split(article_text, 1)
    body_parts = body_text.split(BREAK_STR, 1)
    short_body = body_parts[0]
    filename_parts = strip_extension(file_name).split('_')

    return Article(
        slug=filename_parts[1],
        date=filename_parts[0],
        metadata=ArticleMetadata(get_article_header_properties(header_text)),
        short_html=markdown_to_html(short_body),
        long_html=markdown_to_html(body_text),
        short_version_is_full_article=len(body_parts) > 1)

def get_categories(articles):
    categories_dict = {}
    for article in articles:
        for label in article.metadata.labels:
            if not label.slug in categories_dict:
                categories_dict[label.slug] = Category(label, [])
            categories_dict[label.slug].articles.append(article)
    return sorted(categories_dict.values(), key=lambda x: x.label.name)

def build_website(source_path, compiled_path):
    templates = load_templates(source_path)
    articles = load_articles(source_path)

    setup_output_dir(compiled_path)

    copy_static_content(source_path, compiled_path)

    for article in articles:
        write_article_page(article, compiled_path, templates)

    for category in get_categories(articles):
        write_category_page(category, compiled_path, templates)

    write_index(articles, compiled_path, templates)

    write_rss_feed(compiled_path, create_rss_feed(articles))

def create_new_article(date, slug):
    year_day = date if len(date.split(' ')) != 3 else datestr_to_yearday(date)
    file_path = pathify(DEFAULT_SOURCE_CONTENT_PATH, ARTICLES_REL_PATH, '%s_%s.md' % (year_day, slug))
    if not os.path.exists(file_path):
        write_article_stub(file_path)
    else:
        print('This exact file already exists')

if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'new':
        create_new_article(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 1:
        build_website(DEFAULT_SOURCE_CONTENT_PATH, DEFAULT_COMPILED_CONTENT_PATH)
    else:
        print('invalid arguments')