# from django.http import JsonResponse
# from django.shortcuts import render

# # Try importing REST framework, or set a flag if it's not available
# try:
#     from rest_framework.views import APIView
#     from rest_framework.response import Response
#     from rest_framework import status
#     from rest_framework.parsers import JSONParser
#     REST_FRAMEWORK_AVAILABLE = True
# except ImportError:
#     REST_FRAMEWORK_AVAILABLE = False
#     # Define fallback classes
#     class APIView:
#         pass
#     Response = JsonResponse
#     class status:
#         HTTP_200_OK = 200
#         HTTP_400_BAD_REQUEST = 400
#         HTTP_500_INTERNAL_SERVER_ERROR = 500

# # Try importing data science packages
# try:
#     import pandas as pd
#     import seaborn as sns 
#     import numpy as np
#     import matplotlib.pyplot as plt
#     import pyarrow.parquet as pq
#     import io
#     import os
#     import re
#     import base64
#     DATA_SCIENCE_PACKAGES_AVAILABLE = True
# except ImportError:
#     DATA_SCIENCE_PACKAGES_AVAILABLE = False

# # Try importing Azure and OpenAI packages
# try:
#     from azure.storage.blob import ContainerClient
#     from openai import OpenAI
#     AZURE_OPENAI_AVAILABLE = True
# except ImportError:
#     AZURE_OPENAI_AVAILABLE = False

# # Only set up these components if dependencies are available
# if DATA_SCIENCE_PACKAGES_AVAILABLE:
#     # Set the Matplotlib backend to Agg (non-interactive)
#     plt.switch_backend('Agg')

# # Initialize variables
# container_client = None
# chatbot = None

# if AZURE_OPENAI_AVAILABLE:
#     try:
#         # SAS URL for the container
#         sas_url = "https://saviaitdtldatalake.blob.core.windows.net/dblayer?<new-container-level-sas-token>"
#         container_client = ContainerClient.from_container_url(sas_url)
#     except Exception as e:
#         print(f"Error connecting to Azure: {str(e)}")

# # Function to load data from a Parquet file in Azure Blob Storage
# def load_parquet_data(blob_name):
#     blob_client = container_client.get_blob_client(blob_name)
#     blob_data = blob_client.download_blob()
#     parquet_data = blob_data.readall()
#     table = pq.read_table(io.BytesIO(parquet_data))
#     df = table.to_pandas()
#     return df

# class DataAnalysisChatbot:
#     def __init__(self, api_key=None):
#         self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
#         if not self.api_key:
#             raise ValueError("OpenAI API key is required")
        
#         self.client = OpenAI(api_key=self.api_key)
#         self.dataframes = {}
#         self.active_df = None
#         self.active_table = None
#         self.history = []
    
#     def load_data_from_azure(self, table_names):
#         for table in table_names:
#             folder_name = f"Copy-25042025/{table}"
            
#             dataframes = []
#             for blob in container_client.list_blobs(name_starts_with=folder_name):
#                 if blob.name.endswith(".parquet"):
#                     df = load_parquet_data(blob.name)
#                     dataframes.append(df)
            
#             if dataframes:
#                 combined_df = pd.concat(dataframes, ignore_index=True)
#                 self.dataframes[table] = combined_df
                
#                 if not self.active_df:
#                     self.active_df = combined_df
#                     self.active_table = table
    
#     def generate_code_from_query(self, query):
#         df_info = f"DataFrame Info for '{self.active_table}':\n"
#         df_info += f"- Shape: {self.active_df.shape}\n"
#         df_info += f"- Columns: {list(self.active_df.columns)}\n"
        
#         column_stats = {}
#         for col in self.active_df.columns:
#             try:
#                 if self.active_df[col].dtype in ['int64', 'float64']:
#                     column_stats[col] = {
#                         'dtype': str(self.active_df[col].dtype),
#                         'unique_values': self.active_df[col].unique()[:5].tolist(),
#                         'min': self.active_df[col].min(),
#                         'max': self.active_df[col].max(),
#                         'mean': self.active_df[col].mean() if self.active_df[col].dtype == 'float64' else None
#                     }
#                 else:
#                     column_stats[col] = {
#                         'dtype': str(self.active_df[col].dtype),
#                         'unique_values': self.active_df[col].unique()[:5].tolist(),
#                         'count': len(self.active_df[col].unique())
#                     }
#             except:
#                 column_stats[col] = {
#                     'dtype': str(self.active_df[col].dtype),
#                     'note': 'Could not calculate statistics'
#                 }
        
#         df_info += f"\nSample data (5 rows):\n{self.active_df.head(5).to_string()}\n\n"
#         df_info += f"Column statistics: {column_stats}\n"
        
#         prompt = f"""
#         We have data already loaded into a DataFrame called `df` with information below:
#         {df_info}
        
#         Generate Python code to answer this query: "{query}"
        
#         Rules:
#         - The data is already loaded in the variable `df`
#         - DO NOT include any file operations (read_csv, to_csv, etc.)
#         - If creating visualizations, use matplotlib or seaborn
#         - Return only the code without explanations
#         - Enclose the code in triple backticks (```)
#         - For any chart or visualization, include plt.tight_layout() and make sure labels and titles are clear
        
#         Generate concise, efficient code that directly addresses the query.
#         """
        
#         response = self.client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a data science code generator that creates Python code for data analysis. You only return valid, executable Python code without explanations."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2,
#             max_tokens=1000
#         )
        
#         content = response.choices[0].message.content
#         pattern = r'```(?:python)?(.*?)```'
#         matches = re.findall(pattern, content, re.DOTALL)
        
#         if not matches:
#             return content.strip()
#         return matches[0].strip()
    
#     def execute_code(self, code):
#         img_buf = io.BytesIO()
        
#         try:
#             local_namespace = {
#                 'df': self.active_df,
#                 'pd': pd,
#                 'np': np,
#                 'plt': plt
#             }
            
