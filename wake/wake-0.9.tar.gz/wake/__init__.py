from broth import Broth
from bz2 import BZ2Decompressor
from os.path import isfile
from re import findall
from re import finditer
from re import IGNORECASE
from re import MULTILINE
from re import sub
from requests import get
from subprocess import call
from subprocess import check_output
from urllib.request import urlretrieve
from urllib.request import urlopen
import xml.etree.ElementTree as ET

blacklist = ["User talk:", "Talk:", "Comments:", "User:", "File:", "Category:", "Wikinews:", "Template:", "Category talk:", "MediaWiki:", "User:"]

patterns = {
    "category": { "pattern": "\[\[Category:[A-Za-z- |]+\]\]", "repl": "", "flags": 0 },
    "ref": { "pattern": "<ref.*/(ref)?>", "repl": "", "flags": 0 },
    "header2": { "pattern": "==[A-Za-z -]*==", "repl": "", "flags": 0 },
    "header3": { "pattern": "===[A-Za-z -]*===", "repl": "", "flags": 0 },
    "simple_link": { "pattern": "\[\[([A-Za-z- ]*)\]\]", "repl": "\\1", "flags": 0 },
    "reference": { "pattern": "(?<=\n)\*.*(?=\n)", "repl": "", "flags": 0 },
    "simple_brackets": { "pattern": "{{([A-za-z- ]*)}}", "repl": "\\1", "flags": 0 },
    "main": { "pattern": "{{Main[A-za-z- \|]*}}", "repl": "", "flags": IGNORECASE },
    "comment": { "pattern": "<!--.*-->", "repl": "", "flags": 0 },
    "use": { "pattern": "{{use[^}]*}}", "repl": "", "flags": 0 },
    "seealso": { "pattern": "{{see also[^}]*}}", "repl": "", "flags": IGNORECASE }
}

def remove_text_between(text, start_text, end_text):
    try:
        start = 0
        len_end_text = len(end_text)
        for n in range(1000):
            try:
                start = text.index(start_text, start)
            except ValueError:
                break
            try:
                end = text.index(end_text, start)
            except ValueError:
                break
            text = text[:start] + text[end+len_end_text:]
        return text
    except Exception as e:
        print("[wake.remove_refs] hit exception:", e)
        raise(e)    

def remove_references(text):
    text = remove_text_between(text, start_text="<ref", end_text="</ref>")
    text = remove_text_between(text, start_text="{{refbegin", end_text="{{refend}}")
    return text    

def clean_title(title):
    return title.replace("'","\\'").replace("`","\\`").replace('"','\\"').rstrip("\\")
    
def find_index_of_sublist(items, target):
    try:
        num_to_match = len(target)
        matched = []
        for index, item in enumerate(items):
            if item == target[len(matched)]:
                matched.append(index)
                if len(matched) == num_to_match:
                    return (matched[0], matched[-1])
            elif item == target[0]:
                matched = [index]
            else:
                matched = []
        return (None, None)
    except Exception as e:
        print("[wake.find_index_of_sublist] hit error:", e)
        raise(e)

def get_links(page_text):
    try:
        links = []
        
        brackets = finditer("(\[\[|\]\])", page_text)

        # convert brackets to dictionaries
        brackets = [{"index": b.start(), "type": "open" if b.group(0) == "[[" else "close" } for b in brackets]

        while len(brackets) >= 2:

            types = [b["type"] for b in brackets]

            open_index, close_index = find_index_of_sublist(types, ["open", "close"])

            if open_index is None or close_index is None:
                print("[wake.get_links] breaking from loop because not able to find open and close in a row")
                break

            link_text = page_text[brackets[open_index]["index"]+2:brackets[close_index]["index"]]

            brackets = [bracket for index, bracket in enumerate(brackets) if not (open_index <= index <= close_index)]

            parts = link_text.split("|")
            wiki_title = parts[0].split("#")[0]
            display_text = parts[-1]
            link = { "title": wiki_title, "display_text": display_text }
            links.append(link)

        return links
    except Exception as e:
        try: print("[wake.get_links] brackets:", brackets)
        except: pass    
        print("[wake.get_links] hit exception:", e)
        raise(e)
            

#def get_link_titles(page_text):
#    return [clean_title(link) for link in get_links(page_text)]

def download_if_necessary(url, debug=False):
    if debug: print("starting download_if_necessary with: " + url) 
    path_to_downloaded_file = "/tmp/" + url.split("/")[-1] 
    if not isfile(path_to_downloaded_file): 
        urlretrieve(url, path_to_downloaded_file) 
        print("downloaded:", url, "to", path_to_downloaded_file) 
    return path_to_downloaded_file 

