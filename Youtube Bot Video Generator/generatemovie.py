from moviepy.editor import *
import settings
import soundfile as sf
import pickle
from pydub import AudioSegment
from pymediainfo import MediaInfo
from time import sleep
from copy import deepcopy
import gc


class Movie():
    def __init__(self, videoformat, content, authorpostups, scriptno):
        self.videoformat = videoformat
        self.content = content
        self.scriptno = scriptno
        self.clips = []
        self.index = 0
        self.background_music_name = None
        self.title = authorpostups
        self.imageframes = []
        self.audiofiles = []
        self.durations = []
        self.transitions = []

    def renderVideo(self):

        script = [[self.title[0], self.title[1]]]

        new_content = []
        new_content.append([self.title[0], self.title[1]])
        for con in self.content:
            new_content.append(con)

        for i, subcontent in enumerate(new_content):
            if type(subcontent) is tuple:
                for comment in subcontent:
                    author = comment.author
                    text = comment.text

                    script.append([author, text])

        clips = self.videoformat.renderClips(self.content, self.title)
        self.videoformat.createMovie(clips, self)
        self.background_music_name = self.videoformat.music

        clips = []
        for i, transition in enumerate(self.transitions):
            print("Putting together clip (%s/%s)" % (i + 1, len(self.transitions)))
            transition_file_name = transition[0]
            last_image_index = transition[1]
            transition_duration = transition[2]
            if i == 0:
                clip = ImageSequenceClip(self.imageframes[0:last_image_index + 1], durations=self.durations[0:last_image_index + 1])
                combined_sounds = sum(self.audiofiles[0:last_image_index + 1])
                audio_name = "%s/%s%s.wav" % (settings.tempPath, "atestaudio", i)
                combined_sounds.export(audio_name, format="wav")
                video_clip = VideoFileClip(transition_file_name).fx(afx.volumex, settings.voice_volume)
                audio_clip = AudioFileClip(audio_name)
                clip = clip.set_audio(audio_clip)
                clip_with_interval = concatenate_videoclips([clip, video_clip])
                clips.append(clip_with_interval)

            else:
                prev_image_index = self.transitions[i-1][1]
                clip = ImageSequenceClip(self.imageframes[prev_image_index + 1:last_image_index + 1], durations=self.durations[prev_image_index + 1:last_image_index + 1])
                combined_sounds = sum(self.audiofiles[prev_image_index + 1:last_image_index + 1])
                audio_name = "%s/%s%s.wav" % (settings.tempPath, "atestaudio", i)
                combined_sounds.export(audio_name, format="wav")
                video_clip = VideoFileClip(transition_file_name).fx(afx.volumex, settings.voice_volume)
                audio_clip = AudioFileClip(audio_name)
                clip = clip.set_audio(audio_clip)
                clip_with_interval = concatenate_videoclips([clip, video_clip])
                clips.append(clip_with_interval)

        main_vid_duration = 0
        for i in range(1, len(clips), 1):
            main_vid_duration += clips[i].duration

        print("Generating Audio Loop (%s) " % main_vid_duration)
        print("Using Audio Loop %s" % self.background_music_name)
        music_loop = afx.audio_loop(AudioFileClip(self.background_music_name).fx(afx.volumex, settings.background_music_volume),
                                    duration=int(main_vid_duration))
        music_loop.to_audiofile("%s/music-loop.wav" % settings.tempPath)
        pause_time = int(clips[0].duration * 1000)
        print("Adding pause to start of Audio Loop (%s) " % (pause_time / 1000))
        audio_clip = AudioSegment.from_wav("%s/music-loop.wav" % settings.tempPath)
        new_audio = AudioSegment.silent(duration=(pause_time)) + audio_clip
        new_audio.export("%s/music-loop2.wav" % settings.tempPath, format='wav')

        # here we are combining the first clip with the last
        print("Combining all Video Clips %s" % (pause_time / 1000))
        if os.path.exists("%s/Intervals/outro.mp4" % settings.assetPath):
            clips.append(VideoFileClip("%s/Intervals/outro.mp4" % settings.assetPath))
            print("Adding outro")
        main_vid_combined = concatenate_videoclips(clips)
        main_vid_with_audio = main_vid_combined.set_audio(CompositeAudioClip([main_vid_combined.audio, AudioFileClip("%s/music-loop2.wav" % settings.tempPath)]))

        folder_location = settings.finishedvideosdirectory + "/vid%s" % self.scriptno
        if not os.path.exists(folder_location):
            os.makedirs(folder_location)
        print("Writing video to location %s" % folder_location)
        main_vid_with_audio.write_videofile("%s/%s.mp4" % (folder_location, "vid%s" % self.scriptno), threads=4,
                                            fps=settings.movieFPS, temp_audiofile="%s/%s.mp3" % (folder_location, "audio%s" % self.scriptno), remove_temp=False)

        sleep(5)
        #os.system(f"ffmpeg -y -i \"{'%s/%s.mp4' % (folder_location, 'vid%s' % self.scriptno)}\" -i \"{'%s/%s.mp3' % (folder_location, 'audio%s' % self.scriptno)}\" -c:v copy -c:a aac \"{'%s/%s.mp4' % (folder_location, 'vidfixedaudio%s' % self.scriptno)}\"")

        try:
            f= open(f"{folder_location}/script.txt","w+")
            f.write(script[0][1] + "\n" + script[0][1] + "\n\n")

            for i in range(1, len(script), 1):
                try:
                    f.write(script[i][0] + "\n" + script[i][1] + "\n\n")
                except Exception as e:
                    pass
            f.close()
        except Exception as e:
            pass

        return folder_location


    def closeReader(self, target):
        target.reader.close()

    def addFrame(self, image_file, audio_file):
        audio_file = audio_file.replace("\\", "/")
        try:
            audio_clip = AudioSegment.from_wav(r"%s"%audio_file)
            f = sf.SoundFile(r"%s"%audio_file)
        except Exception as e:
            print(e)
            audio_clip = AudioSegment.from_wav("%s/pause.wav" % settings.assetPath)
            f = sf.SoundFile("%s/pause.wav" % settings.assetPath)

        duration = len(f) / f.samplerate
        self.imageframes.append(image_file)
        self.audiofiles.append(audio_clip)
        self.durations.append(duration)

    def addFrameWithPause(self, image_file, audio_file, pause):
        audio_file = audio_file.replace("\\", "/")
        f = sf.SoundFile(audio_file)
        audio_clip = AudioSegment.from_wav(audio_file)
        duration = (len(f) / f.samplerate) + pause / 1000
        audio_clip_with_pause = audio_clip + AudioSegment.silent(duration=pause)
        self.imageframes.append(image_file)
        self.audiofiles.append(audio_clip_with_pause)
        self.durations.append(duration)


    def addFrameWithTransition(self, image_file, audio_file, transition_file):
        media_info = MediaInfo.parse(transition_file)
        duration_in_ms = media_info.tracks[0].duration
        audio_file = audio_file.replace("\\", "/")
        try:
            audio_clip = AudioSegment.from_wav(r"%s"%audio_file)
            f = sf.SoundFile(r"%s"%audio_file)
        except Exception as e:
            print(e)
            audio_clip = AudioSegment.from_wav("%s/pause.wav" % settings.assetPath)
            f = sf.SoundFile("%s/pause.wav" % settings.assetPath)
        duration = (len(f) / f.samplerate)
        audio_clip_with_pause = audio_clip
        self.imageframes.append(image_file)
        self.audiofiles.append(audio_clip_with_pause)
        self.durations.append(duration)
        self.transitions.append((transition_file, len(self.imageframes) - 1, duration_in_ms / 1000))

    def addFrameWithTransitionAndPause(self, image_file, audio_file, transition_file, pause):
        media_info = MediaInfo.parse(transition_file)
        duration_in_ms = media_info.tracks[0].duration
        audio_file = r"%s"%audio_file
        f = sf.SoundFile(audio_file)
        try:
            audio_clip = AudioSegment.from_wav(audio_file)
        except:
            print("error with frame audio transition pause for %s" % audio_file)
            audio_clip = AudioSegment.silent(duration=pause)
        duration = (len(f) / f.samplerate)
        audio_clip_with_pause = audio_clip
        self.imageframes.append(image_file)
        self.audiofiles.append(audio_clip_with_pause)
        self.durations.append(duration + (pause/1000))
        self.transitions.append((transition_file, len(self.imageframes) - 1, (duration_in_ms / 1000) + (pause/1000)))


    def exportMovie(self, name):

        main_vid = concatenate_videoclips(self.clips[2:], method="compose")
        music_loop = afx.audio_loop(AudioFileClip(self.background_music_name).fx(afx.volumex, 0.2), duration=int(main_vid.duration))
        video_with_audio = main_vid.set_audio(CompositeAudioClip([main_vid.audio, music_loop]))


        # here we are combining the first clip with the last
        main_vid_combined = concatenate_videoclips([self.clips[0], self.clips[1], video_with_audio])
        main_vid_combined.write_videofile("%s/%s.mp4" % (settings.exportPath, name), fps=settings.movieFPS)
