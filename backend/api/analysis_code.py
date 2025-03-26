import matplotlib.pyplot as plt
import numpy as np
from scikits.bootstrap import ci
import matplotlib.pyplot as plt
import numpy as np
from scikits.bootstrap import ci

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



#OLD CODE WITHOUT CI VALUES
# def resistance_analysis_graph(dataset, source, infection, antibiotic, gender_filter, gender_column, mappings):
   
#     custom_colors = ['#ff69b4', '#00bfff', '#90EE90']  # Pink, Blue, Green
    
#     # Filter dataset
#     resistant_dataset = dataset[
#         (dataset[mappings['source_input']] == source) & 
#         (dataset[mappings['bacterial_infection']] == infection)
#     ]
    
    
#     fig = plt.figure(figsize=(12, 6))
#     ax = fig.add_subplot(111)
#     ax.set_facecolor('#1a1a1a')
#     fig.patch.set_facecolor('#1a1a1a')
    
#     # gender filter is on
#     if gender_filter and gender_column != 'None':
#         gender_groups = resistant_dataset[gender_column].unique()
        
#         # each gender
#         for i, gender in enumerate(gender_groups):
#             gender_data = resistant_dataset[resistant_dataset[gender_column] == gender].copy()
            
#             # Process date information for this gender group
#             date_format = mappings['date_format']
#             date_column = mappings['date_column']
#             granularity = mappings['resistance_granularity']

#             # Date processing based on format
#             if date_format == 'DD/MM/YYYY':
#                 result = gender_data[date_column].str.split('/')
#                 gender_data['Year'] = result.str[2].astype(int)
#                 gender_data['Month'] = result.str[1].astype(int)
#                 gender_data['Day'] = result.str[0].astype(int)
#             elif date_format == 'MM/DD/YYYY':
#                 result = gender_data[date_column].str.split('/')
#                 gender_data['Year'] = result.str[2].astype(int)
#                 gender_data['Month'] = result.str[0].astype(int)
#                 gender_data['Day'] = result.str[1].astype(int)
#             elif date_format == 'YYYY/MM/DD':
#                 result = gender_data[date_column].str.split('/')
#                 gender_data['Year'] = result.str[0].astype(int)
#                 gender_data['Month'] = result.str[1].astype(int)
#                 gender_data['Day'] = result.str[2].astype(int)
#             elif date_format == 'YYYY-MM-DD':
#                 result = gender_data[date_column].str.split('-')
#                 gender_data['Year'] = result.str[0].astype(int)
#                 gender_data['Month'] = result.str[1].astype(int)
#                 gender_data['Day'] = result.str[2].astype(int)
#             elif date_format == 'MM-DD-YYYY':
#                 result = gender_data[date_column].str.split('-')
#                 gender_data['Year'] = result.str[2].astype(int)
#                 gender_data['Month'] = result.str[0].astype(int)
#                 gender_data['Day'] = result.str[1].astype(int)
#             elif date_format == 'DD-MM-YYYY':
#                 result = gender_data[date_column].str.split('-')
#                 gender_data['Year'] = result.str[2].astype(int)
#                 gender_data['Month'] = result.str[1].astype(int)
#                 gender_data['Day'] = result.str[0].astype(int)
#             elif date_format == 'YYYY':
#                 gender_data['Year'] = gender_data[date_column].astype(int)
#                 gender_data['Month'] = 1
#                 gender_data['Day'] = 1
#             elif date_format == 'MM':
#                 gender_data['Year'] = 2024  # Default year
#                 gender_data['Month'] = gender_data[date_column].astype(int)
#                 gender_data['Day'] = 1
#             elif date_format == 'DD':
#                 gender_data['Year'] = 2024  # Default year
#                 gender_data['Month'] = 1
#                 gender_data['Day'] = gender_data[date_column].astype(int)

#             # Group by date and calculate resistance rate
#             if granularity == 'yearly':
#                 grouped = gender_data.groupby('Year')
#             elif granularity == 'monthly':
#                 grouped = gender_data.groupby(['Year', 'Month'])
#             else:  # daily
#                 grouped = gender_data.groupby(['Year', 'Month', 'Day'])

#             # Calculate resistance rates
#             resistance_rates = []
#             dates = []
            
#             for name, group in grouped:
#                 total = len(group)
#                 resistant = len(group[group[antibiotic].str.startswith('R', na=False)])
#                 rate = (resistant / total * 100) if total > 0 else 0
#                 resistance_rates.append(rate)
                
