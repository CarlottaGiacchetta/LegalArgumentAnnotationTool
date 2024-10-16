from openai import OpenAI
import xml.etree.ElementTree as ET
from collections import defaultdict
import json

class AddAnnotations:
    '''
    La classe AddAnnotations utilizza l'API di OpenAI per analizzare e classificare argomentazioni
    di supporto estratte da un documento XML legale in una delle categorie predefinite. 
    L'API OpenAI viene utilizzata per determinare automaticamente la sottocategoria più appropriata per ciascun argomento.
    
    Argomenti:
    - model_name (str): il nome del modello OpenAI da utilizzare.
    - max_tokens (int): il numero massimo di token per ciascuna richiesta API.
    - openai_api_key (str): la chiave API per autenticare l'accesso a OpenAI.
    
    Metodi principali:
    - annotations(element): itera sugli elementi XML e classifica gli argomenti.
    - parse_category(categories, response_content): analizza la risposta dell'API e aggiorna il conteggio delle categorie.
    - call_annotations(name, mult_run): esegue il processo di annotazione e permette di salvare i risultati di più esecuzioni in un file JSON.
    '''

    def __init__(self, model_name='gpt-4o-mini', max_tokens=2000, openai_api_key=None):
        self.model_name = model_name
        self.max_tokens = max_tokens
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)

    def annotations(self, element):
        '''
        Analizza ciascun elemento XML alla ricerca dell'attributo 'SUP' e utilizza l'API OpenAI
        per classificare l'argomento di supporto in una delle categorie.
        
        Ritorna:
        - categories (dict): un dizionario con il conteggio per ciascuna categoria.
        '''
        categories = defaultdict(int)
        for elem in element.iter():
            if 'SUP' in elem.attrib:
                print('1. Testo:', elem.text)
                print(f"2. Tag: {elem.tag}")
                print("3. Attributi:", elem.attrib)
                messaggi = [
                    {
                        "role": "system", 
                        "content": (
                            "You are an expert assistant in analyzing legal texts. "
                            "Your task is to classify a supporting argument into one of the following subcategories, "
                            "or to indicate that none is appropriate: \n"
                            "- **Historical Arguments**: Historical arguments aim to interpret the law based on the original intentions of the framers (the drafters) and the ratifiers (those who approved it). This approach seeks to reconstruct the historical context and debates of the time to better understand the values and objectives that guided the legislators' choices (e.g., references to preparatory work on the law, legislative debates).\n"
                            "- **Textual Arguments**: Textual arguments rely exclusively on the literal meaning of the words in the law, focusing on the words that are actually present in the document (e.g., reference to the literal content of the legal provision).\n"
                            "- **Structural Arguments**: Structural arguments are based on the analysis of the overall system and related provisions. Structural reasoning assumes that each provision should not be viewed in isolation but as part of an integrated and coherent system (e.g., reference to the normative system, meaning related provisions within the code or other laws).\n"
                            "- **Prudential Arguments**: Prudential arguments are based on an assessment of the practical pros and cons of a legal decision. This type of argument considers the potential consequences that a ruling might have on society and seeks to avoid outcomes that could cause significant harm or complications. Prudential reasoning analyzes the practical implications and real-world impacts of a decision, weighing the potential benefits against the possible drawbacks (e.g., cost-benefit analysis resulting from a particular argument and application of the law).\n"
                            "- **Doctrinal Arguments**: Doctrinal arguments rely on the use of precedents, meaning decisions made in similar previous cases, either by lower courts or by the Supreme Court (e.g., reference to relevant case law rulings).\n"
                            "- **Ethical Arguments**: Ethical arguments are based on general principles or moral values and on what is considered right or wrong, with the aim of aligning judicial decisions with the values and ideals of society. This type of argument seeks to reflect and promote a sense of justice that mirrors the ethical principles shared by the community (e.g., reference to values, principles, ethics, and morals).\n\n"
                            "If none of the categories is suitable, you may indicate that the text does not fit into any of them."
                        )
                    },
                    {
                        "role": "user", 
                        "content": (
                            f"The following text is a supporting argument: {elem.text}. "
                            "Analyze the content and identify the most relevant subcategory from the provided options, "
                            "or indicate if none of the subcategories is appropriate. "
                            "Please format the response as follows:\n\n"
                            "- Subcategory: **[Name of Category or 'None']**\n"
                            "- Reason: [Explanation for the classification]"
                        )
                    }
                ]
                risposta = self.client.chat.completions.create(
                    model= self.model_name,
                    messages=messaggi,
                    temperature=0.7
                )
                print("\nRisposta:",risposta.choices[0].message.content.strip())
                codice = self.parse_category(categories, risposta.choices[0].message.content.strip())
                elem.attrib[f'SUP-{codice}'] = elem.attrib.pop('SUP')
                print('Nuova chiave associata:', elem.attrib)
                print("\n-------------------------------\n")

        
        return categories
                
            
    
    def parse_category(self, categories, response_content):
        '''
        Analizza la risposta dell'API per identificare la categoria e aggiorna il contatore per ciascuna categoria.
        
        Argomenti:
        - categories (dict): dizionario contenente i contatori delle categorie.
        - response_content (str): testo della risposta ricevuta dall'API OpenAI.
        '''
        category_line = next((line for line in response_content.splitlines() if line.startswith("- Subcategory:")), None)
        if category_line:

            category_name = category_line.split("**")[1].strip()
            category_map = {
                "Historical Arguments": "HIS",
                "Textual Arguments": "TXT",
                "Structural Arguments": "STRUCT",
                "Prudential Arguments": "PRUD",
                "Doctrinal Arguments": "DOCT",
                "Ethical Arguments": "ETH",
                "None": "None"
            }
            categories[category_map.get(category_name, "None")] += 1
        else:
            categories["None"] += 1
        return category_map.get(category_name, "None")
        


    def call_annotations(self, name, mult_run=False):
        '''
        Esegue il processo di annotazione per il file XML specificato. Se mult_run è True, esegue 20 cicli
        e salva i risultati in un file JSON.
        
        Argomenti:
        - name (str): nome del file XML da analizzare.
        - mult_run (bool): se True, esegue l'analisi 20 volte e salva i risultati in un file JSON.
        '''
        tree = ET.parse(f'demosthenes_dataset/{name}')
        root = tree.getroot()
        if mult_run:
            results = {}
            for i in range(20):
                categories = self.annotations(root)
                print("Categorie contate:", dict(categories))
                results[f'run{i}'] = dict(categories)
            with open('categories_results.json', 'w') as outfile:
                json.dump(results, outfile, indent=4)
            print("Risultati salvati in 'categories_results.json'")
        else:
            categories = self.annotations(root)
            print("Categorie contate:", dict(categories))
        # Salva il file XML modificato con un nuovo nome
        tree.write(f'demosthenes_dataset_new/{name.split(".")[0]}_annotated.xml')
        print(f"File XML modificato salvato come '{name.split('.')[0]}_annotated.xml'")

        
