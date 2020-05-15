from twilio.rest import Client
from bs4 import BeautifulSoup
import requests
import datetime
import gspread
import pprint

# Input parameters 'data' and 'context' are provided by the Cloud Function at runtime
def main(data, context):
    
    # Google Sheets setup
    credentials_filepath = 'your-gcloud-credentials-for-default-service-account.json'
    gc = gspread.service_account(filename=credentials_filepath)
    wb = gc.open('My Google Sheet') # Worksheet name as you see it in Google Sheets
    sheet1 = wb.worksheet("Sheet1") # First sheet in the file
    sheet2 = wb.worksheet("Sheet2") # Second sheet in the file
    
    # Twilio authentication setup 
    account_sid = 'obtain-this-from-your-twilio-console'
    auth_token = 'obtain-this-from-your-twilio-console'
    client = Client(account_sid, auth_token)

    # BeautifulSoup setup
    pp = pprint.PrettyPrinter(depth=10)
    yesterdays_obituaries = 'https://thestarphoenix.remembering.ca/obituaries/all-categories/search?filter_date=yesterday&sort_by=obitslastname_meta&order=asc&limit=240'
    r = requests.get(yesterdays_obituaries) 
    soup = BeautifulSoup(r.content, 'html5lib')

    # Text all obituary name matches found within webpage 'soup'
    def send_text(found_matches):
        for i, j in found_matches.items():
            print(i + '\n' + j['Match Type'] + '\n' +
                 j['Category'] + '\n' + j['URL'] + '\n')
            message = client.messages.create(
                    body = '~ Automated obituary notifier ~\n' +
                    i + '\n' + j['Match Type'] + '\n' +
                    j['Category'] + '\n' + j['URL'] + '\n',
                    from_ = 'your-twilio-number',
                    to = 'recipient-number'
                    )
        print(message.sid)

    # Parse soup to retrieve relevant data from each obituary listed
    # e.g., the obituary URL, dates, status of 'in memoriam' or 'obituary'
    '''Input: a webpage soup
    Return: a dict of obituaries indexed by name'''
    def get_obituaries_dict(soup):
        ads = soup.findAll('div', attrs = {'class':'ap_ad_wrap'})
        details = {}
        # Loop over each obituary in soup and store its details in a dict
        # e.g. details = {'JANE DOE': {'URL': 'http...', 'Category': 'In Memoriam'...}, 'JOHN DANE': {'URL': ...}}
        for person in ads:
            name = person.find('div', attrs={'class':'name'}).text.replace('\n','').replace("  ", " ").upper()
            details[name] = {'Image': '', 'URL': '', 'Category': '', 'Dates1': '', 'Dates2': ''}
            dn = details[name]
            if str(person.find('img')['data-src']).find('placeholder') == -1:
                dn['Image'] = person.find('img')['data-src']
            dn['URL'] = 'https://thestarphoenix.remembering.ca' + person.a['href']
            dn['Category'] = person.find('span', attrs={'class':'category'}).text

            # findChildren() gives [<span>1982</span>, <span class="category">In Memoriam</span>]
            # obit dates can either be in Dates1 or Dates2 positions
            dates1 = person.find('div', attrs={'class':'dates'})
            if dates1.findChildren()[0].get_text() != '\n':
                dn['Dates1'] = dates1.findChildren()[0].get_text().replace('\n','').strip()
            dates2 = person.find('p', attrs={'class':'content'})
            if dates2:
                dates2_list = dates2.get_text().split('\n')
                try: 
                    if '-' in str(dates2_list[1]):
                        dn['Dates2'] = dates2_list[1].replace('\n','').strip()
                except: 
                    pass
        return details

    # Determine if any names from the user's list match webpage obituaries
    '''Input: NA
    Return: a dict of matched obituary names with correponding data for each person'''
    def determine_matches():
        rows_as_dicts = sheet2.get_all_records() # Each row in the sheet is a dict. Entire sheet is a list of dicts.
        last_names = [] # last name matches
        full_names = [] # full name matches
        # Loop over rows in Google Sheets to group names into two lists
        # depending on search type (* for only lastname, or full name)
        for i in rows_as_dicts:
            # Loop over column NAMES TO SEARCH to group each name into either the last_names or full_names list
            if i['NAMES TO SEARCH'].split(' ')[0] == '*':
                last_names.append(i['NAMES TO SEARCH'].split(' ')[-1])
            else:
                full_names.append(i['NAMES TO SEARCH'])

        # Determine matches between 'obits_dict' webpage and the user's list of full_names / last_names
        obits_dict = get_obituaries_dict(soup)
        matches = {}
        for i, j in obits_dict.items():
            if i in full_names:
                matches[i] = j
                matches[i]['Match Type'] = 'Full name match' # Add match type to dict value
                matches[i]['Match Date'] = datetime.datetime.today().strftime('%B %d, %Y')
            elif i.split(' ')[-1] in last_names:
                matches[i] = j
                matches[i]['Match Type'] = 'Last name match' # Add match type to dict value
                matches[i]['Match Date'] = datetime.datetime.today().strftime('%B %d, %Y')
        return matches

    # Append data from matched obituaries to a Google Sheet
    '''Input: NA
    Return: number of obituary matches found'''
    def trigger_append_matches():
        sheet1 = wb.worksheet("Sheet1")
        matches_as_list = []
        # Retrieve dict of matches
        matches = determine_matches()
        # Store matches in a list of lists to make gspread appending easier
        # e.g. ['JOHN DANE', 'http://..', 'In Memoriam'...]
        for i, j in matches.items():
            row = []
            row.append(i) 
            for k, l in j.items():
                row.append(l)
            matches_as_list.append(row)
        # Write each match row to Sheet1 for logging
        for match in matches_as_list:
            sheet1.append_row(match, value_input_option='RAW', insert_data_option=None, table_range=None)
        # If any matches were found at runtime, text the user
        if len(matches_as_list) >= 1:
            print(str(len(matches_as_list)) + " match(es) found!")
            send_text(matches)
        return len(matches_as_list)
    
    # Call trigger_append_matches which triggers all others:
    # trigger_append_matches() > calls > determine_matches() > calls > get_obituaries_dict(soup)
    trigger_append_matches()
    
if __name__ == '__main__':
    main('data', 'context')