#             exec(code, {}, local_namespace)
            
#             if 'plt' in code:
#                 plt.tight_layout()
#                 plt.savefig(img_buf, format='png', dpi=100)
#                 img_buf.seek(0)
                
#                 img_data = base64.b64encode(img_buf.getvalue()).decode()
#                 plt.close('all')
                
#                 return {
#                     'type': 'plot',
#                     'data': img_data,
#                     'message': 'Generated a visualization'
#                 }
            
#             if 'result' in local_namespace:
#                 result = local_namespace['result']
#                 if isinstance(result, pd.DataFrame):
#                     return {
#                         'type': 'dataframe',
#                         'data': result.head(20).to_dict(orient='records'),
#                         'message': f'Dataframe result with {len(result)} rows (showing first 20)'
#                     }
#                 else:
#                     return {
#                         'type': 'result',
#                         'data': str(result),
#                         'message': 'Executed code and got result'
#                     }
            
#             last_var = None
#             for var_name, var_value in local_namespace.items():
#                 if var_name not in ['df', 'pd', 'np', 'plt'] and not var_name.startswith('_'):
#                     last_var = (var_name, var_value)
            
#             if last_var:
#                 var_name, var_value = last_var
#                 if isinstance(var_value, pd.DataFrame):
#                     return {
#                         'type': 'dataframe',
#                         'data': var_value.head(20).to_dict(orient='records'),
#                         'message': f'Created dataframe {var_name} with {len(var_value)} rows (showing first 20)'
#                     }
#                 else:
#                     return {
#                         'type': 'result',
#                         'data': str(var_value),
#                         'message': f'Variable {var_name} = {str(var_value)}'
#                     }
            
#             return {
#                 'type': 'message',
#                 'data': 'Code executed successfully, but no results were returned',
#                 'message': 'Code executed without output'
#             }
            
#         except Exception as e:
#             return {
#                 'type': 'error',
#                 'data': str(e),
#                 'message': f'Error executing code: {str(e)}'
#             }
    
#     def get_natural_language_response(self, query, code_result):
#         result_description = ""
        
#         if code_result['type'] == 'plot':
#             result_description = "I've generated a visualization based on your query."
#         elif code_result['type'] == 'dataframe':
#             result_description = f"I've analyzed your data and created a result with {code_result['message']}."
#         elif code_result['type'] == 'result':
#             result_description = f"Based on your query, I found: {code_result['data']}"
#         elif code_result['type'] == 'error':
#             result_description = f"I encountered an error: {code_result['data']}"
        
#         data_context = f"Working with table '{self.active_table}' containing {len(self.active_df)} records with {len(self.active_df.columns)} columns."
        
#         prompt = f"""
#         User Query: {query}
        
#         Data Context: {data_context}
        
#         Result: {result_description}
        
#         Please provide a natural language explanation of these results in a helpful, concise manner.
#         Explain what the data shows, any trends, insights or notable findings.
#         Keep your explanation brief but informative.
#         """
        
#         response = self.client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are a data analysis assistant that explains analysis results in clear, natural language."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,
#             max_tokens=500
#         )
        
#         return response.choices[0].message.content
    
#     def chat(self, query, table_name=None):
#         # Handle table switching if provided
#         if table_name and table_name in self.dataframes:
#             self.active_df = self.dataframes[table_name]
#             self.active_table = table_name
        
#         if not self.active_df is not None:
#             return {"error": "No data loaded. Please load data first."}
        
#         # Add query to history
#         self.history.append({"role": "user", "query": query})
        
#         # Generate and execute code
#         generated_code = self.generate_code_from_query(query)
#         code_result = self.execute_code(generated_code)
        
#         # Generate natural language explanation
#         explanation = self.get_natural_language_response(query, code_result)
        
#         # Format the complete response
#         response = {
#             "query": query,
#             "explanation": explanation,
#             "code": generated_code,
#             "result": code_result,
#             "active_table": self.active_table
#         }
        
#         # Add to history
#         self.history.append({"role": "assistant", "response": response})
        
#         return response


# # Initialize the chatbot and load data (do this on server startup)
# chatbot = None
# try:
#     api_key = os.environ.get("OPENAI_API_KEY") or "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"
#     if api_key:
#         chatbot = DataAnalysisChatbot(api_key)
#         # Load data from Azure Blob Storage
#         # table_names = ['customerdimtable']
#         table_names = [
#     'salesdataproduct',
#     'customerdetails',
#     'productdetailsmarcmard',
#     'salesaggregatesmonthwise',
#     'customerdetails4470',
#     'datedetails',
#     'productdetailsupdated',
#     'productdetailswithbillingdelivery',
#     'plantdetails',
#     'customerdetails_singletaxinfo',
#     'productdetails',
#     'customerdimtable',
#     'customerdetailsunique',
#     'productdetailsmara',
#     'salesorgdetails'
# ]

#         chatbot.load_data_from_azure(table_names)
# except Exception as e:
#     print(f"Error initializing chatbot: {str(e)}")


# class DataAnalysisAPIView(APIView):
#     """
#     API endpoint for data analysis queries.
#     """
#     def get(self, request, format=None):
#         # Check if all requirements are met
#         missing_dependencies = []
#         if not REST_FRAMEWORK_AVAILABLE:
#             missing_dependencies.append("Django REST Framework")
#         if not DATA_SCIENCE_PACKAGES_AVAILABLE:
#             missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
#         if not AZURE_OPENAI_AVAILABLE:
#             missing_dependencies.append("Azure and OpenAI Packages")
        
#         if missing_dependencies:
#             return Response(
#                 {
#                     "message": "This endpoint only accepts POST requests with a 'query' parameter",
#                     "warning": "Missing dependencies: " + ", ".join(missing_dependencies)
#                 },
#                 status=status.HTTP_200_OK
#             )
#         return Response(
#             {"message": "This endpoint only accepts POST requests with a 'query' parameter"},
#             status=status.HTTP_200_OK
#         )
        
