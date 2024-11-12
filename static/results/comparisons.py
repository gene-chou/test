import cv2
import numpy as np
from moviepy.editor import VideoFileClip, clips_array, TextClip, CompositeVideoClip, ColorClip
import json
from pathlib import Path

class VideoComparison:
    def __init__(self, output_path="output.mp4", pause_duration=0.5):
        self.output_path = output_path
        self.pause_duration = pause_duration
        self.titles = ["FLAVR", "LDMVFI", "FILM", "Video-Only", "LUMA", "Ours"]
        
    def add_border(self, frame, color):
        """Add colored border to frame"""
        border_size = 8
        h, w = frame.shape[:2]
        result = frame.copy()
        
        if color == "green":
            border_color = (173, 255, 47)  # BGR for greenyellow (RGB: 173, 255, 47)
        else:  # red
            border_color = (255, 0, 0)
            
        cv2.rectangle(result, (0, 0), (w-1, h-1), border_color, border_size)
        return result

    def adjust_speed(self, clip, target_duration):
        current_duration = clip.duration
        speed_factor = current_duration / target_duration
        return clip.fl_time(lambda t: t * speed_factor).set_duration(target_duration)

    def process_scene(self, scene_data):
        print(f"Processing scene: {scene_data['title']}")
        
        # Load all videos and get target duration from 'Ours'
        video_clips = []
        target_duration = None
        ours_index = self.titles.index("Ours")
        
        for video_path in scene_data['videos']:
            video_path = video_path.replace('static/results/', '')
            clip = VideoFileClip(video_path)
            video_clips.append(clip)
            
        # Get duration from 'Ours' video
        target_duration = video_clips[ours_index].duration
        print(f"Target duration from 'Ours': {target_duration}")
        
        # Process all clips
        processed_clips = []
        for idx, clip in enumerate(video_clips):
            print(f"Processing {self.titles[idx]} - Original duration: {clip.duration}")
            
            # Adjust speed to match target duration
            if idx != ours_index:
                processed_clip = self.adjust_speed(clip, target_duration)
            else:
                processed_clip = clip.set_duration(target_duration)
                
            print(f"{self.titles[idx]} - New duration: {processed_clip.duration}")
            
            # Add borders only for exact first and last frames
            def modify_frame(get_frame, t):
                frame = get_frame(t)
                if abs(t - 0) < 1/30:  # First frame (assuming 30fps)
                    frame = self.add_border(frame, "green")
                elif abs(t - target_duration) < 1/30:  # Last frame
                    frame = self.add_border(frame, "red")
                return frame
                
            processed_clip = processed_clip.fl(modify_frame)
            
            # Create title
            title = TextClip(
                self.titles[idx], 
                fontsize=24, 
                color='black',
                font='Arial-Bold',
                size=(processed_clip.w, 40),
                method='caption',
                align='center'
            ).set_duration(target_duration)
            
            # Add white background for title
            title_bg = ColorClip(
                (processed_clip.w, 40),
                col=(255, 255, 255)
            ).set_duration(target_duration)
            
            # Compose title
            title_final = CompositeVideoClip([title_bg, title]).set_duration(target_duration)
            
            # Add padding around video (light green container)
            padding = 4
            padding_clip = ColorClip(
                (processed_clip.w + 2*padding, processed_clip.h + 2*padding),
                col=(220, 240, 220)  # Very light green color for container
            ).set_duration(target_duration)
            
            # Compose video with padding
            processed_clip = CompositeVideoClip([
                padding_clip,
                processed_clip.set_position((padding, padding))
            ]).set_duration(target_duration)
            
            # Combine title and video
            final_clip = CompositeVideoClip([
                ColorClip(
                    (processed_clip.w, processed_clip.h + title_final.h + padding),
                    col=(255, 255, 255)
                ).set_duration(target_duration),
                title_final.set_position((0, 0)),
                processed_clip.set_position((0, title_final.h))
            ]).set_duration(target_duration)
            
            processed_clips.append(final_clip)
        
        # Arrange in 2x3 grid
        spacing = 10
        total_width = (processed_clips[0].w * 3) + (spacing * 2)
        total_height = (processed_clips[0].h * 2) + spacing
        
        background = ColorClip(
            (total_width, total_height),
            col=(255, 255, 255)
        ).set_duration(target_duration)
        
        positions = [
            (0, 0), (processed_clips[0].w + spacing, 0), (processed_clips[0].w * 2 + spacing * 2, 0),
            (0, processed_clips[0].h + spacing), (processed_clips[0].w + spacing, processed_clips[0].h + spacing),
            (processed_clips[0].w * 2 + spacing * 2, processed_clips[0].h + spacing)
        ]
        
        final_grid = CompositeVideoClip(
            [background] + 
            [clip.set_position(pos) for clip, pos in zip(processed_clips, positions)]
        ).set_duration(target_duration)
        
        return final_grid

    def process_json(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        for scene in data:
            output_path = f"output_{scene['id']}.mp4"
            final_clip = self.process_scene(scene)
            print(f"Writing video to {output_path}")
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio=False
            )
            
            # Clean up
            final_clip.close()

# Example usage
if __name__ == "__main__":
    processor = VideoComparison()
    processor.process_json("comparison_list.json")