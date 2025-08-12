import requests as rq
import xml.etree.ElementTree as ET

import time
import logging

from modules.pubmed_api import PubMedAPI 
from config.apis_config import API_SLEEP_TIME



class TermsNormalizer(PubMedAPI):
    def __init__(self, api_key=None, email=None):
        super().__init__(api_key, email)
     
    def normalize_by_entity_type(self, term, entity_type):
        """
        Route normalization to appropriate database based on entity type
        
        Args:
            term: Term to normalize
            entity_type: One of your entity types
            
        Returns:
            Normalized term info or None
        """
        # Map entity types to normalization methods
        entity_mapping = {
            'GENE_OR_GENE_PRODUCT': self.normalize_gene,
            'SIMPLE_CHEMICAL': self.normalize_chemical,
            'AMINO_ACID': self.normalize_chemical,  # PubChem covers amino acids
            'ORGANISM': self.normalize_taxonomy,
            'CANCER': self.normalize_mesh_term,
            'ANATOMICAL_SYSTEM': self.normalize_mesh_term,
            'CELL': self.normalize_mesh_term,
            'CELLULAR_COMPONENT': self.normalize_mesh_term,
            'DEVELOPING_ANATOMICAL_STRUCTURE': self.normalize_mesh_term,
            'IMMATERIAL_ANATOMICAL_ENTITY': self.normalize_mesh_term,
            'MULTI_TISSUE_STRUCTURE': self.normalize_mesh_term,
            'ORGAN': self.normalize_mesh_term,
            'ORGANISM_SUBDIVISION': self.normalize_mesh_term,
            'ORGANISM_SUBSTANCE': self.normalize_mesh_term,
            'PATHOLOGICAL_FORMATION': self.normalize_mesh_term,
            'TISSUE': self.normalize_mesh_term
        }
        
        normalizer = entity_mapping.get(entity_type)
        if normalizer:
            return normalizer(term)
        else:
            logging.warning(f"No normalizer found for entity type: {entity_type}")
            return None

    def normalize_mesh_term(self, term):
        """
        Normalize medical/anatomical terms using MeSH
        Covers: CANCER, ANATOMICAL_SYSTEM, CELL, CELLULAR_COMPONENT, 
                DEVELOPING_ANATOMICAL_STRUCTURE, IMMATERIAL_ANATOMICAL_ENTITY,
                MULTI_TISSUE_STRUCTURE, ORGAN, ORGANISM_SUBDIVISION, 
                ORGANISM_SUBSTANCE, PATHOLOGICAL_FORMATION, TISSUE
        """
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'mesh',
            'term': term,
            'retmax': 1,
            'retmode': 'json'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
        
        try:
            search_response = rq.get(search_url, params=search_params, headers=self.headers)
            if search_response.status_code != 200:
                return None
                
            search_data = search_response.json()
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return None
            
            # Fetch MeSH term details
            fetch_url = f"{self.base_url}efetch.fcgi"
            fetch_params = {
                'db': 'mesh',
                'id': id_list[0],
                'retmode': 'xml'
            }
            
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            if self.email:
                fetch_params['email'] = self.email
            
            fetch_response = rq.get(fetch_url, params=fetch_params, headers=self.headers)
            if fetch_response.status_code != 200:
                return None
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            # Parse MeSH term
            root = ET.fromstring(fetch_response.text)
            mesh_term = root.find('.//DescriptorName/String')
            mesh_ui = root.find('.//DescriptorUI')
            
            if mesh_term is not None:
                return {
                    'normalized_term': mesh_term.text,
                    'mesh_ui': mesh_ui.text if mesh_ui is not None else None,
                    'database': 'mesh'
                }
            
            return None
            
        except Exception as e:
            logging.error(f"MeSH normalization failed for '{term}': {e}")
            return None

    def normalize_gene(self, gene_term):
        """
        Normalize gene names using NCBI Gene database
        Covers: GENE_OR_GENE_PRODUCT
        """
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'gene',
            'term': f"{gene_term}[Gene Name] OR {gene_term}[Gene Symbol]",
            'retmax': 1,
            'retmode': 'json'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
        
        try:
            search_response = rq.get(search_url, params=search_params, headers=self.headers)
            if search_response.status_code != 200:
                return None
                
            search_data = search_response.json()
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return None
            
            # Fetch gene details
            fetch_url = f"{self.base_url}efetch.fcgi"
            fetch_params = {
                'db': 'gene',
                'id': id_list[0],
                'retmode': 'xml'
            }
            
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            if self.email:
                fetch_params['email'] = self.email
            
            fetch_response = rq.get(fetch_url, params=fetch_params, headers=self.headers)
            if fetch_response.status_code != 200:
                return None
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            # Parse gene info
            root = ET.fromstring(fetch_response.text)
            gene_symbol = root.find('.//Gene-ref_locus')
            gene_desc = root.find('.//Gene-ref_desc')
            gene_id = root.find('.//Gene-track_geneid')
            
            if gene_symbol is not None:
                return {
                    'normalized_term': gene_symbol.text,
                    'full_name': gene_desc.text if gene_desc is not None else None,
                    'gene_id': gene_id.text if gene_id is not None else None,
                    'database': 'gene'
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Gene normalization failed for '{gene_term}': {e}")
            return None

    def normalize_chemical(self, chemical_term):
        """
        Normalize chemicals/compounds using PubChem
        Covers: SIMPLE_CHEMICAL, AMINO_ACID
        """
        # Use PubChem Compound search
        search_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/JSON"
        
        try:
            response = rq.get(search_url.format(chemical_term.replace(' ', '%20')), headers=self.headers)
            
            # Rate limiting for PubChem (5 requests per second)
            time.sleep(0.2)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            compounds = data.get('PC_Compounds', [])
            
            if not compounds:
                return None
            
            compound = compounds[0]
            props = compound.get('props', [])
            
            # Extract compound name and CID
            iupac_name = None
            molecular_formula = None
            cid = compound.get('id', {}).get('id', {}).get('cid')
            
            for prop in props:
                urn = prop.get('urn', {})
                label = urn.get('label', '')
                
                if 'IUPAC Name' in label:
                    iupac_name = prop.get('value', {}).get('sval')
                elif 'Molecular Formula' in label:
                    molecular_formula = prop.get('value', {}).get('sval')
            
            return {
                'normalized_term': iupac_name or chemical_term,
                'cid': str(cid) if cid else None,
                'molecular_formula': molecular_formula,
                'database': 'pubchem'
            }
            
        except Exception as e:
            logging.error(f"Chemical normalization failed for '{chemical_term}': {e}")
            return None

    def normalize_taxonomy(self, organism_term):
        """
        Normalize organism names using NCBI Taxonomy
        Covers: ORGANISM
        """
        search_url = f"{self.base_url}esearch.fcgi"
        search_params = {
            'db': 'taxonomy',
            'term': organism_term,
            'retmax': 1,
            'retmode': 'json'
        }
        
        if self.api_key:
            search_params['api_key'] = self.api_key
        if self.email:
            search_params['email'] = self.email
        
        try:
            search_response = rq.get(search_url, params=search_params, headers=self.headers)
            if search_response.status_code != 200:
                return None
                
            search_data = search_response.json()
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return None
            
            # Fetch taxonomy details
            fetch_url = f"{self.base_url}efetch.fcgi"
            fetch_params = {
                'db': 'taxonomy',
                'id': id_list[0],
                'retmode': 'xml'
            }
            
            if self.api_key:
                fetch_params['api_key'] = self.api_key
            if self.email:
                fetch_params['email'] = self.email
            
            fetch_response = rq.get(fetch_url, params=fetch_params, headers=self.headers)
            if fetch_response.status_code != 200:
                return None
            
            if self.api_key:
                time.sleep(API_SLEEP_TIME["with_key"])
            else:
                time.sleep(API_SLEEP_TIME["without_key"])
            
            # Parse taxonomy info
            root = ET.fromstring(fetch_response.text)
            scientific_name = root.find('.//ScientificName')
            tax_id = root.find('.//TaxId')
            rank = root.find('.//Rank')
            
            if scientific_name is not None:
                return {
                    'normalized_term': scientific_name.text,
                    'tax_id': tax_id.text if tax_id is not None else None,
                    'rank': rank.text if rank is not None else None,
                    'database': 'taxonomy'
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Taxonomy normalization failed for '{organism_term}': {e}")
            return None


normalizer = TermsNormalizer(api_key="your_key", email="your_email")


result = normalizer.normalize_by_entity_type("BRCA1", "GENE_OR_GENE_PRODUCT")
print(result)
result = normalizer.normalize_by_entity_type("aspirin", "SIMPLE_CHEMICAL") 
print(result)
result = normalizer.normalize_by_entity_type("lung cancer", "CANCER")
print(result)
result = normalizer.normalize_by_entity_type("Escherichia coli", "ORGANISM")
print(result)


gene = normalizer.normalize_gene("p53")
print(result)
chemical = normalizer.normalize_chemical("acetaminophen")
print(result)
mesh_term = normalizer.normalize_mesh_term("myocardial infarction")
print(result)
organism = normalizer.normalize_taxonomy("mouse")
print(result)