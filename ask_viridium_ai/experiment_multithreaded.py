from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from ask_viridium_ai import AskViridium
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
# df = df.sample(n=10, random_state=1).reset_index(drop=True)

askai = AskViridium()


def process_material(row, include_manufacturer):
    logger = ExperimentLogger()
    final_results = {}

    mn = row['material_name']
    manu_id = row['manufacturer_ids']
    manu_name = manufacturer.loc[manufacturer['id'] == manu_id, "name"].values[0]
    material_id = global_node.loc[global_node['name'] == mn, "id"].values[0]
    service_pfas_status = global_node.loc[global_node['name'] == mn, "pfas_status"].values[0]

    if include_manufacturer:
        res = askai.query(material_name=mn, manufacturer_name=manu_name)
    else:
        res = askai.query(material_name=mn)

    decision = res.get("decision", "UNKNOWN")
    if decision == "PFAS (No)":
        decision = "NO"
    elif decision == "PFAS (Yes)":
        decision = "YES"

    final_results["material_id"] = material_id
    final_results["manufacturer_id"] = manu_id
    final_results["manufacturer_name"] = manu_name
    final_results["modified_service_pfas_status"] = decision
    final_results["material_name"] = mn
    final_results["current_service_pfas_status"] = service_pfas_status

    logger.log(final_results)

    if include_manufacturer:
        logger.save("second_half_experiment_logs.csv")
    else:
        logger.save("first_half_experiment_logs.csv")

    return final_results


rn = time.perf_counter()

# First half without manufacturer info
first_half = df.iloc[:len(df) // 2]
first_half = first_half.iloc[72:]

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_material, row, False) for _, row in first_half.iterrows()]
    for future in as_completed(futures):
        print(future.result())

# Second half with manufacturer info
second_half = df.iloc[len(df) // 2:]

with ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_material, row, True) for _, row in second_half.iterrows()]
    for future in as_completed(futures):
        print(future.result())

print(f"took {time.perf_counter() - rn} seconds")
