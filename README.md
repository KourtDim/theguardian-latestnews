# theguardian-latestnews
Python script for mining latest headlines from The Guardian

---The script starts by creating local directories for storing the data that will be mined.

os.mkdir("Data")
os.mkdir("Data\Headlines")
os.mkdir("Data\Headlines\Top10Words")
os.mkdir("Data\MostUsedWords")
os.mkdir("Data\MostUsedNames")

---Then it uses urllib.request.urlopen and bs4.BeautifulSoup in order to parse The Guardian's main page.

mainpage_url = "https://www.theguardian.com/international"
mainpage = urlopen(mainpage_url)
mainpage_soup= bs4.BeautifulSoup(mainpage,"html.parser")

---After all the news themes existing in the page are located with soup.find method 

themes_loc = mainpage_soup.find("ul",{"aria-label":"Submenu News"})
themes_links = themes_loc.findAll("a")

---Then by using a for loop the themes_url list is populated with the theme_links 


themes_url = []

# Populate the list of themes
for i in themes_links:
     theme_url = i.get("href")
     themes_url.append(theme_url)
 
 
 ---Nltk stopwords are inserted from the nltk.corpus and extra stopwords are added 
 
#Creating Stopwords
stop_words= nltk.corpus.stopwords.words('english')
more_stopwords = [",",".","'","I","!","The","?",";",":","He","It","She","´","’","<",">","`","“","\n","-","'s ","$","..."]
stop_words.extend(more_stopwords)

---Another for loop is used to construct every targeted link that will be mined

Make a list to store all the url that will be iterated in the loop
links = []
# Construct all the urls to iterate over

for i in themes_url:
     i = i+"/?page="
     for a in range(7):
          if a > 0:
               url = i + str(a)
               links.append(url)
               
---After inspecting the website I found out that the html div with class = fc-item__container
contained all the info and the link for each article and created 3 nested loops in order to:

1) find all those divs in every url from the links list :
for i in links:
     page = urlopen(i)
     soup = bs4.BeautifulSoup(page,"html.parser")
     find = soup.findAll("div",{"class":"fc-item__container"})

2) Iterate over every found div and mine the selected information (after inspecting the website again)

for f in find:
          headline = f.a.get_text()
          headline_theme = soup.h1.get_text()
          t = find[0].find("time",{"class":"fc-item__timestamp"})
          headline_timestamp = t.get("datetime")
          headlines.append(headline)
          headline_themes.append(headline_theme)       
          headline_timestamps.append(headline_timestamp)

3) Finally in order to populate the lists with data and clear noize the words from each headline are tokenized, and filtered with stopwords

for a in nltk.tokenize.word_tokenize(headline):
               if a.isalpha() == True and a not in stop_words:
                    words.append(a)
                    t = find[0].find("time",{"class":"fc-item__timestamp"})
                    date = t.get("datetime")
                    timestamp.append(date)
                    theme = soup.h1.get_text()
                    themes.append(theme)
                    
A little additional data cleaning for the timestamp data
Break the time stamp data in smaller categories and populate the lists

for i in timestamp:
     i = re.split("[T +]",i)
     calendar.append(i[0])
     hour.append(i[1])
 
 Then various dataframes are created for different uses of analysis:
 

     
