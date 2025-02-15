import matplotlib.pyplot as plt

def isolation_burden_analysis_graph(dataset, source, attribute, mappings):
    print(source, attribute, mappings)
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
    resistant_dataset['Year'] = resistant_dataset[mappings['time_stamp']].astype(int)
    resistant_dataset = resistant_dataset.sort_values(by='Year')
    
    # Group by year and count resistance statuses
    antibiotic_data = resistant_dataset.groupby('Year')[antibiotic_column].value_counts().unstack(fill_value=0)
    
    # Calculate resistance rate
    if 'Resistant' in antibiotic_data.columns:
        antibiotic_data['Total'] = antibiotic_data.sum(axis=1)
        antibiotic_data['Resistance Rate'] = (antibiotic_data['Resistant'] / antibiotic_data['Total']) * 100
    else:
        antibiotic_data['Resistance Rate'] = 0.0
    
    # Filter valid years with data
    valid_data = antibiotic_data[antibiotic_data['Total'] > 0]
    years = valid_data.index.tolist()
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
    