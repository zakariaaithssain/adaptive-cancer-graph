_“This product uses publicly available data from the U.S. National Library of Medicine (NLM), National Institutes of Health, Department of Health and Human Services; NLM is not responsible for the product and does not endorse or recommend this or any other product.”_

**Note: This pipeline uses en_ner_bionlp13cg_md Scispacy NER model for NER and Spacy Matchers and Dependency Matchers for RE. Data is not being revised or validated by any professionals from the medical field.** 

## Core Features

### Complete ETL Pipeline
- **Extract**: Fetch articles from PubMed API 
- **Annotate**: Named Entity Recognition (NER) and Relation Extraction (RE) 
- **Clean**: Data preparation and validation for graph database
- **Load**: Loading into Neo4j Aura with batch processing

### CLI
- **Configurable Parameters**:
  - `--max-results`: Set the number of articles to extract per API call  (default: 1000, max = 10000) 
  (This is not the number of articles to get per query, which is set to the hardcoded API limit of 10K articles)
  - `--batch-size`: Control Neo4j loading batch size for optimal performance (default: 1000)
  - `--full-text`: Extract full-text articles instead of abstracts only
  - `--help`: help documentation with usage examples

##  Usage Examples

### Basic Usage
```bash
# Run full pipeline with defaults
python main.py

# Extract articles with full text, 5000 articles per API call, and load to Neo4j Aura with 5000 article per batch
python main.py --max-results 5000 --full-text  --batch-size 5000

# Run individual stages
python main.py extract
python main.py annotate
python main.py clean
python main.py load
```


# Memory-constrained environment
```bash
python main.py --max-results 1000 --batch-size 200
```

## Architecture

### Pipeline Stages
1. **Extract**: Connects to PubMed API and retrieves medical literature
2. **Annotate**: Processes text for medical entities and relationships , and normalize entities via UMLS API. (generates two CSV files)
4. **Clean**: Validates and prepares data for graph database storage (generates two cleaned CSV files)
5. **Load**: Efficiently loads structured data into Neo4j Aura

### Data Processing
- **MongoDB Integration**: Intermediate storage for extracted articles
- **Entity Recognition**: Identifies medical entities (diseases, treatments, etc.)
- **Relationship Extraction**: Discovers connections between medical concepts
- **Graph Database**: Final storage in Neo4j Aura for complex queries and analysis

##  System Requirements

### Dependencies
- Latest versions of Python I guess
- PubMed API account email and API key (optional but increases the number of tolerated API calls, and needs sleep time configuration): https://account.ncbi.nlm.nih.gov
- UMLS API API key (obligatory):  https://uts.nlm.nih.gov/
- MongoDB Atlas Account:  https://www.mongodb.com/cloud/atlas/register
- Neo4j Aura access (where the graph will be stored): https://console-preview.neo4j.io/account/profile
- Required Python packages (see requirements.txt)
- Inside the config folder, create secrets.py file:

```

PM_API_KEY_EMAIL = {"api_key" : "YOUR PUBMED API KEY HERE", 
              
              "email" : "YOUR EMAIL HERE", 
              }
              
#UMLS API, the key is obligatory.
UMLS_API_KEY = "YOUR UMLS API KEY HERE"

#Mongo Atlas Connection
MONGO_CONNECTION_STR = "YOUR CONNECTION STRING HERE"

#Neo4j Aura Connection
NEO4J_URI = "YOUR AURA URI HERE"
NEO4J_AUTH = ("USER", "PASSWORD")

```

##  Getting Started


### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Get your PubMed API key (optional but recommended) and UMLS API key
4. Configure your MongoDB Atlas, Neo4j Aura
5. Inside config/ create secrets.py described above


### Quick Start
```bash
# Run the complete ETL pipeline with defaults
python main.py

# Get help and see all options
python main.py --help
```

##  Use Cases

### Research & Development
- Build medical knowledge graphs for research
- Extract relationships between medical concepts
- Create datasets for machine learning models

### Healthcare Analytics
- Analyze medical literature trends
- Discover new research connections
- Support clinical decision making



##  Contributing

We welcome contributions to improve the Medical Graph ETL Pipeline! Here's how you can help:

- **Report Issues**: Found a bug? Report it via GitHub issues
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests with enhancements
- **Documentation**: Help improve our documentation and examples