#     def post(self, request, format=None):
#         # Check if all requirements are met
#         missing_dependencies = []
#         if not REST_FRAMEWORK_AVAILABLE:
#             missing_dependencies.append("Django REST Framework")
#         if not DATA_SCIENCE_PACKAGES_AVAILABLE:
#             missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
#         if not AZURE_OPENAI_AVAILABLE:
#             missing_dependencies.append("Azure and OpenAI Packages")
        
#         if missing_dependencies:
#             return Response(
#                 {"error": "Missing dependencies: " + ", ".join(missing_dependencies)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
            
#         if not chatbot or not chatbot.dataframes:
#             return Response(
#                 {"error": "Chatbot not initialized or no data loaded. Make sure OPENAI_API_KEY is set in environment variables."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
        
#         try:
#             data = JSONParser().parse(request)
#             query = data.get('query')
#             table_name = data.get('table_name')  # Optional parameter
            
#             if not query:
#                 return Response(
#                     {"error": "Query is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             response = chatbot.chat(query, table_name)
#             return Response(response)
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# def index(request):
#     return render(request, 'data_analysis_api/test.html') 





# from django.http import JsonResponse
# from django.shortcuts import render
 
# # Try importing REST framework, or set a flag if it's not available
# try:
#     from rest_framework.views import APIView
#     from rest_framework.response import Response
#     from rest_framework import status
#     from rest_framework.parsers import JSONParser
#     REST_FRAMEWORK_AVAILABLE = True
# except ImportError:
#     REST_FRAMEWORK_AVAILABLE = False
#     # Define fallback classes
#     class APIView:
#         pass
#     Response = JsonResponse
#     class status:
#         HTTP_200_OK = 200
#         HTTP_400_BAD_REQUEST = 400
#         HTTP_500_INTERNAL_SERVER_ERROR = 500
 
# # Try importing data science packages
# try:
#     import pandas as pd
#     import numpy as np
#     import matplotlib.pyplot as plt
#     import pyarrow.parquet as pq
#     import io
#     import os
#     import re
#     import base64
#     import seaborn as sns
#     import matplotlib
#     import matplotlib.dates as mdates
#     DATA_SCIENCE_PACKAGES_AVAILABLE = True
# except ImportError:
#     DATA_SCIENCE_PACKAGES_AVAILABLE = False
 
# # Try importing Azure and OpenAI packages
# try:
#     from azure.storage.blob import ContainerClient
#     from openai import OpenAI
#     AZURE_OPENAI_AVAILABLE = True
# except ImportError:
#     AZURE_OPENAI_AVAILABLE = False
 
# # Only set up these components if dependencies are available
# if DATA_SCIENCE_PACKAGES_AVAILABLE:
#     # Set the Matplotlib backend to Agg (non-interactive)
#     plt.switch_backend('Agg')
 
# # Initialize variables
# container_client = None
# chatbot = None
 
# if AZURE_OPENAI_AVAILABLE:
#     try:
#         # SAS URL for the container
#         sas_url = "https://saviaitdtldatalake.blob.core.windows.net/dblayer?<new-container-level-sas-token>"
#         container_client = ContainerClient.from_container_url(sas_url)
#     except Exception as e:
#         print(f"Error connecting to Azure: {str(e)}")
 
# # Function to load data from a Parquet file in Azure Blob Storage
# def load_parquet_data(blob_name):
#     blob_client = container_client.get_blob_client(blob_name)
#     blob_data = blob_client.download_blob()
#     parquet_data = blob_data.readall()
#     table = pq.read_table(io.BytesIO(parquet_data))
#     df = table.to_pandas()
#     return df
 
# class DataAnalysisChatbot:
#     def __init__(self, api_key=None):
#         self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
#         if not self.api_key:
#             raise ValueError("OpenAI API key is required")
       
#         self.client = OpenAI(api_key=self.api_key)
#         self.dataframes = {}
#         self.active_df = None
#         self.active_table = None
#         self.history = []
   
#     def load_data_from_azure(self, table_names):
#         for table in table_names:
#             folder_name = f"Copy-25042025/{table}"
           
#             dataframes = []
#             for blob in container_client.list_blobs(name_starts_with=folder_name):
#                 if blob.name.endswith(".parquet"):
#                     df = load_parquet_data(blob.name)
#                     dataframes.append(df)
           
#             if dataframes:
#                 combined_df = pd.concat(dataframes, ignore_index=True)
#                 self.dataframes[table] = combined_df
               
#                 if not self.active_df:
#                     self.active_df = combined_df
#                     self.active_table = table
   
#     def generate_code_from_query(self, query):
#         df_info = f"DataFrame Info for '{self.active_table}':\n"
#         df_info += f"- Shape: {self.active_df.shape}\n"
#         df_info += f"- Columns: {list(self.active_df.columns)}\n"
       
#         column_stats = {}
#         for col in self.active_df.columns:
#             try:
#                 if self.active_df[col].dtype in ['int64', 'float64']:
#                     column_stats[col] = {
#                         'dtype': str(self.active_df[col].dtype),
#                         'unique_values': self.active_df[col].unique()[:5].tolist(),
#                         'min': self.active_df[col].min(),
#                         'max': self.active_df[col].max(),
#                         'mean': self.active_df[col].mean() if self.active_df[col].dtype == 'float64' else None
#                     }
#                 else:
#                     column_stats[col] = {
#                         'dtype': str(self.active_df[col].dtype),
#                         'unique_values': self.active_df[col].unique()[:5].tolist(),
#                         'count': len(self.active_df[col].unique())
#                     }
#             except:
#                 column_stats[col] = {
#                     'dtype': str(self.active_df[col].dtype),
#                     'note': 'Could not calculate statistics'
#                 }
       
