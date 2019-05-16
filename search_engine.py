# Final project
# Search engine
# Ke Xu

#before running this code make sure that the html files is in input folder
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import glob
import re

'-----------------------------------------------------------text process-------------------------------------------------'
#remove all puntuations and stopwords from text and return a word list
def textProcess(text):
    temp = re.sub(r'\W',' ',text)
    temp = temp.lower()
    temp = temp.split()
    #this is just a part of stop words, we can use nltk to find more
    stopwords = {'what','who','is','a','at','is','he','on','the','an','this','that','of','t','s','d','r','to','am','but','again'}
    temp  = [word for word in temp if word not in stopwords]
    return temp

#get the text and url from html files
def get_text_link(path): 
    textList = []
    urlList = []
    for p in path:
        html = open(p, 'rb')
        soup = BeautifulSoup(html, 'html.parser')  
        
        #get text from html
        #remove javascript and stylesheet code
        for ss in soup(["script", "style"]):
            ss.extract()
        text = soup.get_text()
        text = textProcess(text)
        textList.append(text)
        
        #find url of each html file, for saved html file the url is at the second line in html file
        temp = soup.prettify()
        code = temp.splitlines()[1]
        url = ''
        for i in range(len(code)):
            if code[i] == 'h':
                for l in range(i,len(code)-4):
                    url = url + code[l]
                break
        urlList.append(url)
        
    return textList, urlList

# make occurrence list
def occurrence_list(data):
    ocu = defaultdict(list)
    for idx, val in enumerate(data):
        for word in val:
            ocu[word].append(idx)
    return ocu

'-----------------------------------------------------------compressed trie-------------------------------------------------'
# compressed trie nodes
class Node:
    def __init__(self, children=None, is_leaf=False):
        self.children = {} 
        self.is_leaf = is_leaf
        if children:
            self.children = children

#to check if two string has same prefix, then split them base on prefiex
def getPrefix(s1, s2):
    n = 0
    s = zip(s1,s2)
    #if l1 and l2 are same we increase index n
    for l1, l2 in s:
        if l1 != l2:
            break
        n += 1
    
    pre = s1[:n]            #this is the prefix that both s1 and s2 have
    remain1 = s1[n:]        #this is the remaining part of s1 exclude the prefix
    remain2 = s2[n:]        #this is the remaining part of s2 exclude the prefix
    return pre, remain1, remain2

# add node to the trie
def insert(trie, word):
    node = trie
    
    for key in node.children:
        #check if there is a prefix match of the word in trie
        pre, remain1, remain2 = getPrefix(key, word)

        if remain1 == '':
            # there is a match of a part of the key
            # then we keep seach the remaining part of that word
            child = node.children[key]
            return insert(child, remain2)

       # if we found there is a prefix match between the key and the prefix of the word 
		# we need delete that node.children[key] and use the prefix we just got to create 
		# a new node then add remaining part of that key and word as the new node's children. 
        if pre != '':
            child = node.children[key]

            # split child
            temp = Node(children={remain1: child})
            # delete that key
            del node.children[key]
            # using prefix to create new node
            node.children[pre] = temp
            return insert(temp, remain2)
        
    #if there is no any match found then we add a new child with that word to root
    node.children[word] = Node(is_leaf=True)

#check if the word is in trie 
def find(trie, word):
    node = trie

    for key in node.children:
        #check if there is a match of word in trie
        pre, remain1, remain2 = getPrefix(key, word)
        
        #if there is no remaining part of that word and the key node is leaf then return True
        #if the key node is not leaf then return False
        if remain2 == '':
                return node.children[key].is_leaf
        #if a part of word match a key in trie, then keep check remaining part until nothing left
        if remain1 == '':
            return find(node.children[key], remain2)
    
    # if can't find any matchs then return false
    return False

'-----------------------------------------------------------build------------------------------------------------------------'
#build an occurrence_list with frequency of each word in text
def make_wordDict(text):
    word_dict = defaultdict(list)
    text, url = get_text_link(path)         #get all text and the url list
    temp = occurrence_list(text)        #get the list of occurrence list
    word_dict.update(temp)
    return word_dict, url

#build and store all of the word in occurrence list to trie 
def bulid_trie(word_dict):
    trie = Node()
    # for each word in occurrence list, then insert it to trie
    for word in word_dict:
        insert(trie, word)
    return trie

'-----------------------------------------------------------search and print-------------------------------------------------'
#search for word, then return occurrence list of that word
def search(s, trie, ocu):
    result ={}
    text = textProcess(s)
    for i in text:
        if find(trie, i):
            result.update({i: ocu[i]})
    return result

#rank the result depend on frequency of each word
def rankingResult(search_result):
    result=[]
    #if search_result is empty then return an empty set
    if len(search_result) ==0:
        return result
    
    #let first be first element in search_result
    first = list(search_result.keys())[0]
    temp=set(search_result[first])              #let temp be first element in search_result and remove duplicates
    for i in search_result:                     
        temp = temp & set(search_result[i])     #if there are multiple results then we need find intersection of them
        result = result + search_result[i]      
    
    count = Counter(result)                     #find frequence of each web page
    result = count.most_common()                #make the result be decreasing order
    finalResult= []
    
    #check if any index of web page is also in the intersection set(temp) then add them to final result
    for i in result:
        if i[0] in temp:
            finalResult.append(i[0])
    return finalResult

#print the result
def printResult(result,url):
    # if result is empty
    if not result:
        print(f'\n No result found. \n')
        return
    print("\n Search results: \n")
    for idx, val in enumerate(result):
        print(f'{idx+1}: {url[val]}')
'-----------------------------------------------------------main---------------------------------------------------------------'
if __name__ == '__main__':
    
    #read all html file name from input folder
    path = glob.glob('input\*.html')
    
    #make occurrence List and url list
    occurrenceList, url = make_wordDict(path)
    
    #create trie
    trie = bulid_trie(occurrenceList)
    
    #let user input and search
    while True:
        strIn = input("Enter text(enter # if want quit): ");
        if strIn == '#':
            break;
        result = search(strIn, trie, occurrenceList)
        rankedResult = rankingResult(result)
        printResult(rankedResult,url)
