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

def resistance_analysis_graph(dataset, source, infection, antibiotic, mappings):
    resistant_dataset = dataset.sort_values(by='Year')
    resistant_dataset = resistant_dataset[(resistant_dataset[mappings['source_input']] == source) & (resistant_dataset[mappings['bacterial_infection']] == infection)]

    antibiotic_data = {}

    for index, row in dataset.iterrows():
        year = row['Year']
        if year not in antibiotic_data:
            antibiotic_data[year] = {'Resistant':0, 'Intermediate':0, 'Susceptible':0}
        
        if row[antibiotic] == 'Resistant':
            antibiotic_data[year]['Resistant'] += 1
        elif row[antibiotic] == 'Intermediate':
            antibiotic_data[year]['Intermediate'] += 1
        else:
            antibiotic_data[year]['Susceptible'] += 1

    years = sorted(antibiotic_data.keys())
    resistant_rates = []
    valid_years = []
    
    # Only include points where there is data
    for year in years:
        total = sum(antibiotic_data[year].values())
        if total > 0:
            rate = (antibiotic_data[year]['Resistant'] / total) * 100
            resistant_rates.append(rate)
            valid_years.append(year)

    # Create figure with dark background
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    # Set dark background
    ax.set_facecolor('#1a1a1a')
    fig.patch.set_facecolor('#1a1a1a')
    
    # Plot line and fill
    line = ax.plot(valid_years, resistant_rates, marker='o', linestyle='-', color='#00bfff', linewidth=2, markersize=8)
    ax.fill_between(valid_years, resistant_rates, color='#00bfff', alpha=0.2)
    
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
    plt.title(f'Resistance Rate Over Time\n{infection} - {antibiotic} - {source}', 
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
    