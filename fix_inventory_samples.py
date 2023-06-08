import pandas as pd

# Fixes invetory after sample orders were removed from the inventory

# Global Variables
data_dir = r"C:\Users\marci\OneDrive\silkresource\data06"
orders_file = 'sample-orders-2023-06-08-13-07-17.xlsx'
inventory_file = 'inventory-8-6-2023-1686255158161.csv'
out_inventory_file = 'output.csv'

def process_orders():
    # Load the CSV inventory file
    inventory_df = pd.read_csv(f'{data_dir}/{inventory_file}')

    # Remove single quotes in 'Stock' column, replace NaN with 0, and convert to integer
    inventory_df['Stock'] = inventory_df['Stock'].str.replace("'", "").fillna(0).astype(int)

    # Load the Excel orders file
    orders_df = pd.read_excel(f'{data_dir}/{orders_file}')

    # Initialize a list for updated inventory
    updated_inventory = []

    # Create a dictionary to keep track of processed SKUs
    processed_skus = {}

    # For each row in orders dataframe
    for idx, order in orders_df.iterrows():
        # Find matching SKU in inventory
        inventory_idx = inventory_df[inventory_df['SKU'] == order['SKU']].index

        # If matching SKU is found
        if not inventory_idx.empty:
            # If SKU has not been processed before
            if order['SKU'] not in processed_skus:
                # Save 'Stock' to 'Old Stock' and initialize 'Order Qty'
                inventory_df.loc[inventory_idx, 'Old Stock'] = inventory_df.loc[inventory_idx, 'Stock']
                inventory_df.loc[inventory_idx, 'Order Qty'] = str(order['Quantity'])
                processed_skus[order['SKU']] = True
            else:
                # Append order quantity to 'Order Qty'
                inventory_df.loc[inventory_idx, 'Order Qty'] += ';' + str(order['Quantity'])

            # Update the inventory's stock
            inventory_df.loc[inventory_idx, 'Stock'] += order['Quantity']

            # Check if SKU appears more than once in the orders
            if orders_df[orders_df['SKU'] == order['SKU']].shape[0] > 1:
                print(f"SKU {order['SKU']} found more than once in Order Number {order['Order Number']}.")

            # Add the updated inventory row to the list
            updated_inventory.append(inventory_df.loc[inventory_idx])

    # Combine all the dataframes in the list into a single dataframe
    updated_inventory_df = pd.concat(updated_inventory)

    # Write the updated inventory dataframe to output CSV file
    updated_inventory_df.to_csv(f'{data_dir}/{out_inventory_file}', index=False)

# Call the function
process_orders()