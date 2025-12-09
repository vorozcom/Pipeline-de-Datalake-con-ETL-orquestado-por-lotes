import pandas as pd
import boto3
import io

print("INICIANDO SCRIPT ETL (PYTHON SHELL)")

### --- CONFIGURACIÓN --- ###
# Reemplaza esto con el nombre de tu bucket
# (Asegúrate de que no haya espacios al final de esta línea)
S3_BUCKET_NAME = "bucket-proyecto-servidores"

# Carpetas
RAW_FOLDER = "raw/"
PROCESSED_FOLDER = "processed/"

# Los archivos CSV reales
FILE_CUSTOMER = "customer_data.csv"
FILE_SALES = "sales_data.csv"
FILE_STORE = "store_data.csv"
FILE_PRODUCTS = "product_data.csv"

# Nombre del archivo final en Parquet
OUTPUT_FILE = "file_processed.parquet"
### ----------------------- ###


# 1. CONSTRUIR RUTAS DE S3
s3_client = boto3.client('s3')

path_customer = f"s3://{S3_BUCKET_NAME}/{RAW_FOLDER}{FILE_CUSTOMER}"
path_sales = f"s3://{S3_BUCKET_NAME}/{RAW_FOLDER}{FILE_SALES}"
path_store = f"s3://{S3_BUCKET_NAME}/{RAW_FOLDER}{FILE_STORE}"
path_products = f"s3://{S3_BUCKET_NAME}/{RAW_FOLDER}{FILE_PRODUCTS}"
path_output = f"s3://{S3_BUCKET_NAME}/{PROCESSED_FOLDER}{OUTPUT_FILE}"

print(f"Leyendo desde: {path_customer}, {path_sales}, {path_store}, {path_products}")

try:
    # 2. LEER DATOS CON PANDAS
    df_customer = pd.read_csv(path_customer)
    df_sales = pd.read_csv(path_sales)
    df_store = pd.read_csv(path_store)
    df_products = pd.read_csv(path_products)

    # 3. TRANSFORMACIÓN (LA "T" DE ETL)
    
    # --- Limpieza Básica ---
    # Convertir fecha a formato datetime
    if 'date' in df_sales.columns:
        df_sales['date'] = pd.to_datetime(df_sales['date'])
    
    # --- Uniones (Joins) ---
    # 1. Ventas + Productos
    df_merged_sales_products_inner = pd.merge(df_sales, df_products, on='product_id', how='inner')
    # 2. + Tiendas
    df_merged_sales_products_store_inner = pd.merge(df_merged_sales_products_inner, df_store, on='store_id', how='inner')
    # 3. + Clientes (Dataframe Consolidado)
    df_consolidated_inner = pd.merge(df_merged_sales_products_store_inner, df_customer, on='customer_id', how='inner')

    print("Uniones completadas exitosamente.")

    # --- LIMPIEZA ESPECÍFICA (La que solicitaste) ---
    # Aplicamos el reemplazo sobre el dataframe consolidado
    print("Limpiando valores '???' en category y gender...")

    # Verificar si 'category' existe y reemplazar
    if 'category' in df_consolidated_inner.columns:
        df_consolidated_inner.loc[:, 'category'] = df_consolidated_inner['category'].replace('???', 'Sets')
    
    # Verificar si 'gender' existe y reemplazar
    if 'gender' in df_consolidated_inner.columns:
        df_consolidated_inner.loc[:, 'gender'] = df_consolidated_inner['gender'].replace('???', 'Other')
    # -----------------------------------------------

    # --- Filtrado Final ---
    # Eliminar filas donde el email sea nulo
    df_final = df_consolidated_inner.dropna(subset=['email'])

    # 4. ESCRIBIR DATOS A PARQUET
    print(f"Escribiendo Parquet en: {path_output}")
    df_final.to_parquet(path_output, index=False, engine='pyarrow')

    print("SCRIPT ETL FINALIZADO CON ÉXITO")

except Exception as e:
    print(f"ERROR: El script falló.")
    print(e)
    raise e
