website_data = {
    'https://www.bleepingcomputer.com/': {
        'header_text': '.article_section h1',
        'extracted_text': '.articleBody p',
        'img_url': '.articleBody img',
        'date': '.cz-news-date',
        'author': '.author-name',
        'p_texts': '.articleBody p',
        'article_links': '.articleBody a'
    },
    'https://www.securityweek.com/': {
        'header_text': 'h1',
        'extracted_text': 'span.zox-post-excerpt',
        'img_url': '.zox-post-img img',
        'date': '.zox-post-date-wrap time',
        'author': '.zox-author-name-wrap .zox-author-name a',
        'p_texts': '.theiaPostSlider_preloadedSlide p',
        'article_links': 'div.zox-art-title a' 
    },

    
}