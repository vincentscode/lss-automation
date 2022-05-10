
def extract_table_data(table):
    items = {}
    trs = table.find_all('tr')
    for tr in trs:
        tds = [td.get_text(strip=True) for td in tr.find_all('td')]
        if len(tds) != 2:
            continue
        items[tds[0]] = tds[1]
    return items

def extract_table_text(table):
    rows = []
    trs = table.find_all('tr')
    headerow = [td.get_text(strip=True) for td in trs[0].find_all('th')] # header row
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
    return rows

def extract_table_html(table):
    rows = []
    trs = table.find_all('tr')
    headerow = [td for td in trs[0].find_all('th')] # header row
    if headerow: # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs: # for every table row
        rows.append([td for td in tr.find_all('td')]) # data row
    return rows
