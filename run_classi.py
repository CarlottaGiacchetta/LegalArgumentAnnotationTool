from classi import AddAnnotations

key = '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'
model_GPT = 'gpt-4o'
filename = "A2008_Commission of the European Communities v Salzgitter AG.xml"

annotator = AddAnnotations(model_name=model_GPT, openai_api_key=key)
annotator.call_annotations(name=filename, mult_run=False)
