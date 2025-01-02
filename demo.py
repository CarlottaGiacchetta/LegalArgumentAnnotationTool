from annotator import AddAnnotations


key = 'put here your API key'
model_GPT = 'gpt-4o'
filename = "A2008_Commission of the European Communities v Salzgitter AG.xml"

annotator = AddAnnotations(model_name=model_GPT, openai_api_key=key)
annotator.call_unifypar_struct(name=filename, output_json=f'output_group/{filename}.json')
annotator.call_annotations(name=filename, output_json=f'output_annotations/{filename}.json')