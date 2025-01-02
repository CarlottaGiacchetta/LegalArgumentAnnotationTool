# Legal Argument Annotation Tool

## Overview

This repository provides a Python-based tool for processing and annotating legal texts in XML format. The tool utilizes OpenAI's GPT model to group sentences based on semantic meaning and categorize them into predefined legal argumentation types. It supports creating structured JSON outputs and updating XML files with these annotations for further analysis.

## Key Features

1. **Semantic Grouping**: Groups sentences based on thematic or semantic connections, ensuring coherence in legal arguments.
2. **Argument Categorization**: Assigns sentences to categories such as Historical, Textual, Doctrinal, Ethical, etc., based on their argumentative type.
3. **File Output**: Saves results in both annotated XML and structured JSON formats for integration with other tools or analysis pipelines.
4. **Automation**: Automates directory management, API interactions, and file handling to streamline the annotation workflow.

## Motivations

This tool is inspired by and extends the methodologies discussed in the paper *Detecting Arguments in CJEU Decisions on Fiscal State Aid*. The paper emphasizes the critical role of argument mining (AM) in the legal domain, where arguments must be systematically identified and categorized. It identifies challenges like:

1. The need for annotated corpora in underexplored legal domains.
2. The complexity of operationalizing legal argumentation theory for automated systems.
3. The importance of hierarchical annotation (e.g., identifying premises, conclusions, and schemes).

Building on these insights, this tool applies advanced AI models to address these challenges, enabling efficient annotation and classification of legal texts.

Additionally, this pipeline aligns with the theories presented in Philip Bobbitt's *Methods of Constitutional Argument*. Bobbitt's framework identifies six modalities of constitutional reasoning, which form the foundation for categorizing legal arguments in this tool.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/legal-annotation-tool.git
   cd legal-annotation-tool
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Initializing the Class

```python
from openai import OpenAI
from add_annotations import AddAnnotations

annotations = AddAnnotations(model_name='gpt-4o-mini', max_tokens=2000, openai_api_key='your-api-key')
```

### 2. Semantic Grouping

Groups sentences from an XML file based on their thematic connection.

```python
annotations.call_unifypar_struct(name='input_file.xml', output_json='output.json')
```

### 3. Argument Categorization

Classifies grouped arguments into predefined categories and updates the XML structure.

```python
annotations.call_annotations(name='grouped_file.xml', output_json='categorized_output.json')
```

### Output

- Updated XML files with annotations.
- Structured JSON outputs summarizing the categorization.

## Methodology

### Semantic Grouping

- **Objective**: Group sentences sharing a common theme.
- **Implementation**:
  - Extracts sentences and their metadata from the XML structure.
  - Sends sentences to OpenAI's GPT model for semantic grouping.
  - Integrates grouped information into the XML structure.

### Argument Categorization

- **Objective**: Assign legal categories to grouped sentences.

- **Categories**:

  - **Historical Arguments**: Based on framers' and ratifiers' intentions.
  - **Textual Arguments**: Focused on literal meanings.
  - **Structural Arguments**: Examining systemic constitutional interactions.
  - **Prudential Arguments**: Evaluating practical outcomes.
  - **Doctrinal Arguments**: Grounded in legal precedents.
  - **Ethical Arguments**: Based on societal values and morals.

- **Implementation**:
  - Aggregates sentences by group.
  - Uses GPT to assign categories based on the above types.
  - Updates the XML file with `Category` attributes.


## References

- [Detecting Arguments in CJEU Decisions on Fiscal State Aid](https://aclanthology.org/2022.argmining-1.14/)
- [Methods of Constitutional Argument by Philip Bobbitt](https://law.utexas.edu/faculty/publications/1989-Methods-of-Constitutional-Argument/)



