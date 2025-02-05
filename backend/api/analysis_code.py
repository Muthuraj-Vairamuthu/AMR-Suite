import matplotlib.pyplot as plt

def isolation_burden_analysis_graph(dataset, source, infection, antibiotic, mappings):
    dataset.sort_values(by='Year', inplace=True)
    dataset = dataset[(dataset[mappings['source_input']] == source) & (dataset[mappings['bacterial_infection']] == infection)]

    antibiotic_data = {}

    for index, row in dataset.iterrows():
        year = row['Year']
        if year not in antibiotic_data:
            antibiotic_data[year] = {'Resistant':0, 'Intermediate':0, 'Susceptible':0}
        else:
            if row[antibiotic] == 'Resistant':
                antibiotic_data[year]['Resistant'] += 1
            elif row[antibiotic] == 'Intermediate':
                antibiotic_data[year]['Intermediate'] += 1
            else:
                antibiotic_data[year]['Susceptible'] += 1

    years = sorted(antibiotic_data.keys())
    resistant_rates = [antibiotic_data[year]['Resistant'] / sum(antibiotic_data[year].values()) * 100 if sum(antibiotic_data[year].values()) > 0 else 0 for year in years]

    fig = plt.figure(figsize=(10, 5))
    plt.plot(years, resistant_rates, marker='o', linestyle='-', color='b')
    plt.title('Resistant Rate Over Time')
    plt.xlabel('Year')
    plt.ylabel('Resistant Rate')
    plt.grid(True)

    return fig

    