from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
import re
from bs4 import BeautifulSoup

engine = create_engine('sqlite:///epiquote.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Quote(Base):
  __tablename__ = 'quotes'
  id = Column(Integer, primary_key=True)
  author = Column(String, nullable=False)
  context = Column(String, nullable=True)
  content = Column(String, nullable=False)


def update_db():
  # First, get number of pages
  req = requests.get('https://epiquote.fr/last')
  if req.status_code != 200:
    error_exit()
  soup = BeautifulSoup(req.text, 'html.parser')
  total_pages = int(re.sub("[^0-9]", "", soup.find(class_='add-on').text))
  # Then import each page
  session = Session()
  page = 1
  while page <= total_pages:
    req = requests.get('https://epiquote.fr/last?page=' + str(page))
    if req.status_code != 200:
      error_exit()
    soup = BeautifulSoup(req.text, 'html.parser')
    quotes = soup.find_all(class_='span12')
    for q in quotes:
      id = int(q.find('a').text[1:])
      quote_db = session.query(Quote).filter_by(id = id).first()
      if quote_db is not None:
        continue
      author = q.find('strong').text
      context_soup = q.find('em')
      context = None if context_soup is None else context_soup.text
      content = q.find_all('p')[1].get_text('\n')
      quote = Quote(id=id, author=author, content=content, context=context)
      session.add(quote)
    page += 1
  session.commit()
  session.close()


def get_authors_count():
  session = Session()
  result_rows = session.query(Quote.author, func.count(Quote.author)).group_by(Quote.author).order_by(func.count(Quote.author).desc()).all()
  for r in result_rows:
    print (r[0] + ' - ' + str(r[1]))
  session.close()

def error_exit():
  print('Import error', file=sys.stderr)
  exit(1)


if __name__ == "__main__":
  Base.metadata.create_all(engine)
  update_db()