#                 if granularity == 'yearly':
#                     dates.append(str(name))
#                 elif granularity == 'monthly':
#                     dates.append(f"{name[0]}-{name[1]}")
#                 else:
#                     dates.append(f"{name[0]}-{name[1]}-{name[2]}")
            
#             # gender
#             line = ax.plot(dates, resistance_rates, 
#                          marker='o', linestyle='-', color=custom_colors[i % len(custom_colors)], 
#                          linewidth=2, markersize=8, label=gender)
            
#             # Add fill
#             ax.fill_between(dates, resistance_rates, 
#                           color=custom_colors[i % len(custom_colors)], alpha=0.2)
    
#     else:
#         # Original single-line plot code
#         # Process date information
#         date_format = mappings['date_format']
#         date_column = mappings['date_column']
#         granularity = mappings['resistance_granularity']

#         if date_format == 'DD/MM/YYYY':
#             result = resistant_dataset[date_column].str.split('/')
#             resistant_dataset['Year'] = result.str[2].astype(int)
#             resistant_dataset['Month'] = result.str[1].astype(int)
#             resistant_dataset['Day'] = result.str[0].astype(int)

#         elif date_format == 'MM/DD/YYYY':
#             result = resistant_dataset[date_column].str.split('/')
#             resistant_dataset['Year'] = result.str[2].astype(int)
#             resistant_dataset['Month'] = result.str[0].astype(int)
#             resistant_dataset['Day'] = result.str[1].astype(int)

#         elif date_format == 'YYYY/MM/DD':
#             result = resistant_dataset[date_column].str.split('/')
#             resistant_dataset['Year'] = result.str[0].astype(int)
#             resistant_dataset['Month'] = result.str[1].astype(int)
#             resistant_dataset['Day'] = result.str[2].astype(int)

#         elif date_format == 'YYYY-MM-DD':
#             result = resistant_dataset[date_column].str.split('-')
#             resistant_dataset['Year'] = result.str[0].astype(int)
#             resistant_dataset['Month'] = result.str[1].astype(int)
#             resistant_dataset['Day'] = result.str[2].astype(int)

#         elif date_format == 'MM-DD-YYYY':
#             result = resistant_dataset[date_column].str.split('-')
#             resistant_dataset['Year'] = result.str[2].astype(int)
#             resistant_dataset['Month'] = result.str[0].astype(int)
#             resistant_dataset['Day'] = result.str[1].astype(int)

#         elif date_format == 'DD-MM-YYYY':
#             result = resistant_dataset[date_column].str.split('-')
#             resistant_dataset['Year'] = result.str[2].astype(int)
#             resistant_dataset['Month'] = result.str[1].astype(int)
#             resistant_dataset['Day'] = result.str[0].astype(int)
        
#         elif date_format == 'YYYY':
#             resistant_dataset['Year'] = resistant_dataset[date_column].astype(int)
#             resistant_dataset['Month'] = 0
#             resistant_dataset['Day'] = 0

#         elif date_format == 'MM':
#             resistant_dataset['Year'] = 0
#             resistant_dataset['Month'] = resistant_dataset[date_column].astype(int)
#             resistant_dataset['Day'] = 0

#         elif date_format == 'DD':
#             resistant_dataset['Year'] = 0
#             resistant_dataset['Month'] = 0
#             resistant_dataset['Day'] = resistant_dataset[date_column].astype(int)

#         resistant_dataset = resistant_dataset.sort_values(by=['Year', 'Month', 'Day'])

#         if granularity == 'yearly':
#             antibiotic_data = resistant_dataset.groupby('Year')[antibiotic].value_counts().unstack(fill_value=0)
        
#         elif granularity == 'monthly':
#             antibiotic_data = resistant_dataset.groupby(['Year', 'Month'])[antibiotic].value_counts().unstack(fill_value=0)

#         elif granularity == 'daily':
#             antibiotic_data = resistant_dataset.groupby(['Year', 'Month', 'Day'])[antibiotic].value_counts().unstack(fill_value=0)

#         # Calculate resistance rate
#         values = resistant_dataset[antibiotic].unique()
#         resistant_value = [i for i in values if i and i.startswith('R')][0]

#         if resistant_value in antibiotic_data.columns:
#             antibiotic_data['Total'] = antibiotic_data.sum(axis=1)
#             antibiotic_data['Resistance Rate'] = (antibiotic_data[resistant_value] / antibiotic_data['Total']) * 100
#         else:
#             antibiotic_data['Resistance Rate'] = 0.0
        
