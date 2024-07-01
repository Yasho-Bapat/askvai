from ask_viridium_ai import AskViridium
import pandas as pd
from tracking import ExperimentLogger
import time

# Loading dataframes
global_node = pd.read_csv('../data/global_node.csv')
manufacturer = pd.read_csv('../data/manufacturer.csv')
material_to_document_mapping = pd.read_csv('../data/material_to_document_mapping.csv')

# Extracting relevant dfs with pfas_status as PENDING
pending_materials = global_node[global_node['pfas_status'] == 'PENDING']
material_ids = material_to_document_mapping[material_to_document_mapping['material_id'].isin(pending_materials['id'])][
    'material_id']
material_names = pending_materials.loc[pending_materials['id'].isin(material_ids), 'name']

manufacturer_ids = pending_materials.loc[pending_materials['id'].isin(material_ids), 'manufacturer_id']
manufacturer_names = manufacturer.loc[manufacturer['id'].isin(manufacturer_ids), 'name']

# Create our own dataframe
df = pd.DataFrame({"material_name": material_names, "manufacturer_ids": manufacturer_ids})

# Limit to 10 materials
df = df.sample(n=10, random_state=1).reset_index(drop=True)

askai = AskViridium()

first_half = df.iloc[:len(df) // 2]  # First half
second_half = df.iloc[len(df) // 2:]  # Second half

rn = time.perf_counter()

# Manufacturer info NOT being passed in this run
for i, mn in enumerate(first_half["material_name"]):
    logger = ExperimentLogger()
    final_results = {}

    manu_id = df.loc[df["material_name"] == mn, "manufacturer_ids"].values[0]
    manu_name = manufacturer.loc[manufacturer['id'] == manu_id, "name"].values[0]
    material_id = global_node.loc[global_node['name'] == mn, "id"].values[0]
    service_pfas_status = global_node.loc[global_node['name'] == mn, "pfas_status"].values[0]

    res = askai.query(material_name=mn)

    if res["decision"] == "PFAS (No)":
        decision = "NO"
    elif res["decision"] == "PFAS (Yes)":
        decision = "YES"
    else:
        decision = res["decision"]

    print(f"{decision}\n")
    final_results["material_id"] = material_id
    final_results["manufacturer_id"] = manu_id
    final_results["manufacturer_name"] = manu_name
    final_results["modified_service_pfas_status"] = decision
    final_results["material_name"] = mn
    final_results["current_service_pfas_status"] = service_pfas_status

    logger.log(final_results)
    logger.save("first_half_experiment_logs.csv")

# Manufacturer info being passed in this run
for i, mn in enumerate(second_half["material_name"]):
    secondlogger = ExperimentLogger()
    final_results = {}
    print(mn)

    manu_id = df.loc[df["material_name"] == mn, "manufacturer_ids"].values[0]
    manu_name = manufacturer.loc[manufacturer['id'] == manu_id, "name"].values[0]
    material_id = global_node.loc[global_node['name'] == mn, "id"].values[0]
    print(manu_name)
    service_pfas_status = global_node.loc[global_node['name'] == mn, "pfas_status"].values[0]

    res = askai.query(material_name=mn, manufacturer_name=manu_name)

    if res["decision"] == "PFAS (No)":
        decision = "NO"
    elif res["decision"] == "PFAS (Yes)":
        decision = "YES"
    else:
        decision = res["decision"]

    print(f"{decision}\n")
    final_results["material_id"] = material_id
    final_results["manufacturer_id"] = manu_id
    final_results["manufacturer_name"] = manu_name
    final_results["modified_service_pfas_status"] = decision
    final_results["material_name"] = mn
    final_results["current_service_pfas_status"] = service_pfas_status

    secondlogger.log(final_results)
    secondlogger.save("second_half_experiment_logs.csv")

print(f"took {time.perf_counter() - rn} seconds")
