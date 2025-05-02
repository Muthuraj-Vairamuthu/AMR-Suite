import matplotlib.pyplot as plt
import numpy as np
from scikits.bootstrap import ci
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import re
import pandas as pd
import subprocess
import json
import threading

def isolation_burden_analysis_graph(dataset, source, country, cluster_attribute, gender_filter, gender_column, mappings):
    
    custom_colors = ['#ff69b4', '#00bfff', '#90EE90']  # Pink, Blue, Green
    
    # source filter
    if source != 'All Sources':
        dataset = dataset[dataset[mappings['source_input']] == source]
    
    # country filter
    if country != 'All Countries':
        dataset = dataset[dataset['Country'] == country]
    
    # cluster attribute is selected
    if cluster_attribute != 'None':
        # gender filter is on 
        if gender_filter and gender_column != 'None':
            # Get top 5 values for the cluster attribute
            top_values = dataset[cluster_attribute].value_counts().nlargest(5).index
            dataset_filtered = dataset[dataset[cluster_attribute].isin(top_values)]
            grouped_data = dataset_filtered.groupby([cluster_attribute, gender_column]).size().unstack(fill_value=0)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            x = np.arange(len(grouped_data.index))
            width = 0.8 / len(grouped_data.columns)  
            colors = custom_colors[:len(grouped_data.columns)]
            
            # each gender category
            for i, (gender_cat, color) in enumerate(zip(grouped_data.columns, colors)):
                bars = ax.bar(x + i*width, grouped_data[gender_cat], width, 
                            label=gender_cat, color=color)
                
                # Add count labels on top of bars
                for j, v in enumerate(grouped_data[gender_cat]):
                    if v > 0:
                        ax.text(x[j] + i*width, v + 0.5, str(v), 
                                color='white', ha='center', fontsize=9)
            
            # Customize 
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by {cluster_attribute} and {gender_column}\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel(cluster_attribute, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            
            ax.set_xticks(x + width * (len(grouped_data.columns) - 1) / 2)
            ax.set_xticklabels(grouped_data.index, color='white', rotation=45, ha='right')
            
            # Add legend
            ax.legend(title=gender_column, facecolor='#1a1a1a', 
                     edgecolor='white', labelcolor='white', 
                     title_fontsize=10, fontsize=9)
            
        else:
            
            cluster_counts = dataset[cluster_attribute].value_counts().nlargest(5)
            
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            
            bars = ax.bar(range(len(cluster_counts)), cluster_counts.values, color='#00bfff')
            
            for i, v in enumerate(cluster_counts.values):
                ax.text(i, v + 0.5, str(v), color='white', ha='center')
            
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by {cluster_attribute}\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel(cluster_attribute, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            ax.set_xticks(range(len(cluster_counts)))
            ax.set_xticklabels(cluster_counts.index, color='white', rotation=45, ha='right')
    else:
        # gender filter is on 
        if gender_filter and gender_column != 'None':
            # Group 
            gender_counts = dataset[gender_column].value_counts().nlargest(5)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            colors = custom_colors[:len(gender_counts)]
            bars = ax.bar(range(len(gender_counts)), gender_counts.values, color=colors)
            
            # count label
            for i, v in enumerate(gender_counts.values):
                if v > 0:
                    ax.text(i, v + 0.5, str(v), color='white', ha='center', fontsize=9)
            
            # plot
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by {gender_column}\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel(gender_column, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            # x-axis labels
            ax.set_xticks(range(len(gender_counts)))
            ax.set_xticklabels(gender_counts.index, color='white', rotation=45, ha='right')
            
        else:
            # Just show total count
            total_count = len(dataset)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            bars = ax.bar([0], [total_count], color='#00bfff')
            
            # count label
            ax.text(0, total_count + 0.5, str(total_count), color='white', ha='center')
            
            # Customize the plot
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Total Isolation Burden\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            # Set x-axis labels
            ax.set_xticks([0])
            ax.set_xticklabels(['Total'], color='white')
    
    # Common styling
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, linestyle='--', alpha=0.3, color='white', axis='y')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()
    return fig


### working code with zero values marked as individual markers
def resistance_analysis_graph(dataset, source, infection, antibiotic_column, mappings):
    # Filter dataset first
    resistant_dataset = dataset[
        (dataset[mappings['source_input']] == source) &
        (dataset[mappings['bacterial_infection']] == infection)
    ].copy()
    
    # Convert year to integer and sort
    date_format = mappings['date_format']
    date_column = mappings['date_column']
    granularity = mappings['resistance_granularity']

    if date_format == 'DD/MM/YYYY':
        result = resistant_dataset[date_column].str.split('/')
        resistant_dataset['Year'] = result.str[2].astype(int)
        resistant_dataset['Month'] = result.str[1].astype(int)
        resistant_dataset['Day'] = result.str[0].astype(int)

    elif date_format == 'MM/DD/YYYY':
        result = resistant_dataset[date_column].str.split('/')
        resistant_dataset['Year'] = result.str[2].astype(int)
        resistant_dataset['Month'] = result.str[0].astype(int)
        resistant_dataset['Day'] = result.str[1].astype(int)

    elif date_format == 'YYYY/MM/DD':
        result = resistant_dataset[date_column].str.split('/')
        resistant_dataset['Year'] = result.str[0].astype(int)
        resistant_dataset['Month'] = result.str[1].astype(int)
        resistant_dataset['Day'] = result.str[2].astype(int)

    elif date_format == 'YYYY-MM-DD':
        result = resistant_dataset[date_column].str.split('-')
        resistant_dataset['Year'] = result.str[0].astype(int)
        resistant_dataset['Month'] = result.str[1].astype(int)
        resistant_dataset['Day'] = result.str[2].astype(int)

    elif date_format == 'MM-DD-YYYY':
        result = resistant_dataset[date_column].str.split('-')
        resistant_dataset['Year'] = result.str[2].astype(int)
        resistant_dataset['Month'] = result.str[0].astype(int)
        resistant_dataset['Day'] = result.str[1].astype(int)

    elif date_format == 'DD-MM-YYYY':
        result = resistant_dataset[date_column].str.split('-')
        resistant_dataset['Year'] = result.str[2].astype(int)
        resistant_dataset['Month'] = result.str[1].astype(int)
        resistant_dataset['Day'] = result.str[0].astype(int)
        
    elif date_format == 'YYYY':
        resistant_dataset['Year'] = resistant_dataset[date_column].astype(int)
        resistant_dataset['Month'] = 0
        resistant_dataset['Day'] = 0

    elif date_format == 'MM':
        resistant_dataset['Year'] = 0
        resistant_dataset['Month'] = resistant_dataset[date_column].astype(int)
        resistant_dataset['Day'] = 0

    elif date_format == 'DD':
        resistant_dataset['Year'] = 0
        resistant_dataset['Month'] = 0
        resistant_dataset['Day'] = resistant_dataset[date_column].astype(int)

    resistant_dataset = resistant_dataset.sort_values(by=['Year', 'Month', 'Day'])

    if granularity == 'yearly':
        antibiotic_data = resistant_dataset.groupby('Year')[antibiotic_column].value_counts().unstack(fill_value=0)
    
    elif granularity == 'monthly':
        antibiotic_data = resistant_dataset.groupby(['Year', 'Month'])[antibiotic_column].value_counts().unstack(fill_value=0)

    elif granularity == 'daily':
        antibiotic_data = resistant_dataset.groupby(['Year', 'Month', 'Day'])[antibiotic_column].value_counts().unstack(fill_value=0)

    # Calculate resistance rate
    values = resistant_dataset[antibiotic_column].unique()
    resistant_value = [i for i in values if i and i.startswith('R')][0]

    if resistant_value in antibiotic_data.columns:
        antibiotic_data['Total'] = antibiotic_data.sum(axis=1)
        antibiotic_data['Resistance Rate'] = (antibiotic_data[resistant_value] / antibiotic_data['Total']) * 100
    else:
        antibiotic_data['Resistance Rate'] = 0.0
    
    # Filter valid years with data
    valid_data = antibiotic_data[antibiotic_data['Total'] > 0]
    
    # Calculate confidence intervals
    valid_data['ci_lower'] = np.nan
    valid_data['ci_upper'] = np.nan

    for idx in valid_data.index:
        resistant = valid_data.loc[idx, resistant_value]
        total = valid_data.loc[idx, 'Total']
        if total == 0:
            continue
        # Create binary data: 1s for resistant, 0s otherwise
        samples = np.concatenate([np.ones(int(resistant)), np.zeros(int(total - resistant))])
        try:
            # Compute 95% CI using bootstrap
            ci_lower, ci_upper = ci(samples, statfunction=np.mean, n_samples=1000)
            valid_data.loc[idx, 'ci_lower'] = ci_lower * 100
            valid_data.loc[idx, 'ci_upper'] = ci_upper * 100
        except Exception as e:
            # Handle cases where calculation fails
            valid_data.loc[idx, 'ci_lower'] = np.nan
            valid_data.loc[idx, 'ci_upper'] = np.nan

    # Clip CI values to 0-100%
    valid_data['ci_lower'] = valid_data['ci_lower'].clip(lower=0)
    valid_data['ci_upper'] = valid_data['ci_upper'].clip(upper=100)

    # Extract data for plotting
    if granularity == 'yearly':
        years = valid_data.index.tolist()
        resistant_rates = valid_data['Resistance Rate'].tolist()
        ci_lower = valid_data['ci_lower'].tolist()
        ci_upper = valid_data['ci_upper'].tolist()
    elif granularity == 'monthly':
        res = valid_data.index.tolist()
        years = [f'{r[0]}-{r[1]}' for r in res]
        resistant_rates = valid_data['Resistance Rate'].tolist()
        ci_lower = valid_data['ci_lower'].tolist()
        ci_upper = valid_data['ci_upper'].tolist()
    elif granularity == 'daily':
        res = valid_data.index.tolist()
        years = [f'{r[0]}-{r[1]}-{r[2]}' for r in res]
        resistant_rates = valid_data['Resistance Rate'].tolist()
        ci_lower = valid_data['ci_lower'].tolist()
        ci_upper = valid_data['ci_upper'].tolist()

    # Create figure with dark background
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)

    # Set dark background
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')

    # ===== NEW CODE STARTS HERE =====
    # Identify segments of non-zero values and zero points
    segments = []
    current_segment = []
    zero_indices = []

    for i, rate in enumerate(resistant_rates):
        if rate == 0:
            zero_indices.append(i)
            if current_segment:  # Close current segment if exists
                segments.append(current_segment)
                current_segment = []
        else:
            current_segment.append(i)

    if current_segment:  # Add the last segment if it exists
        segments.append(current_segment)

    # Plot each non-zero segment with connecting lines
    for segment in segments:
        seg_years = [years[i] for i in segment]
        seg_rates = [resistant_rates[i] for i in segment]
        seg_ci_lower = [ci_lower[i] for i in segment]
        seg_ci_upper = [ci_upper[i] for i in segment]
        
        # Plot line with markers for this segment
        ax.plot(seg_years, seg_rates, 
                marker='o', linestyle='-', 
                color='#00bfff', 
                linewidth=2, markersize=8)
        
        # Plot confidence interval for this segment
        ax.fill_between(seg_years, seg_ci_lower, seg_ci_upper,
                    color='#00bfff', alpha=0.2)

    # Plot zero values as individual markers
    if zero_indices:
        zero_years = [years[i] for i in zero_indices]
        zero_rates = [resistant_rates[i] for i in zero_indices]
        ax.plot(zero_years, zero_rates, 
                'o',  # Just markers, no lines
                markersize=8,
                markerfacecolor='#666666',  # Gray fill
                markeredgecolor='white',    # White border
                linestyle='none')           # No connecting lines
    # ===== NEW CODE ENDS HERE =====

    # Keep all the existing styling code below
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.tick_params(colors='white')

    plt.title(f'Resistance Rate Over Time\n{infection} - {antibiotic_column} - {source}', 
            color='white', pad=20, fontsize=14)
    plt.xlabel('Year', color='white', fontsize=12)
    plt.ylabel('Resistance Rate (%)', color='white', fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1f}%'.format(y)))
    plt.tight_layout()

    return fig


import matplotlib.pyplot as plt
import numpy as np
from scikits.bootstrap import ci
import pandas as pd


def scorecard_analysis(dataset, source_input, infection, antibiotic, mappings):
    scorecard_dataset = dataset.sort_values(by='Year')
    scorecard_dataset = scorecard_dataset[(scorecard_dataset[mappings['source_input']] == source_input) & (scorecard_dataset[mappings['bacterial_infection']] == infection)]
    valid_values = ['Resistant', 'Intermediate', 'Susceptible']

    date_format = mappings['date_format']
    date_column = mappings['date_column']

    if date_format == 'DD/MM/YYYY':
        result = scorecard_dataset[date_column].str.split('/')
        scorecard_dataset['Year'] = result.str[2].astype(int)
        scorecard_dataset['Month'] = result.str[1].astype(int)
        scorecard_dataset['Day'] = result.str[0].astype(int)


    elif date_format == 'MM/DD/YYYY':
        result = scorecard_dataset[date_column].str.split('/')
        scorecard_dataset['Year'] = result.str[2].astype(int)
        scorecard_dataset['Month'] = result.str[0].astype(int)
        scorecard_dataset['Day'] = result.str[1].astype(int)
    
    elif date_format == 'YYYY/MM/DD':
        result = scorecard_dataset[date_column].str.split('/')
        scorecard_dataset['Year'] = result.str[0].astype(int)
        scorecard_dataset['Month'] = result.str[1].astype(int)
        scorecard_dataset['Day'] = result.str[2].astype(int)
    
    elif date_format == 'YYYY-MM-DD':
        result = scorecard_dataset[date_column].str.split('-')
        scorecard_dataset['Year'] = result.str[0].astype(int)
        scorecard_dataset['Month'] = result.str[1].astype(int)
        scorecard_dataset['Day'] = result.str[2].astype(int)

    elif date_format == 'MM-DD-YYYY':
        result = scorecard_dataset[date_column].str.split('-')
        scorecard_dataset['Year'] = result.str[2].astype(int)
        scorecard_dataset['Month'] = result.str[0].astype(int)
        scorecard_dataset['Day'] = result.str[1].astype(int)

    elif date_format == 'DD-MM-YYYY':
        result = scorecard_dataset[date_column].str.split('-')
        scorecard_dataset['Year'] = result.str[2].astype(int)
        scorecard_dataset['Month'] = result.str[1].astype(int)
        scorecard_dataset['Day'] = result.str[0].astype(int)

    elif date_format == 'YYYY':
        scorecard_dataset['Year'] = scorecard_dataset[date_column].astype(int)
        scorecard_dataset['Month'] = 0
        scorecard_dataset['Day'] = 0

    elif date_format == 'MM':
        scorecard_dataset['Year'] = 0
        scorecard_dataset['Month'] = scorecard_dataset[date_column].astype(int)
        scorecard_dataset['Day'] = 0

    elif date_format == 'DD':
        scorecard_dataset['Year'] = 0
        scorecard_dataset['Month'] = 0
        scorecard_dataset['Day'] = scorecard_dataset[date_column].astype(int)

    scorecard_dataset = scorecard_dataset.sort_values(by=['Year', 'Month', 'Day'])

    cluster_granularity = mappings['time_stamp']

    if cluster_granularity == 'Year':
        start = scorecard_dataset['Year'].min()
        end = scorecard_dataset['Year'].max()

    elif cluster_granularity == 'Month':
        start = scorecard_dataset['Month'].min()
        end = scorecard_dataset['Month'].max()

    elif cluster_granularity == 'Day':
        start = scorecard_dataset['Day'].min()
        end = scorecard_dataset['Day'].max()

    
    scorecard_dataset.to_csv('static/media/Data.csv', index=False)
    dataset_path = "static/media/Data.csv"

    # Path to the R script
    r_script_path = "static/media/cluster_model_final.R"

    threads = []
    time_gap = int(mappings['time_gap_attribute'])

    for i in range(start, end + 1, time_gap):
        chunk_end = min(i + time_gap - 1, end)
        thread = threading.Thread(
            target=run_r_script,
            args=(infection, antibiotic, source_input, i, chunk_end, dataset_path, mappings)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Now generate figures
    figures, visualization_data = generate_scorecard_graph(source_input, infection, antibiotic, dataset, mappings)
    return figures, visualization_data

def run_r_script(infection, antibiotic, source_input, start, end, dataset_path, mappings):
    r_script_path = "static/media/cluster_model_final.R"
    cmd = [
        'Rscript', r_script_path, infection, antibiotic,
        source_input, str(start), str(end), dataset_path,
        mappings['cluster_attribute'], mappings['time_stamp']
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
    
def generate_scorecard_graph(source, infection, antibiotic, dataset, mappings):
    time_series_dir = 'Time series data'
    json_output_dir = 'Scorecards JSONs'
    folder = os.path.join(time_series_dir, infection, source, antibiotic)
    files = os.listdir(folder)

    if len(files) == 0:
        print(f"No files found in {folder}")
        return None, None

    if '.DS_Store' in files:
        files.remove('.DS_Store')

    cluster_attributes = dataset[mappings['cluster_attribute']].unique()

    # Create a colorful palette with distinct colors for each country/attribute
    # Using more vibrant colors similar to the example image
    color_palette = plt.cm.gist_rainbow(np.linspace(0, 1, len(cluster_attributes)))
    attribute_colors = {attr: color_palette[i] for i, attr in enumerate(cluster_attributes)}

    # Regular expression to extract year from filenames
    file_pattern = re.compile(r"(?P<organism>[^_]+)_(?P<antibiotic>[^_]+)_I_(?P<year>\d{4})")

    # Create a list to store file paths and metadata
    file_data = []
    figures = []
    
    # Structured data for visualization
    visualization_data = {
        'years': [],
        'countries': {}  # Use dict first for easier lookup, then convert to list
    }
    
    for file_name in files:
        match = file_pattern.match(file_name)
        if match:
            metadata = match.groupdict()
            metadata['file_path'] = os.path.join(folder, file_name)
            file_data.append(metadata)

    if len(file_data) == 0:
        print(f"No files found in {folder}")
        return None, None

    # Group files by organism and antibiotic
    grouped_files = {}
    for data in file_data:
        key = (data['organism'], data['antibiotic'])
        if key not in grouped_files:
            grouped_files[key] = []
        grouped_files[key].append(data)

    # Process each organism-antibiotic combination
    for (organism, antibiotic), files in grouped_files.items():
        # Determine global min and max for consistent axes
        global_intercept_min = float('inf')
        global_intercept_max = float('-inf')
        global_slope_min = float('inf')
        global_slope_max = float('-inf')

        json_results = []
        for data in files:
            df = pd.read_csv(data['file_path'])
            assert(len(df) == len(df.dropna()))

            country_data = df[df['Cluster'] != 'Global']
            global_average = df[df['Cluster'] == 'Global'].iloc[0]

            # Calculate new slope and intercept
            country_data['slope'] += global_average['slope']
            country_data['intercept'] += global_average['intercept']

            # Update global min and max values
            global_intercept_min = min(global_intercept_min, country_data['intercept'].min())
            global_intercept_max = max(global_intercept_max, country_data['intercept'].max())
            global_slope_min = min(global_slope_min, country_data['slope'].min())
            global_slope_max = max(global_slope_max, country_data['slope'].max())

        # Add padding to the limits
        global_slope_min -= 1.0
        global_slope_max += 1.0
        global_intercept_min = max(0, global_intercept_min - 1)  # Ensure it starts at 0 or slightly below
        global_intercept_max += 5

        for data in files:
            df = pd.read_csv(data['file_path'])
            year = data['year']

            country_data = df[df['Cluster'] != 'Global']
            global_average = df[df['Cluster'] == 'Global'].iloc[0]

            # Calculate new slope and intercept
            country_data['slope'] += global_average['slope']
            country_data['intercept'] += global_average['intercept']
            
            # Plot median lines
            median_slope = country_data['slope'].median()
            median_intercept = country_data['intercept'].median()


            # Create the structured data for this year
            year_data = {
                "year": year,
                "median_slope": float(median_slope),
                "median_intercept": float(median_intercept),
                "countries": []
            }
            
            # Add country data points
            for _, row in country_data.iterrows():
                country_name = row['Cluster']
                x_value = float(row['intercept'])
                y_value = float(row['slope'])
                
                # Add to year data
                year_data["countries"].append({
                    "name": country_name,
                    "x": x_value,
                    "y": y_value
                })
                
                # Add to countries data structure
                if country_name not in visualization_data['countries']:
                    visualization_data['countries'][country_name] = {
                        'name': country_name,
                        'years': []
                    }
                
                # Add this year's data to the country
                visualization_data['countries'][country_name]['years'].append({
                    'year': year,
                    'x': x_value,
                    'y': y_value,
                    'median_intercept': float(median_intercept),
                    'median_slope': float(median_slope)
                })
            
            # Add year data to visualization structure
            visualization_data['years'].append(year_data)

            # Construct the full output directory path
            output_path = os.path.join(json_output_dir, infection, source, antibiotic)
            os.makedirs(output_path, exist_ok=True)

            # Save the JSON file inside the constructed path
            json_file_path = os.path.join(output_path, f"{organism}_{antibiotic}_{year}_scorecard.json")
            with open(json_file_path, 'w') as json_file:
                json.dump(year_data, json_file, indent=4)
            
            # You can add code here to save the figure to a file if needed
            # plt.savefig(f'output/{year}_scorecard.png', dpi=300, bbox_inches='tight')
    
    # Convert countries dictionary to list for the final output
    visualization_data['countries'] = list(visualization_data['countries'].values())
    
    return figures, visualization_data