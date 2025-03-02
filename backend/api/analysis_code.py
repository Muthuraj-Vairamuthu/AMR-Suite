import matplotlib.pyplot as plt
import numpy as np

def isolation_burden_analysis_graph(dataset, source, country, cluster_attribute, gender_filter, mappings):
    # Filter dataset based on source if not 'All Sources'
    if source != 'All Sources':
        dataset = dataset[dataset[mappings['source_input']] == source]
    
    # Filter dataset based on country if specific country selected
    if country != 'All Countries':
        dataset = dataset[dataset['Country'] == country]
    
    # If no cluster attribute is selected or it's 'None'
    if cluster_attribute == 'None':
        # If gender filter is on, just stratify by gender
        if gender_filter and 'Gender' in dataset.columns:
            gender_counts = dataset.groupby('Gender').size()
            
            # Create figure with dark background
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            
            # Create bars for each gender
            gender_colors = ['#00bfff', '#ff69b4']  # Blue for male, pink for female
            bars = ax.bar(range(len(gender_counts)), gender_counts.values, 
                         color=gender_colors[:len(gender_counts)])
            
            # Add count labels on top of bars
            for i, v in enumerate(gender_counts.values):
                ax.text(i, v + 0.5, str(v), color='white', ha='center')
            
            # Customize the plot
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by Gender\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel('Gender', color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            # Set x-axis labels
            ax.set_xticks(range(len(gender_counts)))
            ax.set_xticklabels(gender_counts.index, color='white')
            
        else:
            # Just show total count
            total_count = len(dataset)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            
            # Create single bar
            bars = ax.bar([0], [total_count], color='#00bfff')
            
            # Add count label
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
    
    # If cluster attribute is selected
    else:
        # If gender filter is on, stratify by gender and cluster attribute
        if gender_filter and 'Gender' in dataset.columns:
            # Get top 5 values for the cluster attribute if more than 5 unique values
            top_values = dataset[cluster_attribute].value_counts().nlargest(5).index
            dataset_filtered = dataset[dataset[cluster_attribute].isin(top_values)]
            
            # Group by cluster attribute and gender
            grouped_data = dataset_filtered.groupby([cluster_attribute, 'Gender']).size().unstack(fill_value=0)
            
            # Create figure with dark background
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            
            # Set up bar positions
            x = np.arange(len(grouped_data.index))
            width = 0.35
            
            # Create bars for each gender
            gender_colors = ['#00bfff', '#ff69b4']  # Blue for male, pink for female
            for i, gender in enumerate(grouped_data.columns):
                if i < len(gender_colors):  # Ensure we don't exceed our color list
                    bars = ax.bar(x + i*width, grouped_data[gender], width, 
                                label=gender, color=gender_colors[i])
                    
                    # Add count labels on top of bars
                    for j, v in enumerate(grouped_data[gender]):
                        if v > 0:  # Only show label if value is greater than 0
                            ax.text(x[j] + i*width, v + 0.5, str(v), 
                                    color='white', ha='center', fontsize=9)
            
            # Customize the plot
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by {cluster_attribute} and Gender\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel(cluster_attribute, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            # Set x-axis labels
            ax.set_xticks(x + width/2 if len(grouped_data.columns) > 1 else x)
            ax.set_xticklabels(grouped_data.index, color='white', rotation=45, ha='right')
            
            # Add legend
            ax.legend(facecolor='#1a1a1a', edgecolor='white', labelcolor='white')
            
        else:
            # If gender filter is off, just group by cluster attribute
            # Get top values for the cluster attribute
            cluster_counts = dataset[cluster_attribute].value_counts().nlargest(5)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 7))
            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            
            # Create bars
            bars = ax.bar(range(len(cluster_counts)), cluster_counts.values, color='#00bfff')
            
            # Add count labels on top of bars
            for i, v in enumerate(cluster_counts.values):
                ax.text(i, v + 0.5, str(v), color='white', ha='center')
            
            # Customize the plot
            source_text = f"Source: {source}" if source != 'All Sources' else "All Sources"
            country_text = f", Country: {country}" if country != 'All Countries' else ""
            ax.set_title(f'Isolation Burden Analysis by {cluster_attribute}\n{source_text}{country_text}', 
                        color='white', pad=20, fontsize=14)
            ax.set_xlabel(cluster_attribute, color='white', fontsize=12)
            ax.set_ylabel('Count', color='white', fontsize=12)
            
            # Set x-axis labels
            ax.set_xticks(range(len(cluster_counts)))
            ax.set_xticklabels(cluster_counts.index, color='white', rotation=45, ha='right')
    
    # Common styling for all plots
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, linestyle='--', alpha=0.3, color='white', axis='y')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()
    return fig

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
    if granularity == 'yearly':
        years = valid_data.index.tolist()
        resistant_rates = valid_data['Resistance Rate'].tolist()

    elif granularity == 'monthly':
        res = valid_data.index.tolist()
        years = [f'{r[0]}-{r[1]}' for r in res]
        resistant_rates = valid_data['Resistance Rate'].tolist()

    elif granularity == 'daily':
        res = valid_data.index.tolist()
        years = [f'{r[0]}-{r[1]}-{r[2]}' for r in res]
        resistant_rates = valid_data['Resistance Rate'].tolist()

    # Create figure with dark background
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    # Set dark background
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    
    # Plot line and fill
    line = ax.plot(years, resistant_rates, marker='o', linestyle='-', color='#00bfff', linewidth=2, markersize=8)
    ax.fill_between(years, resistant_rates, color='#00bfff', alpha=0.2)
    
    # Customize grid
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    
    # Customize spines
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    
    # Customize ticks
    ax.tick_params(colors='white')
    
    # Set labels and title with white color
    plt.title(f'Resistance Rate Over Time\n{infection} - {antibiotic_column} - {source}', 
              color='white', pad=20, fontsize=14)
    plt.xlabel('Year', color='white', fontsize=12)
    plt.ylabel('Resistance Rate (%)', color='white', fontsize=12)
    
    # Add percentage to y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1f}%'.format(y)))
    
    # Adjust layout
    plt.tight_layout()

    return fig
    
def scorecard_analysis(dataset, source, infection, antibiotic):
    scorecard_dataset = dataset.sort_values(by='Year')
    scorecard_dataset = scorecard_dataset[(scorecard_dataset[mappings['source_input']] == source) & (scorecard_dataset[mappings['bacterial_infection']] == infection)]
    valid_values = ['Resistant', 'Intermediate', 'Susceptible']
    