#         df_info += f"\nSample data (5 rows):\n{self.active_df.head(5).to_string()}\n\n"
#         df_info += f"Column statistics: {column_stats}\n"
       
#         prompt = f"""
#         We have data already loaded into a DataFrame called `df` with information below:
#         {df_info}
       
#         Generate Python code to create a professional, high-quality visualization for this query: "{query}"
       
#         Rules for generating beautiful visualizations:
#         - The data is already loaded in the variable `df`
#         - DO NOT include any file operations (read_csv, to_csv, etc.)
#         - ALWAYS create visualizations using seaborn or matplotlib with modern styling
#         - ALWAYS start with plt.figure(figsize=(12, 8)) for adequate chart size
#         - For sales data specifically:
#           * For time-based trends, use line charts with markers
#           * For product comparisons, use horizontal bar charts sorted by value
#           * For multi-dimensional analysis, consider heatmaps or multiple subplots
#           * Use currency formatting with commas for sales values (e.g., "$1,234,567")
#           * Show percentages for proportional data
#         - Use a professional color palette: 'viridis', 'plasma', or custom brand colors like ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
#         - Set style with sns.set_style("whitegrid") and sns.set_context("talk") for larger text
#         - Add clear, descriptive title with fontsize=16 and make axis labels readable with fontsize=14
#         - Include appropriate legends with fontsize=12
#         - Add plt.grid(True, alpha=0.3, linestyle='--') for subtle gridlines
#         - For time series data, use mdates for proper formatting and set rotation with plt.xticks(rotation=45, ha='right')
#         - Add data annotations for key values and insights
#         - Ensure data is properly sorted for better visualization (e.g., chronological for time series)
#         - Use colorful visualizations with distinct colors for different categories
#         - Highlight important data points or thresholds
#         - If comparing time periods, use side-by-side bars or overlapping transparent lines
#         - Include totals or averages as reference lines when appropriate
#         - For tables (like SalesDataProduct) with many columns, focus on relevant columns only
#         - Add plt.tight_layout(pad=1.5) to ensure no text is cut off
#         - Format all numeric values appropriately (add ₹ for INR currency, % for percentages)
#         - Return only the code without explanations
#         - Enclose the code in triple backticks (```)
 
#         Generate code that produces a visually appealing, professional-grade chart that clearly addresses the query and makes the insights obvious at first glance.
#         """
       
#         response = self.client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a data visualization expert specializing in creating beautiful, professional-grade charts using Python. You understand design principles like color theory, typography, and layout. You create visualizations that would be appropriate for business presentations and dashboards. You only return valid, executable Python code that ALWAYS produces a polished visualization."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.2,
#             max_tokens=1500
#         )
       
#         content = response.choices[0].message.content
#         pattern = r'```(?:python)?(.*?)```'
#         matches = re.findall(pattern, content, re.DOTALL)
       
#         if not matches:
#             return content.strip()
#         return matches[0].strip()
   
#     def execute_code(self, code):
#         img_buf = io.BytesIO()
       
#         try:
#             # Define helper functions for currency and number formatting
#             def format_inr(x, pos):
#                 """Format numbers as INR currency with commas"""
#                 if x >= 10000000:  # Crore
#                     return f'₹{x/10000000:.1f}Cr'
#                 elif x >= 100000:  # Lakh
#                     return f'₹{x/100000:.1f}L'
#                 elif x >= 1000:  # Thousand
#                     return f'₹{x/1000:.1f}K'
#                 else:
#                     return f'₹{x:.0f}'
           
#             # Add a helper function for number formatting with Indian system
#             def format_indian(x):
#                 """Format numbers with Indian number system (lakhs, crores)"""
#                 if isinstance(x, (int, float)):
#                     if x >= 10000000:
#                         return f'{x/10000000:.2f} Cr'
#                     elif x >= 100000:
#                         return f'{x/100000:.2f} L'
#                     elif x >= 1000:
#                         return f'{x/1000:.1f}K'
#                     else:
#                         return f'{x:.0f}'
#                 return x
           
#             local_namespace = {
#                 'df': self.active_df,
#                 'pd': pd,
#                 'np': np,
#                 'plt': plt,
#                 'sns': sns,
#                 'matplotlib': matplotlib,
#                 'mdates': mdates,
#                 'format_inr': format_inr,
#                 'format_indian': format_indian,
#                 'FuncFormatter': matplotlib.ticker.FuncFormatter
#             }
           
#             exec(code, {}, local_namespace)
           
#             if 'plt' in code:
#                 # Apply tight layout with padding to ensure no labels are cut off
#                 plt.tight_layout(pad=1.5)
#                 # Save with higher DPI and proper bounding box to avoid clipping
#                 plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight',
#                            facecolor='white', edgecolor='none', transparent=False)
#                 img_buf.seek(0)
               
#                 img_data = base64.b64encode(img_buf.getvalue()).decode()
#                 plt.close('all')
               
#                 return {
#                     'type': 'plot',
#                     'data': img_data,
#                     'format': 'image/png;base64',
#                     'message': 'Generated visualization'
#                 }
           
#             if 'result' in local_namespace:
#                 result = local_namespace['result']
#                 if isinstance(result, pd.DataFrame):
#                     return {
#                         'type': 'dataframe',
#                         'data': result.head(20).to_dict(orient='records'),
#                         'message': f'Dataframe result with {len(result)} rows (showing first 20)'
#                     }
#                 else:
#                     return {
#                         'type': 'result',
#                         'data': str(result),
#                         'message': 'Executed code and got result'
#                     }
           
#             last_var = None
#             for var_name, var_value in local_namespace.items():
#                 if var_name not in ['df', 'pd', 'np', 'plt'] and not var_name.startswith('_'):
#                     last_var = (var_name, var_value)
           