#         # Filter valid years with data
#         valid_data = antibiotic_data[antibiotic_data['Total'] > 0]
#         if granularity == 'yearly':
#             years = valid_data.index.tolist()
#             resistant_rates = valid_data['Resistance Rate'].tolist()

#         elif granularity == 'monthly':
#             res = valid_data.index.tolist()
#             years = [f'{r[0]}-{r[1]}' for r in res]
#             resistant_rates = valid_data['Resistance Rate'].tolist()

#         elif granularity == 'daily':
#             res = valid_data.index.tolist()
#             years = [f'{r[0]}-{r[1]}-{r[2]}' for r in res]
#             resistant_rates = valid_data['Resistance Rate'].tolist()

#         # Plot for non-filtered case
#         line = ax.plot(years, resistant_rates, marker='o', linestyle='-', color='#00bfff', linewidth=2, markersize=8)
#         ax.fill_between(years, resistant_rates, color='#00bfff', alpha=0.2)
    
#     # Common styling
#     ax.grid(True, linestyle='--', alpha=0.3, color='white')
#     ax.spines['bottom'].set_color('white')
#     ax.spines['top'].set_color('white')
#     ax.spines['left'].set_color('white')
#     ax.spines['right'].set_color('white')
#     ax.tick_params(colors='white')
    
#     plt.title(f'Resistance Rate Over Time\n{infection} - {antibiotic} - {source}', 
#              color='white', pad=20, fontsize=14)
#     plt.xlabel('Time', color='white', fontsize=12)
#     plt.ylabel('Resistance Rate (%)', color='white', fontsize=12)
    
#     if gender_filter and gender_column != 'None':
#         plt.legend(title=gender_column, facecolor='#1a1a1a', 
#                   edgecolor='white', labelcolor='white',
#                   title_fontsize=10, fontsize=9)
    
#     # Rotate x-axis labels for better readability
#     plt.xticks(rotation=45, ha='right')
    
#     # Add percentage to y-axis
#     ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1f}%'.format(y)))
    
#     plt.tight_layout()
#     return fig
# def resistance_analysis_graph(dataset, source, infection, antibiotic_column, mappings):
#     # Filter dataset
#     resistant_dataset = dataset[
#         (dataset[mappings['source_input']] == source) &
#         (dataset[mappings['bacterial_infection']] == infection)
#     ].copy()

#     # Parse date columns
#     date_format = mappings['date_format']
#     date_column = mappings['date_column']
#     granularity = mappings['resistance_granularity']

#     if date_format == 'DD/MM/YYYY':
#         result = resistant_dataset[date_column].str.split('/')
#         resistant_dataset['Year'] = result.str[2].astype(int)
#         resistant_dataset['Month'] = result.str[1].astype(int)
#         resistant_dataset['Day'] = result.str[0].astype(int)
#     elif date_format == 'MM/DD/YYYY':
#         result = resistant_dataset[date_column].str.split('/')
#         resistant_dataset['Year'] = result.str[2].astype(int)
#         resistant_dataset['Month'] = result.str[0].astype(int)
#         resistant_dataset['Day'] = result.str[1].astype(int)
#     elif date_format == 'YYYY/MM/DD':
#         result = resistant_dataset[date_column].str.split('/')
#         resistant_dataset['Year'] = result.str[0].astype(int)
#         resistant_dataset['Month'] = result.str[1].astype(int)
#         resistant_dataset['Day'] = result.str[2].astype(int)
#     elif date_format == 'YYYY-MM-DD':
#         result = resistant_dataset[date_column].str.split('-')
#         resistant_dataset['Year'] = result.str[0].astype(int)
#         resistant_dataset['Month'] = result.str[1].astype(int)
#         resistant_dataset['Day'] = result.str[2].astype(int)
#     elif date_format == 'MM-DD-YYYY':
#         result = resistant_dataset[date_column].str.split('-')
#         resistant_dataset['Year'] = result.str[2].astype(int)
#         resistant_dataset['Month'] = result.str[0].astype(int)
#         resistant_dataset['Day'] = result.str[1].astype(int)
#     elif date_format == 'DD-MM-YYYY':
#         result = resistant_dataset[date_column].str.split('-')
#         resistant_dataset['Year'] = result.str[2].astype(int)
#         resistant_dataset['Month'] = result.str[1].astype(int)
#         resistant_dataset['Day'] = result.str[0].astype(int)
#     elif date_format == 'YYYY':
#         resistant_dataset['Year'] = resistant_dataset[date_column].astype(int)
#         resistant_dataset['Month'] = 0
#         resistant_dataset['Day'] = 0
#     elif date_format == 'MM':
#         resistant_dataset['Year'] = 0
#         resistant_dataset['Month'] = resistant_dataset[date_column].astype(int)
#         resistant_dataset['Day'] = 0
#     elif date_format == 'DD':
#         resistant_dataset['Year'] = 0
#         resistant_dataset['Month'] = 0
#         resistant_dataset['Day'] = resistant_dataset[date_column].astype(int)

