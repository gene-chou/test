import json
import random

def shuffle_and_renumber_scenes(input_json_path, output_json_path):
    """
    Read a JSON file containing scene data, randomly shuffle the order,
    and update scene IDs and titles to reflect the new order.
    
    Args:
        input_json_path (str): Path to input JSON file
        output_json_path (str): Path where the shuffled JSON will be saved
    """
    # Read the original JSON file
    with open(input_json_path, 'r') as f:
        scenes = json.load(f)
    
    # Store original order for reporting
    original_order = [scene['id'] for scene in scenes]
    
    # Shuffle the scenes
    #random.shuffle(scenes)
    
    # Update IDs and titles
    for i, scene in enumerate(scenes, 1):
        scene['id'] = f'scene{i}'
        scene['title'] = f'Scene {i}'
    
    # Save the shuffled and renumbered JSON
    with open(output_json_path, 'w') as f:
        json.dump(scenes, f, indent=2)
    
    # Print summary
    print("Shuffle and Renumber Summary")
    print("===========================")
    print("\nOriginal order:", ', '.join(original_order))
    print("\nNew order:", ', '.join(scene['id'] for scene in scenes))
    print(f"\nShuffled and renumbered JSON saved to: {output_json_path}")

# Example usage
if __name__ == "__main__":
    input_path = "final_pairs.json"  # Update this path
    output_path = "final_pairs.json"  # Update this path
    shuffle_and_renumber_scenes(input_path, output_path)