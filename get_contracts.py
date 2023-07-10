import html
import bs4
import feedparser as fp
from markdownify import markdownify
from datetime import datetime
from dateutil import tz
import configparser as cp
import urllib.parse as up
class Entry:
    def __init__(self, id, title, description, link):
        self.id = id
        self.title = title
        self.description = description
        self.link = link

    def __str__(self):
        return f'{self.title}\n\n{self.description}\n\n{self.link}'

    def __repr__(self):
        return self.__str__()


    
def format_title(title):
    title = html.unescape(title)
    title = markdownify(title)
    title = '# ' + title
    return title

def format_desc(description):
    def parse_link_from_desc(description):
        soup = bs4.BeautifulSoup(description, 'html.parser')
        element = soup.find('a')
        element.extract()
        return str(soup)
    def adjust_length(description):
        if '**Budget**:' in description and len(description) > 1500:
            description = description.split('**Budget**:')
            description = description[0][:1500] + '...\n' + '**Budget**:' + description[1]
        elif '**Hourly Range**:' in description and len(description) > 1500:
            description = description.split('**Hourly Range**:')
            description = description[0][:1500] + '...\n' + '**Hourly Range**:' + description[1]
        elif len(description) > 1500:
            description = description[:1800] + '...\n'
        return description
    def format_date(description):
        config = cp.ConfigParser()
        config.read('config.ini')
        timezone = config['Settings']['Timezone']
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(timezone)
        
        time_format = "%B %d, %Y %H:%M"
        desc = description.split('**Posted On**:')
        time = desc[1].split('UTC')[0].strip() 
        time = datetime.strptime(time, time_format)
        time = time.replace(tzinfo=from_zone)
        time = time.astimezone(to_zone)
        time = time.strftime(time_format)
        return desc[0] + '**Posted On**:' + time + desc[1].split('UTC')[1]
    
    description = html.unescape(description)
    description = parse_link_from_desc(description)
    description = markdownify(description)
    description = adjust_length(description)
    description = format_date(description)
    return description

def format_link(link):
    return "**Link**: " + link.strip("?source=rss")

def create_search_query():
    config = cp.ConfigParser()
    config.read('config.ini')
    keywords = config['Settings']['Keywords']
    keywords = [keyword.strip() for keyword in keywords.split(',')]
    banned_keywords = config['Settings']['BannedKeywords']
    banned_keywords = [banned_keyword.strip() for banned_keyword in banned_keywords.split(',')]
    search_query = f"({' OR '.join(keywords)}) AND NOT ({' OR '.join(banned_keywords)})"
    search_query = up.quote(search_query)
    return search_query

def main():
    search_query = create_search_query()
    feed = fp.parse(f"https://www.upwork.com/ab/feed/jobs/rss?q={search_query}&sort=recency")
    entries = []
    for entry in feed.entries:
        id = entry.id
        title = format_title(entry.title)
        descr = format_desc(entry.description)
        link = format_link(entry.link)
        entries.append(Entry(id, title, descr, link))

    return entries


if __name__ == '__main__':
    print(main())