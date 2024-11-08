import json

def update_video_paths(data):
    updated_scenes = []
    
    for scene in data:
        # Check if 'luma_generations' is in any of the video paths; skip if not
        if not any("luma_generations" in video for video in scene["videos"]):
            continue
        
        # Find paths for pt/re10k and luma_generations to create the new entries
        luma_path = next(video for video in scene["videos"] if "luma_generations" in video)
        ours_path = next(video for video in scene["videos"] if "ours_generations" in video)
        
        # Extract prefix for pt or re10k
        prefix = luma_path.split('/')[0]

        # Construct new video paths
        flavr_path = f"{prefix}/flavr/{'/'.join(luma_path.split('/')[2:-1])}/result.mp4"
        ldmvfi_path = f"{prefix}/ldmvfi/{'/'.join(luma_path.split('/')[2:-1])}/ref_imgs_512x512_4fps_LDMVFI.mp4"
        film_path = f"{prefix}/film/{'/'.join(luma_path.split('/')[2:-1])}/interpolated.mp4"
        vid_only_path = ours_path.replace("ours_generations", "vid-only_generations")
        
        # Update scene videos list to have 6 entries
        scene["videos"] = [
            flavr_path,
            ldmvfi_path,
            film_path,
            vid_only_path,
            luma_path,
            ours_path
        ]
        
        # Add the updated scene to the list
        updated_scenes.append(scene)
    
    return updated_scenes

# Load the input JSON file
with open("final_pairs.json", "r") as file:
    data = json.load(file)

# Update the data
updated_data = update_video_paths(data)

# Save the updated JSON data to a new file
with open("comparison_list.json", "w") as file:
    json.dump(updated_data, file, indent=2)
