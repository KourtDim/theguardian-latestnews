import bs4
from urllib.request import urlopen
import re
import pandas as pd
import nltk
import os
import time

start_time = time.time()



os.mkdir("Data")
os.mkdir("Data\Headlines")
os.mkdir("Data\Headlines\Top10Words")
os.mkdir("Data\MostUsedWords")
os.mkdir("Data\MostUsedNames")

print("New Directories Created")

# Find News Themes:
mainpage_url = "https://www.theguardian.com/international"
mainpage = urlopen(mainpage_url)
mainpage_soup= bs4.BeautifulSoup(mainpage,"html.parser")
themes_loc = mainpage_soup.find("ul",{"aria-label":"Submenu News"})
themes_links = themes_loc.findAll("a")


# List of themes
themes_url = []

# Populate the list of themes
for i in themes_links:
     theme_url = i.get("href")
     themes_url.append(theme_url)
     
# Empty lists for the DataFrame

words     = []
pos_tag   = []
themes    = []
timestamp = []
calendar  = []
hour      = []

# Headlines

headlines           = []
headline_themes     = []         
headline_timestamps = []
         
#Creating Stopwords
stop_words= nltk.corpus.stopwords.words('english')
#Adding extra stopwords
more_stopwords = [",",".","'","I","!","The","?",";",":","He","It","She","´","’","<",">","`","“","\n","-","'s ","$","..."]
#Extending the stopwords list
stop_words.extend(more_stopwords)

# Make a list to store all the url that will be iterated in the loop
links = []
# Construct all the urls to iterate over

for i in themes_url:
     i = i+"/?page="
     for a in range(7):
          if a > 0:
               url = i + str(a)
               links.append(url)
               
# Iterate over all the links and gather the data

for i in links:
     page = urlopen(i)
     soup = bs4.BeautifulSoup(page,"html.parser")
     find = soup.findAll("div",{"class":"fc-item__container"})
     
     for f in find:
          headline = f.a.get_text()
          headline_theme = soup.h1.get_text()
          t = find[0].find("time",{"class":"fc-item__timestamp"})
          headline_timestamp = t.get("datetime")
          headlines.append(headline)
          headline_themes.append(headline_theme)       
          headline_timestamps.append(headline_timestamp)
          
          for a in nltk.tokenize.word_tokenize(headline):
               if a.isalpha() == True and a not in stop_words:
                    words.append(a)
                    t = find[0].find("time",{"class":"fc-item__timestamp"})
                    date = t.get("datetime")
                    timestamp.append(date)
                    theme = soup.h1.get_text()
                    themes.append(theme)
     page.close()

# Break the time stamp data in smaller categories and populate the lists

for i in timestamp:
     i = re.split("[T +]",i)
     calendar.append(i[0])
     hour.append(i[1])

# Create the part of speech tags and store them in the list

pos = nltk.pos_tag(words)
for l,k in pos:
     pos_tag.append(k)

# Create words Dataframe    
df                  = pd.DataFrame(words,columns=["Word"])
df["Theme"]         = themes
df["Pos_Tag"]       = pos_tag 
df["Timestamp"]     = timestamp
df["Calendar"]      = calendar
df["Hour"]          = hour

# Store it to csv
df.to_csv("Data\AllWords.csv")

# Word Counts DataFrame
wordcount= df.Word.value_counts()
df_wordcount= wordcount.to_frame()
df_wordcount["Name"]= df_wordcount.index
df_wordcount.to_csv("Data\MostUsedWords\MostUsedWords_AllWords.csv")

# Break the timestamp for the headlines timestamps

for i in headline_timestamps:
     i = re.split("[T +]",i)
     calendar.append(i[0])
     hour.append(i[1])

# Create the headlines df
df_headlines                  = pd.DataFrame(headlines,columns=["Headlines"])
df_headlines["Theme"]         = headline_themes
df_headlines["Timestamp"]     = headline_timestamps

