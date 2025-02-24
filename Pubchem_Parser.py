import requests
import csv
from time import sleep
from tqdm import tqdm

# Headers for HTTP request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'connection': 'keep-alive',
    'referer': 'https://pubchem.ncbi.nlm.nih.gov/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
}

# Read compound list from text file
with open("compoundlists.txt", "r") as file:
    compounds = [line.strip() for line in file.readlines() if line.strip()]

# Check if the compound list is not empty
if not compounds:
    print("No valid compounds found in 'compoundlists.txt'.")
    exit()

# Define output CSV file
csv_filename = "all_compounds_data.csv"

# Open CSV file for writing
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)

    # Write header row
    writer.writerow([
        "Compound", "CID", "IUPAC Name (Preferred)", "Molecular Formula", "Molecular Weight",
        "InChI", "InChIKey", "SMILES Absolute", "SMILES Canonical", "SMILES Isomeric"
    ])

    # Loop through each compound and make individual requests
    for compound in tqdm(compounds):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound}/JSON"

        # Print the URL to debug
        #print(f"Request URL: {url}")

        # Make the API request
        response = requests.get(url, headers=headers, timeout=10)
        sleep(3)

        # Check if request was successful
        if response.status_code == 200:
            data = response.json()

            # Process the compound data
            for compound_data in data.get("PC_Compounds", []):
                cid = compound_data["id"]["id"]["cid"]
                iupac_name = molecular_formula = molecular_weight = inchi = inchikey = ""
                smiles_absolute = smiles_canonical = smiles_isomeric = ""

                # Extract properties
                for prop in compound_data.get("props", []):
                    label = prop["urn"].get("label", "")
                    name = prop["urn"].get("name", "")
                    value = prop["value"].get("sval", "")

                    if label == "IUPAC Name" and name == "Preferred":
                        iupac_name = value
                    elif label == "Molecular Formula":
                        molecular_formula = value
                    elif label == "Molecular Weight":
                        molecular_weight = value
                    elif label == "InChI" and name == "Standard":
                        inchi = value
                    elif label == "InChIKey" and name == "Standard":
                        inchikey = value
                    elif label == "SMILES" and name == "Absolute":
                        smiles_absolute = value
                    elif label == "SMILES" and name == "Canonical":
                        smiles_canonical = value
                    elif label == "SMILES" and name == "Isomeric":
                        smiles_isomeric = value

                # Write compound data to CSV
                writer.writerow([
                    compound, cid, iupac_name, molecular_formula, molecular_weight,
                    inchi, inchikey, smiles_absolute, smiles_canonical, smiles_isomeric
                ])

        else:
                writer.writerow([
                    compound, "N/A", "N/A", "N/A", "N/A",
                    "N/A", "N/A", "N/A", "N/A", "N/A"
                ])

print(f"All compounds have been saved in '{csv_filename}'.")