#             if last_var:
#                 var_name, var_value = last_var
#                 if isinstance(var_value, pd.DataFrame):
#                     return {
#                         'type': 'dataframe',
#                         'data': var_value.head(20).to_dict(orient='records'),
#                         'message': f'Created dataframe {var_name} with {len(var_value)} rows (showing first 20)'
#                     }
#                 else:
#                     return {
#                         'type': 'result',
#                         'data': str(var_value),
#                         'message': f'Variable {var_name} = {str(var_value)}'
#                     }
           
#             # If no explicit output but code included plotting commands, try to get the plot
#             if any(plt_cmd in code for plt_cmd in ['plt.', 'sns.']):
#                 # Apply tight layout with padding to ensure no labels are cut off
#                 plt.tight_layout(pad=1.5)
#                 # Save with higher DPI and proper bounding box to avoid clipping
#                 plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight',
#                            facecolor='white', edgecolor='none', transparent=False)
#                 img_buf.seek(0)
               
#                 img_data = base64.b64encode(img_buf.getvalue()).decode()
#                 plt.close('all')
               
#                 return {
#                     'type': 'plot',
#                     'data': img_data,
#                     'format': 'image/png;base64',
#                     'message': 'Generated visualization'
#                 }
           
#             return {
#                 'type': 'message',
#                 'data': 'Code executed successfully, but no visualization was generated',
#                 'message': 'No visualization output'
#             }
           
#         except Exception as e:
#             return {
#                 'type': 'error',
#                 'data': str(e),
#                 'message': f'Error executing code: {str(e)}'
#             }
   
#     def get_natural_language_response(self, query, code_result):
#         result_description = ""
       
#         if code_result['type'] == 'plot':
#             result_description = "I've generated a visualization based on your query. The chart shows the data graphically."
#         elif code_result['type'] == 'dataframe':
#             result_description = f"I've analyzed your data and created a result with {code_result['message']}."
#         elif code_result['type'] == 'result':
#             result_description = f"Based on your query, I found: {code_result['data']}"
#         elif code_result['type'] == 'error':
#             result_description = f"I encountered an error: {code_result['data']}"
       
#         data_context = f"Working with table '{self.active_table}' containing {len(self.active_df)} records with {len(self.active_df.columns)} columns."
       
#         prompt = f"""
#         User Query: {query}
       
#         Data Context: {data_context}
       
#         Result: {result_description}
       
#         Please provide a natural language interpretation of this visualization.
       
#         For sales data analysis, focus on:
#         1. Key performance metrics and their trends (revenue, quantity, average values)
#         2. Month-over-month or year-over-year comparisons with percentage changes
#         3. Seasonal patterns or cyclical trends in the sales data
#         4. Top performing products, customers, or regions
#         5. Correlation between sales volume and rejections/returns
#         6. Any unusual spikes or drops that require attention
#         7. Business recommendations based on the sales patterns observed
       
#         When providing currency values, use proper formatting with the ₹ symbol for Indian Rupees and use terms like 'lakhs' and 'crores' for large amounts.
       
#         Keep your explanation concise, business-focused, and actionable, highlighting the most important insights for decision makers.
#         """
       
#         response = self.client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a sales analytics expert who interprets data visualizations for business executives. You explain complex sales patterns in simple terms and provide actionable insights. You use Indian currency notation (₹, lakhs, crores) when discussing monetary values."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.3,
#             max_tokens=500
#         )
       
#         return response.choices[0].message.content
   
#     def chat(self, query, table_name=None):
#         # Handle table switching if provided
#         if table_name and table_name in self.dataframes:
#             self.active_df = self.dataframes[table_name]
#             self.active_table = table_name
       
#         if not self.active_df is not None:
#             return {"error": "No data loaded. Please load data first."}
       
#         # Add query to history
#         self.history.append({"role": "user", "query": query})
       
#         # Generate and execute code
#         generated_code = self.generate_code_from_query(query)
#         code_result = self.execute_code(generated_code)
       
#         # Generate natural language explanation
#         explanation = self.get_natural_language_response(query, code_result)
       
#         # Format the complete response
#         response = {
#             "query": query,
#             "explanation": explanation,
#             "code": generated_code,
#             "result": code_result,
#             "active_table": self.active_table
#         }
       
#         # Add to history
#         self.history.append({"role": "assistant", "response": response})
       
#         return response
 
 
# # Initialize the chatbot and load data (do this on server startup)
# chatbot = None
# try:
#     api_key = os.environ.get("OPENAI_API_KEY") or "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"
#     if api_key:
#         chatbot = DataAnalysisChatbot(api_key)
#         # Load data from Azure Blob Storage
#         table_names = ["salesdataproduct",
#                        "customerdetails",
#                     "productdetailsmarcmard",
#                     "salesaggregatesmonthwise",
#                     "customerdetails4470",
#                     "datedetails",
#                     "productdetailsupdated",
#                     "productdetailswithbillingdelivery",
#                     "plantdetails",
#                     "customerdetails_singletaxinfo",
#                     "productdetails",
#                     "customerdimtable",
#                     "customerdetailsunique",
#                     "productdetailsmara",
#                     "salesorgdetails"]
#         chatbot.load_data_from_azure(table_names)
# except Exception as e:
#     print(f"Error initializing chatbot: {str(e)}")
 
 
# class DataAnalysisAPIView(APIView):    
#     """
#     API endpoint for data analysis queries.
#     """
#     def get(self, request, format=None):
#         # Check if all requirements are met
#         missing_dependencies = []
#         if not REST_FRAMEWORK_AVAILABLE:
#             missing_dependencies.append("Django REST Framework")
#         if not DATA_SCIENCE_PACKAGES_AVAILABLE:
#             missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
#         if not AZURE_OPENAI_AVAILABLE:
#             missing_dependencies.append("Azure and OpenAI Packages")
       
