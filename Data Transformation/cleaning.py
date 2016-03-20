from pymongo import MongoClient
import re , string


def remove_url(strng):

    REGEXEN = {} # :nodoc:

    # URL related hash regex collection
    REGEXEN['valid_preceding_chars'] = re.compile("(?:[^\/\"':!=]|^|\:)")
    punct = re.escape(string.punctuation)
    REGEXEN['valid_domain'] = re.compile('(?:[^%s\s][\.-](?=[^%s\s])|[^%s\s]){1,}\.[a-z]{2,}(?::[0-9]+)?' % (punct, punct, punct), re.IGNORECASE)
    REGEXEN['valid_url_path_chars'] = re.compile('[\.\,]?[a-z0-9!\*\'\(\);:=\+\$\/%#\[\]\-_,~@\.]', re.IGNORECASE)
    # Valid end-of-path chracters (so /foo. does not gobble the period).
    #   1. Allow ) for Wikipedia URLs.
    #   2. Allow =&# for empty URL parameters and other URL-join artifacts
    REGEXEN['valid_url_path_ending_chars'] = re.compile('[a-z0-9\)=#\/]', re.IGNORECASE)
    REGEXEN['valid_url_query_chars'] = re.compile('[a-z0-9!\*\'\(\);:&=\+\$\/%#\[\]\-_\.,~]', re.IGNORECASE)
    REGEXEN['valid_url_query_ending_chars'] = re.compile('[a-z0-9_&=#]', re.IGNORECASE)
    REGEXEN['valid_url'] = re.compile('''
        (%s)
        (
            (https?:\/\/|www\.|bit\.ly)
            (%s)
            (/%s*%s?)?
            (\?%s*%s)?
        )
        ''' % (
            REGEXEN['valid_preceding_chars'].pattern,
            REGEXEN['valid_domain'].pattern,
            REGEXEN['valid_url_path_chars'].pattern,
            REGEXEN['valid_url_path_ending_chars'].pattern,
            REGEXEN['valid_url_query_chars'].pattern,
            REGEXEN['valid_url_query_ending_chars'].pattern
        ),
    re.IGNORECASE + re.X)
    strng = REGEXEN['valid_url'].sub(r'', strng)

    return strng



def cleanThis (strng):

    # regex to remove the url   
    strng = remove_url(strng)

    # regex to remove emoji 
    try:
        # Wide UCS-4 build
        emoji_unicode =  re.compile(u'['
            u'\U0001F300-\U0001F64F'
            u'\U0001F680-\U0001F6FF'
            u'\u2600-\u26FF\u2700-\u27BF]+', 
            re.UNICODE)
    except re.error:
        # Narrow UCS-2 build
        emoji_unicode = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u26FF\u2700-\u27BF])+', 
            re.UNICODE)

    strng = emoji_unicode.sub(r'', strng)

    # split the strng based on the space
    str_array = strng.split()
    clean_string = ""
    stopwords = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

    #remove non ascii characters
    first = True

    for word in str_array:
        cl_word = ""
        i = 0
        length = len(word)
        neglect = False
        if length >0 and word[0] == "@":
            continue

        while i<length and not neglect:
            if word[i] == "'":
                i = i+1
            elif word[i] == "$" or word[i] == ":" or word[i] == ";" or ord(word[i]) - ord('0') >= 0 and ord(word[i]) - ord('9') <= 0:
                neglect = True  
            elif ord(word[i]) - ord('a') >= 0 and ord(word[i]) - ord('z') <= 0:
                cl_word += word[i]
            elif ord(word[i]) - ord('A') >=0 and ord(word[i]) - ord('Z') <=0:
                cl_word += word[i]
            i += 1          

        # parse and remove the strngs which are stop words

        if(cl_word not in stopwords and not neglect):
            
            if(not first):
                clean_string += " "
                clean_string += cl_word
            else:
                clean_string += cl_word
                first = False   
                
    return clean_string

client = MongoClient()
db = client.Tweets
#db = client.randomDB

count = 0

#cleanThis("https://www.microsoft.com www.yahoo.com dsfj fsahjkas bit.ly//sjajkf")
#remove_url("https://www.microsoft.com www.yahoo.com dsfj fsahjkas bit.ly//sjajkf :P :o" )

#no_of_tweets = 10
lmt = 10000
no_of_tweets = db.Tweets_data.find().count()

while count < no_of_tweets:
    cursor = db.Tweets_data.find({}, {'text':1}).skip(count).limit(lmt)
    #cursor = db.random.find({}, {'text':1}).skip(count).limit(lmt)
    count += lmt
    for record in cursor:
        strng = cleanThis(record['text'])
        #print(strng)
        db.Tweets_data.update({'_id': record['_id']}, {'$set': {'sanitized_text' : strng}})
        #db.random.update({'_id' : record['_id']}, { '$set': {'new_field' : strng} })
    print(str("{0} are updated".format(count))) 