def unzip_if_necessary(filepath):
    if filepath.endswith(".zip"):
        path_to_unzipped_file = filepath.rstrip(".zip")
        if not isfile(path_to_unzipped_file):
            call(["unzip", filepath, path_to_unzipped_file])
        return path_to_unzipped_file
 

def get_most_recent_available_dump(wiki="enwiki", debug=True):

    try:

        if debug: print("starting get_most_recent_available_dump")
        wiki_url = "https://dumps.wikimedia.org/" + wiki + "/"

        broth = Broth(get(wiki_url).text)
        print("broth:", type(broth))
        dumps = [a.get("href").rstrip("/") for a in broth.select("a") if not a.text.startswith("latest") and not a.text.startswith("entities") and a.get("href") != "../"]
        dumps.reverse()
        print("dumps:", dumps)

        for dump in dumps:
           jobs = get(wiki_url + dump + "/dumpstatus.json").json()['jobs']
           if jobs['geotagstable']['status'] == "done" and jobs['pagepropstable']['status'] == "done" and jobs['articlesdumprecombine']['status'] == "done":
               print("geotags dump on " + dump + " is ready")
               return dump, jobs

    except Exception as e:
        print(e)
        raise e

def run_sql(sql_statement, db_name='', debug=False):
    try:
        if debug: print("starting run_sql with:", sql_statement)
        sql_statement = sql_statement.replace('"', '\\"')
        bash_command = '''mysql -u root ''' + db_name + ''' -e "''' + sql_statement + '''"'''
        if debug: print("bash_command:", bash_command)
        output = check_output(bash_command, shell=True).decode("utf-8")
        if debug: print("output: " + output)
        # format as rows of dictionary objects
        lines = output.strip().split("\n")
        if lines:
            header = lines[0].split("\t")
            if debug: print("header:", header)
            if len(lines) > 1:
                result = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
                if debug: print("result:", str(result))
                return result
    except Exception as e:
        print("[wake] run_sql caught exception " + str(e) + " while trying to run " + sql_statement)
        raise e


def get_english_wikipedia_pages(num_chunks=1000000000, debug=False):
    
    try:
    
        ymd, jobs = get_most_recent_available_dump()
        url = "https://dumps.wikimedia.org/enwiki/" + ymd + "/enwiki-" + ymd + "-pages-articles.xml.bz2"
        print("url:", url)
    
        decompressor = BZ2Decompressor()
        print("decompressor:", decompressor)
        
        req = urlopen(url)
        print("req:", req)
        
        start_page = b"<page>"
        end_page = b"</page>"
        
        text = b""
        for n in range(num_chunks):
            if debug: print("chunk")
            chunk = req.read(16 * 1024)
            if not chunk:
                break
            if debug: print("read")
                
            text += decompressor.decompress(chunk)
            if debug: print("text:", type(text))
            #print("text:", text)
            #with open("/tmp/output.txt", "a") as f:
                #f.write(text.decode("utf-8"))
            
            num_pages = text.count(start_page)
            #print("num_pages:", num_pages)
            for n in range(num_pages):
                
                start_page_index = text.find(start_page)
                
                if start_page_index != -1:
                    
                    #print("start_page_index:", start_page_index)
                    #print("text:", text[:100])
                    
                    # dump any text before start_page
                    text = text[start_page_index:]
                    #print("text:", text[:100])
                    
                    end_page_index = text.find(end_page)
                    #print("end_page_index:", end_page_index)
                    
                    if end_page_index != -1:
                        
                        end_page_index += len(end_page)
                        
                        page = text[:end_page_index]
                        
                        text = text[end_page_index:]
                        
                        #print("page:", page[:20], "...", page[-20:])
                        
                        parsed = ET.fromstring(page)
                        
                        yield parsed
    except Exception as e:
        print("[wake.get_english_wikipedia_pages] found exception:", e)
        raise(e)
                    
def get_valid_english_wikipedia_pages(num_chunks=5000000000000, debug=False):
    
    try:
    
        for page in get_english_wikipedia_pages(num_chunks=num_chunks, debug=debug):
            
            if debug: print("page:", type(page))
    
            page_id = page.find("id").text
            
            page_title = page.find("title").text
            
            page_text = page.find("revision/text").text
            
            if page_id and page_title and page_text:
                
                    if page_title not in blacklist and not page_text.startswith("#REDIRECT"):
                        
                        yield { "id": page_id, "title": page_title, "text": page_text }
                        
    except Exception as e:
        print("[wake.get_valid_english_wikipedia_pages] found exception:", e)
        raise(e)

def clean_page_text(text):
    for value in patterns.values():
        text = sub(value["pattern"], value["repl"], text, flags=value["flags"])
    return text