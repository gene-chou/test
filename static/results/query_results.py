import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

def determine_generation_type(video_path):
    if 'luma_generations' in video_path:
        return 'luma'
    elif 'vid-only_generations' in video_path:
        return 'vid-only'
    elif 'ours_generations' in video_path:
        return 'ours'
    return None

def determine_dataset(video_path):
    return 'pt' if video_path.startswith('pt/') else 're10k'

def normalize_comparison(type1, type2, value):
    """
    Normalize the comparison to always be 'other_vs_ours' and adjust the vote value accordingly
    Returns: (normalized_comparison, adjusted_value)
    """
    if type2 == 'ours':
        return f'{type1}_vs_ours', value
    else:
        new_value = value if value == 2 else (1 - value)
        return f'{type2}_vs_ours', new_value

def analyze_preferences(votes_path, scenes_path):
    # Read JSON files
    with open(votes_path) as f:
        votes_data = json.load(f)
    with open(scenes_path) as f:
        scenes_data = json.load(f)
    
    # Convert scenes data to dictionary for easier lookup
    scenes_dict = {scene['id']: scene for scene in scenes_data}
    
    # Initialize results storage with multi-index for split votes
    results = []
    
    # Process each vote
    for vote in votes_data:
        scene_id = vote['vote_data']['comparisonId']
        if scene_id not in scenes_dict:
            continue
            
        scene = scenes_dict[scene_id]
        videos = scene['videos']
        dataset = determine_dataset(videos[0])
        
        # Determine generation types
        first_type = determine_generation_type(videos[0])
        second_type = determine_generation_type(videos[1])
        
        # Process votes for each criterion
        for criterion, value in vote['vote_data']['votes'].items():
            # Normalize the comparison and adjust the value
            comparison, adjusted_value = normalize_comparison(first_type, second_type, value)
            
            if adjusted_value == 2:  # Equal preference
                # Add 0.5 votes to each method
                results.append({
                    'dataset': dataset,
                    'comparison': comparison,
                    'criterion': criterion,
                    'winner': 'baseline',
                    'weight': 0.5,
                    'scene_id': scene_id
                })
                results.append({
                    'dataset': dataset,
                    'comparison': comparison,
                    'criterion': criterion,
                    'winner': 'ours',
                    'weight': 0.5,
                    'scene_id': scene_id
                })
            else:
                # For clear preferences, add 1 vote to the winner
                winner = 'ours' if adjusted_value == 1 else 'baseline'
                results.append({
                    'dataset': dataset,
                    'comparison': comparison,
                    'criterion': criterion,
                    'winner': winner,
                    'weight': 1.0,
                    'scene_id': scene_id
                })
    
    return pd.DataFrame(results)

def generate_statistics(df):
    # Group by relevant columns and sum the weights
    stats = df.groupby(['dataset', 'comparison', 'criterion', 'winner'])['weight'].sum().reset_index()
    
    # Calculate percentages
    total_votes = stats.groupby(['dataset', 'comparison', 'criterion'])['weight'].sum().reset_index()
    stats = stats.merge(total_votes, on=['dataset', 'comparison', 'criterion'], suffixes=('', '_total'))
    stats['percentage'] = (stats['weight'] / stats['weight_total'] * 100).round(2)
    
    # Pivot table for easier visualization
    pivot_stats = {}
    for dataset in df['dataset'].unique():
        for comparison in df['comparison'].unique():
            filtered = stats[
                (stats['dataset'] == dataset) & 
                (stats['comparison'] == comparison)
            ]
            if len(filtered) > 0:
                key = f"{dataset}_{comparison}"
                votes_pivot = filtered.pivot(
                    index='criterion',
                    columns='winner',
                    values=['weight', 'percentage']
                ).fillna(0)
                pivot_stats[key] = votes_pivot
    
    return pivot_stats

def create_visualizations(df):
    # Create a figure with subplots for each dataset and criterion
    datasets = sorted(df['dataset'].unique())
    criteria = sorted(df['criterion'].unique())
    
    fig, axes = plt.subplots(len(datasets), len(criteria), 
                            figsize=(15, 10), 
                            squeeze=False)
    
    for i, dataset in enumerate(datasets):
        for j, criterion in enumerate(criteria):
            data = df[
                (df['dataset'] == dataset) & 
                (df['criterion'] == criterion)
            ]
            
            # Sum weights and calculate percentages
            pivot_data = data.groupby(['comparison', 'winner'])['weight'].sum().unstack()
            pivot_data = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
            
            pivot_data.plot(
                kind='bar',
                stacked=True,
                ax=axes[i][j],
                colormap='viridis'
            )
            
            axes[i][j].set_title(f'{dataset} - {criterion}')
            axes[i][j].set_xlabel('')
            axes[i][j].set_ylabel('Percentage')
            axes[i][j].legend(title='Winner')
            plt.setp(axes[i][j].get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig

def main(votes_path, scenes_path):
    # Perform analysis
    df = analyze_preferences(votes_path, scenes_path)
    
    # Generate statistics
    stats = generate_statistics(df)
    
    # Print numerical results
    print("\nNumerical Results:")
    print("=================")
    for key, pivot_table in stats.items():
        print(f"\n{key}:")
        print(pivot_table)
    
    # Create and save visualization
    fig = create_visualizations(df)
    plt.savefig('preference_analysis.png', bbox_inches='tight', dpi=300)
    plt.close()
    
    return df, stats

# Usage example:
df, stats = main('votes.json', 'final_pairs.json')