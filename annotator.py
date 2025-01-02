from openai import OpenAI
import xml.etree.ElementTree as ET
import json
import os



class AddAnnotations:
    """
    This class processes legal texts in XML format using OpenAI's API for semantic analysis and categorization. 
    It groups sentences based on meaning, assigns argument categories, and updates XML files with annotations.

    Key Features:
    - Groups sentences into semantic clusters with explanations.
    - Assigns predefined categories (e.g., Historical, Textual, Doctrinal) to groups.
    - Saves results in annotated XML and structured JSON formats.
    - Automatically manages file directories and API integration.

    Main Methods:
    - unified_struct: Groups sentences based on semantic logic.
    - parse_json_output: Validates and unifies API JSON responses.
    - annotations: Categorizes sentence groups and updates XML.
    - call_unifypar_struct & call_annotations: Orchestrate the grouping and annotation processes.

    Efficiently prepares legal datasets for further analysis or presentation.
    """


    def __init__(self, model_name='gpt-4o-mini', max_tokens=2000, openai_api_key=None):
        self.model_name = model_name
        self.max_tokens = max_tokens
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)

    def unified_struct(self, element, output_json, name):
        """
        This method analyzes and groups legal sentences from an XML structure based on semantic meaning. 
        It utilizes an AI model to cluster sentences into groups with clear reasoning for each grouping.

        Steps:
        1. Extracts sentences from the XML `element`, skipping those with the tag 'body'.
        2. Sends sentences to an AI model for semantic grouping, adhering to strict guidelines:
        - Groups must have a maximum of 7-8 sentences.
        - Sentences with no clear thematic connection are assigned `group_id: null`.
        3. Parses the AI response and maps each sentence to its assigned group.
        4. Updates the XML structure by adding a `Group` attribute to relevant elements.
        5. Saves the updated XML file to a specified directory.

        Inputs:
        - `element`: The XML element to process.
        - `output_json`: Path to save the AI's JSON response.
        - `name`: Name of the output XML file.

        Outputs:
        - An updated XML file saved in the `demosthenes_dataset_group` directory.
        """

        lista = []
        for i, elem in enumerate(element.iter()):
            if elem.tag != 'body':
                lista.append({'ID': elem.attrib.get('ID', f'ID{i}'), 'attrib': elem.attrib, 'text': elem.text})

        messaggi = [
            {
                "role": "system",
                "content": (
                    "You are an assistant skilled in the structural and semantic analysis of legal sentences. "
                    "You will receive sentences annotated with an ID and various attributes. "
                    "Your task is to group the sentences that share a common semantic logic or address the same topic.\n\n"
                    "Follow these **strict guidelines** when grouping the sentences:\n"
                    "1. **Do not exceed 7/8 sentences per group**: Under no circumstances should a group contain more than 8 sentences.\n"
                    "2. **Group by semantic meaning**: Ignore the IDs and order. Base the grouping purely on the meaning of each sentence.\n"
                    "3. **Leave unrelated sentences ungrouped**: Assign them to `group_id: null` with an explanation.\n"
                    "4. **Provide clear reasons for grouping**: Explain why sentences are grouped together, focusing on their shared logic or theme.\n\n"
                    "Format the response strictly as JSON:\n"
                    "{\n"
                    "  \"groups\": [\n"
                    "    {\n"
                    "      \"group_id\": 1,\n"
                    "      \"sentence_ids\": [\"ID1\", \"ID2\", \"ID3\"],\n"
                    "      \"reason\": \"Explanation for why these sentences are grouped together.\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"group_id\": 2,\n"
                    "      \"sentence_ids\": [\"ID4\", \"ID5\"],\n"
                    "      \"reason\": \"Explanation for this grouping.\"\n"
                    "    },\n"
                    "    {\n"
                    "      \"group_id\": null,\n"
                    "      \"sentence_ids\": [\"ID8\", \"ID20\"],\n"
                    "      \"reason\": \"Ungrouped sentences due to lack of thematic connection.\"\n"
                    "    }\n"
                    "  ]\n"
                    "}\n"
                )
            },
            {
                "role": "user",
                "content": (
                    "Here are some legal sentences annotated with IDs:\n\n"
                    f"{json.dumps(lista, indent=2)}\n\n"
                    "Please strictly adhere to the guidelines "
                    "Group unrelated sentences under `group_id: null`. Provide clear reasons for each group."
                )
            }
        ]

        risposta = self.client.chat.completions.create(
            model=self.model_name,
            messages=messaggi,
            temperature=0.2
        )
        contenuto_risposta = risposta.choices[0].message.content.strip()

        output_file, unified_json = self.parse_json_output(contenuto_risposta=contenuto_risposta, unified_json=None, file_path=output_json)
        if output_file is None:
            print("Errore: Impossibile elaborare l'output JSON.")
            return

       
        group_map = {item_id: group['group_id'] for group in output_file['groups'] for item_id in group['sentence_ids']}

        print(group_map)
        for elem in element.iter():
            if elem.tag != 'body' and 'ID' in elem.attrib:
                elem_id = elem.attrib['ID']
                if elem_id in group_map:
                    elem.set('Group', str(group_map[elem_id]))

       
        tree = ET.ElementTree(element)
        output_directory = 'demosthenes_dataset_group'
        os.makedirs(output_directory, exist_ok=True)

        tree.write(f'demosthenes_dataset_group/{name}', encoding="utf-8", xml_declaration=True)
        print(f"Updated XML file saved as 'demosthenes_dataset_group/{name}'.")



    def parse_json_output(self, contenuto_risposta, unified_json=None, file_path="output.json"):
        """
        This method processes raw JSON-like responses, validates their structure, 
        integrates them into a unified JSON object, and saves the result to a specified file.

        Steps:
        1. **Initialization**: Initializes `unified_json` if not provided, starting with an empty "groups" list.
        2. **Formatting Cleanup**: Removes Markdown-style delimiters (e.g., ```json```) and unescapes quotes in the response string.
        3. **Parsing**: Attempts to parse the cleaned string into a JSON object. If parsing fails, logs the error and returns the existing `unified_json` unchanged.
        4. **Integration**: Appends the parsed response to the "groups" list in `unified_json`.
        5. **File Saving**: Ensures the directory exists and saves the updated `unified_json` to the specified `file_path` in a human-readable format.
        6. **Error Handling**: Catches and logs any generic exceptions, returning `None` for the response JSON while preserving the existing `unified_json`.

        Inputs:
        - `contenuto_risposta` (str): The raw response string that resembles JSON.
        - `unified_json` (dict, optional): The cumulative JSON object to which new data is appended.
        - `file_path` (str): The file path where the updated JSON object is saved.

        Outputs:
        - `response_json` (dict): The parsed JSON object from the current response.
        - `unified_json` (dict): The cumulative JSON object with the new response integrated.
        """

    
        try:
            
            if unified_json is None:
                unified_json = {"groups": []}

            contenuto_risposta = contenuto_risposta.strip()
            if contenuto_risposta.startswith('```json') and contenuto_risposta.endswith('```'):
                contenuto_risposta = contenuto_risposta[7:-3].strip()
            contenuto_risposta = contenuto_risposta.replace('\\"', '"')

            try:
                response_json = json.loads(contenuto_risposta)
            except json.JSONDecodeError as e:
                print(f"Errore nel parsing del JSON: {e}")
                print("Contenuto grezzo:", contenuto_risposta)
                return None, unified_json
            
            unified_json["groups"].append(response_json)
            output_directory = os.path.dirname(file_path)
            os.makedirs(output_directory, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(unified_json, json_file, indent=4, ensure_ascii=False)
            print(f"JSON salvato con successo in {file_path}")

            return response_json, unified_json

        except Exception as e:
            print(f"Errore generico: {e}")
            return None, unified_json

    def annotations(self, element, file_name, output_json):
        """
        This method processes an XML file containing legal arguments, associates each argument with a semantic category, 
        and updates the XML structure accordingly. 
        It utilizes an AI model to classify arguments into predefined categories or mark them as uncategorized.

        Steps:
        1. **Group Aggregation**: Extracts groups from the XML element based on the `Group` attribute and aggregates the text for each group.
        2. **Classification**: Sends the aggregated text of each group to an AI model to classify into categories:
        - Historical, Textual, Structural, Prudential, Doctrinal, Ethical, or None.
        3. **Mapping**: Maps group IDs to their abbreviated category names (e.g., "HIS" for Historical Arguments).
        4. **XML Update**: Adds a `Category` attribute to XML elements based on the classification results.
        5. **File Saving**: Saves the updated XML file to the `demosthenes_dataset_annotated` directory.

        Inputs:
        - `element`: The root XML element containing legal arguments.
        - `file_name`: The name of the output XML file.
        - `output_json`: Path to save the intermediate and final JSON responses.

        Outputs:
        - An updated XML file with `Category` attributes added for each argument.
        - A JSON file summarizing the AI classifications.
        """

        diz_groups = {}
        unified_json = {"groups": []}  # JSON unificato

        for elem in element.iter():
            if 'Group' in elem.attrib:
                name = str(elem.attrib['Group']) 
                if elem.attrib['Group'] == 'None':
                    print(f'Skip element {elem.attrib} because is not assignet to any group')
                else:
                    if diz_groups.get(f'Group {name}') is None:
                        diz_groups[f'Group {name}'] = elem.text
                    else:
                        diz_groups[f'Group {name}'] = diz_groups[f'Group {name}'] + '\n' + elem.text
        
        for group, text in diz_groups.items():
            messaggi = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert assistant in analyzing legal texts. "
                        "Your task is to classify a supporting argument into one of the following subcategories, "
                        "or to indicate that none is appropriate: \n"
                        "- **Historical Arguments**: Interpretation based on the original intentions of the framers and ratifiers.\n"
                        "- **Textual Arguments**: Based solely on the literal meaning of the words.\n"
                        "- **Structural Arguments**: Analysis of the overall constitutional system and interactions among its parts.\n"
                        "- **Prudential Arguments**: Evaluation of practical pros and cons and social consequences.\n"
                        "- **Doctrinal Arguments**: Use of legal precedents to resolve new cases.\n"
                        "- **Ethical Arguments**: Based on moral principles and shared societal values.\n\n"
                        "If none of the categories is suitable, you may indicate that the text does not fit into any of them.\n\n"
                        "Please return the result in the following JSON format:\n\n"
                        "{\n"
                        f"   \"Group\": \"Group {group}\",\n"
                        "   \"Category\": \"[Name of Category or 'None']\",\n"
                        "   \"Reason\": \"[Explanation for the classification]\"\n"
                        "}\n"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"The following text is a supporting argument: {text}. "
                        f"Group: {group}"
                        "Analyze the content and identify the most relevant subcategory from the provided options, "
                        "or indicate if none of the subcategories is appropriate. "
                        "Please ensure the response is formatted strictly as JSON, following the example provided."
                    )
                }
            ]

            risposta = self.client.chat.completions.create(
                model= self.model_name,
                messages=messaggi,
                temperature=0.2
            )
            response_content = risposta.choices[0].message.content.strip()
            
            output_file, unified_json = self.parse_json_output(contenuto_risposta=response_content, unified_json=unified_json, file_path=output_json)
            

        category_map = {
            "Historical Arguments": "HIS",
            "Textual Arguments": "TXT",
            "Structural Arguments": "STRUCT",
            "Prudential Arguments": "PRUD",
            "Doctrinal Arguments": "DOCT",
            "Ethical Arguments": "ETH",
            "None": "None"
        }
        group_map = {
            group['Group']: category_map.get(group['Category'], "Unknown")
            for group in unified_json["groups"]
        }


        for elem in element.iter():
            if elem.tag != 'body' and 'ID' in elem.attrib:
                if 'Group' in elem.attrib:
                    group_id = 'Group '+ elem.attrib['Group']
           
                    if group_id in group_map:
                        elem.set('Category', str(group_map[group_id]))
        tree = ET.ElementTree(element)
        output_directory = 'demosthenes_dataset_annotated'
        os.makedirs(output_directory, exist_ok=True)
        tree.write(f'demosthenes_dataset_annotated/{file_name}', encoding="utf-8", xml_declaration=True)
        print(f"Updated XML file saved as 'demosthenes_dataset_annotated/{file_name}'.")

    


    def call_unifypar_struct(self, name, output_json):
        tree = ET.parse(f'demosthenes_dataset/{name}')
        root = tree.getroot()
        self.unified_struct(root, output_json, name)


    def call_annotations(self, name, output_json):
        tree = ET.parse(f'demosthenes_dataset_group/{name}')
        root = tree.getroot()
        self.annotations(root, name, output_json)
        



        