df_headlines.dropna()
df_headlines["Headlines"] = df_headlines["Headlines"].str.replace("\n","")

# Store it to csv
df_headlines.to_csv("Data\Headlines\Headlines.csv")

# Name Entities

entities=[]

for chunk in nltk.ne_chunk(nltk.pos_tag(words)):
     if hasattr(chunk, 'label'):
          entities.append((chunk.label(), ' '.join(c[0] for c in chunk.leaves())))

chunk =[]
entity=[]

for c,w in entities:
	chunk.append(c)
	entity.append(w)

chunk_df = pd.DataFrame(chunk,columns=["Chunk"])
chunk_df["Entity"]= entity

# Name count Dataframe
namecount = chunk_df.Entity.value_counts()
namecount_df = namecount.to_frame()
namecount_df.to_csv("Data\MostUsedNames\MostUsedName_AllNames.csv")

# GroupBy Theme

GroupByTheme = df.groupby(["Theme"])
WordCount = GroupByTheme.Word.value_counts()
Index = GroupByTheme.Word.value_counts().index

w = []
t = []
v = []

for i in WordCount:
     v.append(i)

for i in Index:
     t.append(i[0])
     w.append(i[1])

df_values = pd.DataFrame(w,columns=["Word"])
df_values["Theme"] = t
df_values["Count"] = v


values_group = df_values.groupby(["Theme"])

n = 50
df_values_Top = df_values.nlargest(n,columns="Count")
df_values_Top.to_csv("Data\MostUsedWords\MostUsedWords_50.csv")


for i in values_group.groups.keys():
	m = values_group.get_group(i)
	j = m.nlargest(25,columns="Count")
	j.to_csv('Data\MostUsedWords\MostUsedWords_'+i.replace(" ","")+".csv")

# Name Entities
names = df.groupby(["Theme"])
chunks = []
w = []
t = []
c = []
for i in names.groups.keys():
     r= names.get_group(i)
     for chunk in nltk.ne_chunk(nltk.pos_tag(r["Word"])):
          if hasattr(chunk, 'label'):
               chunks.append((chunk.label(), ' '.join(c[0] for c in chunk.leaves())))
               t.append(i)

for ch,n in chunks:
     c.append(ch)
     w.append(n)

names_df = pd.DataFrame(w,columns=["Word"])
names_df["Type"] = c
names_df["Theme"] = t

                  
NamesGroupByTheme = names_df.groupby(["Theme"])
NamesWordCount = NamesGroupByTheme.Word.value_counts()
NamesIndex = NamesGroupByTheme.Word.value_counts().index

w = []
t = []
v = []

for i in NamesWordCount:
     v.append(i)

for i in NamesIndex:
     t.append(i[0])
     w.append(i[1])

df_names_values = pd.DataFrame(w,columns=["Word"])
df_names_values["Theme"] = t
df_names_values["Count"] = v


names_values_group = df_names_values.groupby(["Theme"])

n=50
names_values_count = df_names_values.nlargest(n,columns="Count")
names_values_count.to_csv("Data\MostUsedNames\MostUsedNames_50.csv")


for i in names_values_group.groups.keys():
	m = names_values_group.get_group(i)
	j = m.nlargest(50,columns="Count")
	j.to_csv('Data\MostUsedNames\MostUsedNames_'+i.replace(" ","")+".csv")

# Top Words Headlines Dataframes

top10 = df_wordcount.nlargest(10,columns="Word")
top10words = []
for i in top10.Name:
	top10words.append(i)
for i in top10words:
     a = df_headlines[df_headlines["Headlines"].str.contains(i)]
     a.to_csv("Data\Headlines\Top10Words\AllHeadlines_for_"+i+".csv")
          



elapsed_time = time.time() - start_time
print("Processing Time:"+str(elapsed_time))

print("Info \n The Headlines collected from The Guardian website start from: " + df.Calendar.min()+" till: "+df.Calendar.max())

