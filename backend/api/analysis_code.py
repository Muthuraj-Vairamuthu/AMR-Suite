import matplotlib.pyplot as plt

def isolation_burden_analysis_graph(dataset, source, attribute, mappings):
    isolation_dataset = dataset[dataset[mappings['source_input']] == source]
    isolation_dataset = isolation_dataset[attribute].value_counts().sort_values(ascending=False).to_dict()

    if len(isolation_dataset) > 15:
        isolation_dataset = dict(list(isolation_dataset.items())[:15])
    x_axis = list(isolation_dataset.keys())
    counts = list(isolation_dataset.values())

    # Create figure with dark background
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    # Set dark background
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    
    # Create bars
    bars = plt.bar(x_axis, counts, color='#00bfff')
    
    # Customize the plot
    plt.title(f'Isolation Burden Analysis for {source}', color='white', pad=20, fontsize=14)
    plt.xlabel(attribute, color='white', fontsize=12)
    plt.ylabel('Count', color='white', fontsize=12)
    
    # Rotate x-axis labels
    plt.xticks(rotation=90, ha='center', color='white')
    plt.yticks(color='white')
    
    # Customize grid and spines
    ax.grid(True, linestyle='--', alpha=0.3, color='white', axis='y')
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    
    # Add padding at the bottom for the rotated labels
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
    