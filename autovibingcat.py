import argparse
from youtubesearchpython import VideosSearch
from pytube import YouTube
from pathlib import Path
import cv2
import os
import numpy as np
import ffmpeg
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import bpm_detection

## GLOBAL VARIABLES
tmp_output_path = str(Path(__file__).parent / "temp_output")
provisional_path = os.path.join(tmp_output_path, "provisional.mp4")
bpm_video_path = os.path.join(tmp_output_path, "bpm_prov_video.mp4")
bpm_audio_path = os.path.join(tmp_output_path, "bpm_prov_audio.wav")
tempo_mod_path = os.path.join(tmp_output_path, "vibingCat_tempo_mod.mp4")
tempo_mod_fps_path = os.path.join(tmp_output_path, "vibingCat_tempo_mod_fps.mp4")
original_mv_path = os.path.join(tmp_output_path, "original_music_video.mp4")
output_path = os.path.join(tmp_output_path, "output.mp4")

class VideoAttributes:
    def __init__(self, video: cv2.VideoCapture):
        self.frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = video.get(cv2.CAP_PROP_FPS)
        self.width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

def get_youtube_video(song_title: str):
    videosSearch = VideosSearch(song_title, limit = 5)

    results = videosSearch.result()
    video_link = results['result'][0]['link']

    print('Downloading ' + video_link + '...')

    yt = YouTube(video_link)
    yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=tmp_output_path, filename="original_music_video")

    print(results['result'][0]['title'] + ' saved as original_music_video.mp4')
    print('\n')

def modify_cat_bpm(music_video_start_time: int, vibing_cat_video_length: int):
    print('Computing audio bpm...')
    ffmpeg_extract_subclip(original_mv_path, music_video_start_time, music_video_start_time + vibing_cat_video_length, targetname=bpm_video_path)

    cut_video = VideoFileClip(bpm_video_path)
    audioclip = cut_video.audio
    audioclip.write_audiofile(bpm_audio_path)

    bpm = bpm_detection.main(bpm_audio_path, 3)

    print('Song approximated bpm is: ' + str(bpm))

    print('Modify vibing cat tempo...')
    vibing_cat_bpm = 120
    new_time = vibing_cat_bpm*vibing_cat_video_length/bpm
    time_factor = new_time/vibing_cat_video_length

    ffmpeg.input("vibingCat-green-key.mp4").setpts(str(time_factor)+'*PTS').output(tempo_mod_path).run(overwrite_output=True)

def edit_cat_video(start_time: int):
    music_video = cv2.VideoCapture(original_mv_path)
    mv_attributes = VideoAttributes(music_video)

    ffmpeg.input(tempo_mod_path).filter('fps', fps=mv_attributes.fps, round='up').output(tempo_mod_fps_path).run(overwrite_output=True)

    cat_video = cv2.VideoCapture(tempo_mod_fps_path)
    cat_attributes = VideoAttributes(cat_video)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    prov_video = cv2.VideoWriter(provisional_path, fourcc, mv_attributes.fps,(int(mv_attributes.width), int(mv_attributes.height)))

    start_frame = int(start_time * mv_attributes.fps)
    end_frame = int(start_frame + cat_attributes.frames)

    music_video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    for frameCount in range(int(cat_attributes.frames)):
        print(frameCount)
        ret, frame = cat_video.read()
        ret_cry, frame_cry = music_video.read()

        frame = cv2.resize(frame, (int(mv_attributes.width), int(mv_attributes.height)))

        #[43, 215, 28]
        u_green = np.array([150, 255, 120]) 
        l_green = np.array([0, 150, 0]) 

        mask = cv2.inRange(frame, l_green, u_green) 
        res = cv2.bitwise_and(frame, frame, mask = mask)

        f = frame - res 
        f = np.where(f == 0, frame_cry, f)

        cv2.imshow("video", frame)
        cv2.imshow("mask", f)   

        prov_video.write(f)

        cv2.waitKey(20)
        cv2.destroyAllWindows()

    cat_video.release()
    music_video.release()

    prov_video.release()

    return mv_attributes, cat_attributes

def add_audio_to_video(start_time: int, end_time: float):
    prov_video = VideoFileClip(provisional_path)
    music_video = VideoFileClip(original_mv_path)

    clip_music_video = music_video.subclip(start_time, end_time)
    audioclip = clip_music_video.audio

    prov_video.audio = audioclip
    prov_video.write_videofile(output_path)


def create_vibing_cat(song_title:str, start_time: int):
    vibing_cat_video_length = 22

    get_youtube_video(song_title)

    modify_cat_bpm(start_time, vibing_cat_video_length)

    _, cat_attributes = edit_cat_video(start_time)

    end_time = start_time + (cat_attributes.frames/cat_attributes.fps)

    add_audio_to_video(start_time, end_time)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .wav file to determine the Beats Per Minute.")
    parser.add_argument("--title", required=True, help="Song title that want to be used.")
    parser.add_argument(
        "--start",
        type=int,
        default=60,
        help="Second of the song where will start the cat video.",
    )

    args = parser.parse_args()
    
    create_vibing_cat(args.title, args.start)

    print("Done! Your video has been saved in: " + output_path)