#         if missing_dependencies:
#             return Response(
#                 {
#                     "message": "This endpoint only accepts POST requests with a 'query' parameter",
#                     "warning": "Missing dependencies: " + ", ".join(missing_dependencies)
#                 },
#                 status=status.HTTP_200_OK
#             )
#         return Response(
#             {"message": "This endpoint only accepts POST requests with a 'query' parameter"},
#             status=status.HTTP_200_OK
#         )
       
#     def post(self, request, format=None):
#         # Check if all requirements are met
#         missing_dependencies = []
#         if not REST_FRAMEWORK_AVAILABLE:
#             missing_dependencies.append("Django REST Framework")
#         if not DATA_SCIENCE_PACKAGES_AVAILABLE:
#             missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
#         if not AZURE_OPENAI_AVAILABLE:
#             missing_dependencies.append("Azure and OpenAI Packages")
       
#         if missing_dependencies:
#             return Response(
#                 {"error": "Missing dependencies: " + ", ".join(missing_dependencies)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
           
#         if not chatbot or not chatbot.dataframes:
#             return Response(
#                 {"error": "Chatbot not initialized or no data loaded. Make sure OPENAI_API_KEY is set in environment variables."},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
       
#         try:
#             data = JSONParser().parse(request)
#             query = data.get('query')
#             table_name = data.get('table_name')  # Optional parameter
           
#             if not query:
#                 return Response(
#                     {"error": "Query is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#               )
           
#             response = chatbot.chat(query, table_name)
#             return Response(response)
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
 
# def index(request):
#     return render(request, 'data_analysis_api/test.html')






# Demo

from django.http import JsonResponse
from django.shortcuts import render
 
# Try importing REST framework, or set a flag if it's not available
try:
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.parsers import JSONParser
    REST_FRAMEWORK_AVAILABLE = True
except ImportError:
    REST_FRAMEWORK_AVAILABLE = False
    # Define fallback classes
    class APIView:
        pass
    Response = JsonResponse
    class status:
        HTTP_200_OK = 200
        HTTP_400_BAD_REQUEST = 400
        HTTP_500_INTERNAL_SERVER_ERROR = 500
 
# Try importing data science packages
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import pyarrow.parquet as pq
    import io
    import os
    import re
    import base64
    import seaborn as sns
    import matplotlib
    import matplotlib.dates as mdates
    DATA_SCIENCE_PACKAGES_AVAILABLE = True
except ImportError:
    DATA_SCIENCE_PACKAGES_AVAILABLE = False
 
# Try importing Azure and OpenAI packages
try:
    from azure.storage.blob import ContainerClient
    from openai import OpenAI
    AZURE_OPENAI_AVAILABLE = True
except ImportError:
    AZURE_OPENAI_AVAILABLE = False
 
# Only set up these components if dependencies are available
if DATA_SCIENCE_PACKAGES_AVAILABLE:
    # Set the Matplotlib backend to Agg (non-interactive)
    plt.switch_backend('Agg')
 
# Initialize variables
container_client = None
chatbot = None
 
if AZURE_OPENAI_AVAILABLE:
    try:
        # SAS URL for the container
        sas_url = "https://saviaitdtldatalake.blob.core.windows.net/dblayer?<new-container-level-sas-token>"
        container_client = ContainerClient.from_container_url(sas_url)
    except Exception as e:
        pass
 
