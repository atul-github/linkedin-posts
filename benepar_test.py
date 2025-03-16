import spacy
import benepar
from spacytextblob.spacytextblob import SpacyTextBlob

def run():
    parser =  benepar.Parser("C:\\Users\\<userid>\\.benepar_model\\benepar_en3") # benepar.Parser("~/.benepar_model/benepar_en3")
    def get_mentions(text):
        doc = nlp(text)
        return doc

    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe("benepar", config={"model": "benepar_en3"})
    nlp.add_pipe("spacytextblob")
    

    temp = get_mentions("Atul did great job at AI and now able to work on very complex AI work")
    print(temp.ents)

if __name__ == "__main__":
    run()