#     resistant_dataset = resistant_dataset.sort_values(by=['Year', 'Month', 'Day'])

#     # Grouping
#     if granularity == 'yearly':
#         grouped = resistant_dataset.groupby('Year')[antibiotic_column].value_counts().unstack(fill_value=0)
#     elif granularity == 'monthly':
#         grouped = resistant_dataset.groupby(['Year', 'Month'])[antibiotic_column].value_counts().unstack(fill_value=0)
#     elif granularity == 'daily':
#         grouped = resistant_dataset.groupby(['Year', 'Month', 'Day'])[antibiotic_column].value_counts().unstack(fill_value=0)

#     values = resistant_dataset[antibiotic_column].unique()
#     resistant_value = [v for v in values if v and v.startswith('R')]
#     resistant_value = resistant_value[0] if resistant_value else None

#     if resistant_value and resistant_value in grouped.columns:
#         grouped['Total'] = grouped.sum(axis=1)
#         grouped['Resistance Rate'] = (grouped[resistant_value] / grouped['Total']) * 100

#         # Bootstrap confidence intervals
#         def bootstrap_ci_rate(resistant, total):
#             if total == 0:
#                 return np.nan, np.nan
#             samples = np.concatenate([np.ones(resistant), np.zeros(total - resistant)])
#             try:
#                 ci_low, ci_high = ci(samples, statfunction=np.mean, n_samples=1000)
#                 return ci_low * 100, ci_high * 100
#             except Exception:
#                 return np.nan, np.nan

#         ci_bounds = grouped.apply(
#             lambda row: bootstrap_ci_rate(row[resistant_value], row['Total']), axis=1
#         )
#         grouped['ci_lower'] = [c[0] for c in ci_bounds]
#         grouped['ci_upper'] = [c[1] for c in ci_bounds]
#     else:
#         grouped['Resistance Rate'] = 0.0
#         grouped['ci_lower'] = 0.0
#         grouped['ci_upper'] = 0.0

#     valid_data = grouped[grouped['Total'] > 0]

#     if granularity == 'yearly':
#         x = valid_data.index.tolist()
#     elif granularity == 'monthly':
#         x = [f"{i[0]}-{i[1]:02}" for i in valid_data.index]
#     elif granularity == 'daily':
#         x = [f"{i[0]}-{i[1]:02}-{i[2]:02}" for i in valid_data.index]

#     y = valid_data['Resistance Rate'].tolist()
#     y_lower = valid_data['ci_lower'].tolist()
#     y_upper = valid_data['ci_upper'].tolist()

#     # Plot
#     fig, ax = plt.subplots(figsize=(12, 6))
#     ax.set_facecolor('#1a1a1a')
#     fig.patch.set_facecolor('#1a1a1a')

#     ax.plot(x, y, marker='o', linestyle='-', color='#00bfff', linewidth=2, markersize=8, label='Resistance Rate')
#     ax.fill_between(x, y_lower, y_upper, color='#00bfff', alpha=0.3, label='95% CI')

#     ax.grid(True, linestyle='--', alpha=0.3, color='white')
#     for spine in ax.spines.values():
#         spine.set_color('white')
#     ax.tick_params(colors='white')
#     ax.set_title(f'Resistance Rate Over Time\n{infection} - {antibiotic_column} - {source}',
#                  color='white', pad=20, fontsize=14)
#     ax.set_xlabel('Time', color='white', fontsize=12)
#     ax.set_ylabel('Resistance Rate (%)', color='white', fontsize=12)
#     ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1f}%'.format(y)))
#     ax.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')

#     plt.tight_layout()
#     return fig

def scorecard_analysis(dataset, source, infection, antibiotic):
    scorecard_dataset = dataset.sort_values(by='Year')
    scorecard_dataset = scorecard_dataset[(scorecard_dataset[mappings['source_input']] == source) & (scorecard_dataset[mappings['bacterial_infection']] == infection)]
    valid_values = ['Resistant', 'Intermediate', 'Susceptible']