# Function to load data from a Parquet file in Azure Blob Storage
def load_parquet_data(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob()
    parquet_data = blob_data.readall()
    table = pq.read_table(io.BytesIO(parquet_data))
    df = table.to_pandas()
    return df
 
class DataAnalysisChatbot:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
       
        self.client = OpenAI(api_key=self.api_key)
        self.dataframes = {}
        self.active_df = None
        self.active_table = None
        self.history = []
   
    def load_data_from_azure(self, table_names):
        for table in table_names:
            folder_name = f"Copy-25042025/{table}"
           
            dataframes = []
            for blob in container_client.list_blobs(name_starts_with=folder_name):
                if blob.name.endswith(".parquet"):
                    df = load_parquet_data(blob.name)
                    dataframes.append(df)
           
            if dataframes:
                combined_df = pd.concat(dataframes, ignore_index=True)
                self.dataframes[table] = combined_df
               
                if not self.active_df:
                    self.active_df = combined_df
                    self.active_table = table
   
    def generate_code_from_query(self, query):
        df_info = f"DataFrame Info for '{self.active_table}':\n"
        df_info += f"- Shape: {self.active_df.shape}\n"
        df_info += f"- Columns: {list(self.active_df.columns)}\n"
       
        column_stats = {}
        for col in self.active_df.columns:
            try:
                if self.active_df[col].dtype in ['int64', 'float64']:
                    column_stats[col] = {
                        'dtype': str(self.active_df[col].dtype),
                        'unique_values': self.active_df[col].unique()[:5].tolist(),
                        'min': self.active_df[col].min(),
                        'max': self.active_df[col].max(),
                        'mean': self.active_df[col].mean() if self.active_df[col].dtype == 'float64' else None
                    }
                else:
                    column_stats[col] = {
                        'dtype': str(self.active_df[col].dtype),
                        'unique_values': self.active_df[col].unique()[:5].tolist(),
                        'count': len(self.active_df[col].unique())
                    }
            except:
                column_stats[col] = {
                    'dtype': str(self.active_df[col].dtype),
                    'note': 'Could not calculate statistics'
                }
       
        df_info += f"\nSample data (5 rows):\n{self.active_df.head(5).to_string()}\n\n"
        df_info += f"Column statistics: {column_stats}\n"
       
        prompt = f"""
        We have data already loaded into a DataFrame called `df` with information below:
        {df_info}
       
        Generate Python code to create a professional, high-quality visualization for this query: "{query}"
       
        Rules for generating beautiful visualizations:
        - The data is already loaded in the variable `df`
        - DO NOT include any file operations (read_csv, to_csv, etc.)
        - ALWAYS create visualizations using seaborn or matplotlib with modern styling
        - ALWAYS start with plt.figure(figsize=(12, 8)) for adequate chart size
        - For sales data specifically:
          * For time-based trends, use line charts with markers
          * For product comparisons, use horizontal bar charts sorted by value
          * For multi-dimensional analysis, consider heatmaps or multiple subplots
          * Use currency formatting with commas for sales values (e.g., "$1,234,567")
          * Show percentages for proportional data
        - Use a professional color palette: 'viridis', 'plasma', or custom brand colors like ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        - Set style with sns.set_style("whitegrid") and sns.set_context("talk") for larger text
        - Add clear, descriptive title with fontsize=16 and make axis labels readable with fontsize=14
        - Include appropriate legends with fontsize=12
        - Add plt.grid(True, alpha=0.3, linestyle='--') for subtle gridlines
        - For time series data, use mdates for proper formatting and set rotation with plt.xticks(rotation=45, ha='right')
        - Add data annotations for key values and insights
        - Ensure data is properly sorted for better visualization (e.g., chronological for time series)
        - Use colorful visualizations with distinct colors for different categories
        - Highlight important data points or thresholds
        - If comparing time periods, use side-by-side bars or overlapping transparent lines
        - Include totals or averages as reference lines when appropriate
        - For tables (like SalesDataProduct) with many columns, focus on relevant columns only
        - Add plt.tight_layout(pad=1.5) to ensure no text is cut off
        - Format all numeric values appropriately (add ₹ for INR currency, % for percentages)
        - Return only the code without explanations
        - Enclose the code in triple backticks (```)
 
        Generate code that produces a visually appealing, professional-grade chart that clearly addresses the query and makes the insights obvious at first glance.
        """
       
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data visualization expert specializing in creating beautiful, professional-grade charts using Python. You understand design principles like color theory, typography, and layout. You create visualizations that would be appropriate for business presentations and dashboards. You only return valid, executable Python code that ALWAYS produces a polished visualization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
       
        content = response.choices[0].message.content
        pattern = r'```(?:python)?(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
       
        if not matches:
            return content.strip()
        return matches[0].strip()
   
    def execute_code(self, code):
        img_buf = io.BytesIO()
       
        try:
            # Define helper functions for currency and number formatting
            def format_inr(x, pos):
                """Format numbers as INR currency with commas"""
                if x >= 10000000:  # Crore
                    return f'₹{x/10000000:.1f}Cr'
                elif x >= 100000:  # Lakh
                    return f'₹{x/100000:.1f}L'
                elif x >= 1000:  # Thousand
                    return f'₹{x/1000:.1f}K'
                else:
                    return f'₹{x:.0f}'
           
            # Add a helper function for number formatting with Indian system
            def format_indian(x):
                """Format numbers with Indian number system (lakhs, crores)"""
                if isinstance(x, (int, float)):
                    if x >= 10000000:
                        return f'{x/10000000:.2f} Cr'
                    elif x >= 100000:
                        return f'{x/100000:.2f} L'
                    elif x >= 1000:
                        return f'{x/1000:.1f}K'
                    else:
                        return f'{x:.0f}'
                return x
           
            local_namespace = {
                'df': self.active_df,
                'pd': pd,
                'np': np,
                'plt': plt,
                'sns': sns,
                'matplotlib': matplotlib,
                'mdates': mdates,
                'format_inr': format_inr,
                'format_indian': format_indian,
                'FuncFormatter': matplotlib.ticker.FuncFormatter
            }
           
            exec(code, {}, local_namespace)
           
            if 'plt' in code:
                # Apply tight layout with padding to ensure no labels are cut off
                plt.tight_layout(pad=1.5)
                # Save with higher DPI and proper bounding box to avoid clipping
                plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight',
                           facecolor='white', edgecolor='none', transparent=False)
                img_buf.seek(0)
               
                img_data = base64.b64encode(img_buf.getvalue()).decode()
                plt.close('all')
               
                return {
                    'type': 'plot',
                    'data': img_data,
                    'format': 'image/png;base64',
                    'message': 'Generated visualization'
                }
           
            if 'result' in local_namespace:
                result = local_namespace['result']
                if isinstance(result, pd.DataFrame):
                    return {
                        'type': 'dataframe',
                        'data': result.head(20).to_dict(orient='records'),
                        'message': f'Dataframe result with {len(result)} rows (showing first 20)'
                    }
                else:
                    return {
                        'type': 'result',
                        'data': str(result),
                        'message': 'Executed code and got result'
                    }
           
            last_var = None
            for var_name, var_value in local_namespace.items():
                if var_name not in ['df', 'pd', 'np', 'plt'] and not var_name.startswith('_'):
                    last_var = (var_name, var_value)
           
            if last_var:
                var_name, var_value = last_var
                if isinstance(var_value, pd.DataFrame):
                    return {
                        'type': 'dataframe',
                        'data': var_value.head(20).to_dict(orient='records'),
                        'message': f'Created dataframe {var_name} with {len(var_value)} rows (showing first 20)'
                    }
                else:
                    return {
                        'type': 'result',
                        'data': str(var_value),
                        'message': f'Variable {var_name} = {str(var_value)}'
                    }
           
            # If no explicit output but code included plotting commands, try to get the plot
            if any(plt_cmd in code for plt_cmd in ['plt.', 'sns.']):
                # Apply tight layout with padding to ensure no labels are cut off
                plt.tight_layout(pad=1.5)
                # Save with higher DPI and proper bounding box to avoid clipping
                plt.savefig(img_buf, format='png', dpi=150, bbox_inches='tight',
                           facecolor='white', edgecolor='none', transparent=False)
                img_buf.seek(0)
               
                img_data = base64.b64encode(img_buf.getvalue()).decode()
                plt.close('all')
               
                return {
                    'type': 'plot',
                    'data': img_data,
                    'format': 'image/png;base64',
                    'message': 'Generated visualization'
                }
           
            return {
                'type': 'message',
                'data': 'Code executed successfully, but no visualization was generated',
                'message': 'No visualization output'
            }
           
        except Exception as e:
            return {
                'type': 'error',
                'data': str(e),
                'message': f'Error executing code: {str(e)}'
            }
   
    def get_natural_language_response(self, query, code_result):
        result_description = ""
       
        if code_result['type'] == 'plot':
            result_description = "I've generated a visualization based on your query. The chart shows the data graphically."
        elif code_result['type'] == 'dataframe':
            result_description = f"I've analyzed your data and created a result with {code_result['message']}."
        elif code_result['type'] == 'result':
            result_description = f"Based on your query, I found: {code_result['data']}"
        elif code_result['type'] == 'error':
            result_description = f"I encountered an error: {code_result['data']}"
       
        data_context = f"Working with table '{self.active_table}' containing {len(self.active_df)} records with {len(self.active_df.columns)} columns."
       
        prompt = f"""
        User Query: {query}
       
        Data Context: {data_context}
       
        Result: {result_description}
       
        Please provide a natural language interpretation of this visualization.
       
        For sales data analysis, focus on:
        1. Key performance metrics and their trends (revenue, quantity, average values)
        2. Month-over-month or year-over-year comparisons with percentage changes
        3. Seasonal patterns or cyclical trends in the sales data
        4. Top performing products, customers, or regions
        5. Correlation between sales volume and rejections/returns
        6. Any unusual spikes or drops that require attention
        7. Business recommendations based on the sales patterns observed
       
        When providing currency values, use proper formatting with the ₹ symbol for Indian Rupees and use terms like 'lakhs' and 'crores' for large amounts.
       
        Keep your explanation concise, business-focused, and actionable, highlighting the most important insights for decision makers.
        """
       
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a sales analytics expert who interprets data visualizations for business executives. You explain complex sales patterns in simple terms and provide actionable insights. You use Indian currency notation (₹, lakhs, crores) when discussing monetary values."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
       
        return response.choices[0].message.content
   
    def chat(self, query, table_name=None):
        # Handle table switching if provided
        if table_name and table_name in self.dataframes:
            self.active_df = self.dataframes[table_name]
            self.active_table = table_name
       
        if not self.active_df is not None:
            return {"error": "No data loaded. Please load data first."}
       
        # Add query to history
        self.history.append({"role": "user", "query": query})
       
        # Generate and execute code
        generated_code = self.generate_code_from_query(query)
        code_result = self.execute_code(generated_code)
       
        # Generate natural language explanation
        explanation = self.get_natural_language_response(query, code_result)
       
        # Format the complete response
        response = {
            "query": query,
            "explanation": explanation,
            "code": generated_code,
            "result": code_result,
            "active_table": self.active_table
        }
       
        # Add to history
        self.history.append({"role": "assistant", "response": response})
       
        return response
 
 
