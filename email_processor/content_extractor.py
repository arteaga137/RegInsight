from bs4 import BeautifulSoup

def extract_content(email_body):
    soup = BeautifulSoup(email_body, 'html.parser')
    updates = []
    
    td_tags = soup.find_all('td')
    for td in td_tags:
        p_tags = td.find_all('p')
        for p in p_tags:
            updates.append(p.get_text(strip=True))
            print(len(updates))
    
    return updates