# Initialize the chatbot and load data (do this on server startup)
chatbot = None
try:
    api_key = os.environ.get("OPENAI_API_KEY") or "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"
    if api_key:
        chatbot = DataAnalysisChatbot(api_key)
        # Load data from Azure Blob Storage
        table_names = ["salesdataproduct",
                       "customerdetails",
                    "productdetailsmarcmard",
                    "salesaggregatesmonthwise",
                    "customerdetails4470",
                    "datedetails",
                    "productdetailsupdated",
                    "productdetailswithbillingdelivery",
                    "plantdetails",
                    "customerdetails_singletaxinfo",
                    "productdetails",
                    "customerdimtable",
                    "customerdetailsunique",
                    "productdetailsmara",
                    "salesorgdetails"]
        chatbot.load_data_from_azure(table_names)
except Exception as e:
    pass
 
 
class DataAnalysisAPIView(APIView):    
    """
    API endpoint for data analysis queries.
    """
    def get(self, request, format=None):
        # Check if all requirements are met
        missing_dependencies = []
        if not REST_FRAMEWORK_AVAILABLE:
            missing_dependencies.append("Django REST Framework")
        if not DATA_SCIENCE_PACKAGES_AVAILABLE:
            missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
        if not AZURE_OPENAI_AVAILABLE:
            missing_dependencies.append("Azure and OpenAI Packages")
       
        if missing_dependencies:
            return Response(
                {
                    "message": "This endpoint only accepts POST requests with a 'query' parameter",
                    "warning": "Missing dependencies: " + ", ".join(missing_dependencies)
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "This endpoint only accepts POST requests with a 'query' parameter"},
            status=status.HTTP_200_OK
        )
       
    def post(self, request, format=None):
        # Check if all requirements are met
        missing_dependencies = []
        if not REST_FRAMEWORK_AVAILABLE:
            missing_dependencies.append("Django REST Framework")
        if not DATA_SCIENCE_PACKAGES_AVAILABLE:
            missing_dependencies.append("Data Science Packages (pandas, numpy, matplotlib, pyarrow)")
        if not AZURE_OPENAI_AVAILABLE:
            missing_dependencies.append("Azure and OpenAI Packages")
       
        if missing_dependencies:
            return Response(
                {"error": "Missing dependencies: " + ", ".join(missing_dependencies)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
           
        if not chatbot or not chatbot.dataframes:
            return Response(
                {"error": "Chatbot not initialized or no data loaded. Make sure OPENAI_API_KEY is set in environment variables."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
       
        try:
            data = JSONParser().parse(request)
            query = data.get('query')
            table_name = data.get('table_name')  # Optional parameter
           
            if not query:
                return Response(
                    {"error": "Query is required"},
                    status=status.HTTP_400_BAD_REQUEST
              )
           
            response = chatbot.chat(query, table_name)
            return Response(response)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )       
 
def index(request):
    return render(request, 'data_analysis_api/test.html')