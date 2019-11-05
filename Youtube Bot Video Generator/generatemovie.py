from moviepy.editor import *
import settings
import soundfile as sf
import pickle
from pydub import AudioSegment
from pymediainfo import MediaInfo
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
                video_clip = VideoFileClip(transition_file_name).fx(afx.volumex, 0.2)
                audio_clip = AudioFileClip(audio_name)
                clip = clip.set_audio(audio_clip)
                clip_with_interval = concatenate_videoclips([clip, video_clip])
                clips.append(clip_with_interval)
                #self.closeReader(video_clip)

            else:
                prev_image_index = self.transitions[i-1][1]
                clip = ImageSequenceClip(self.imageframes[prev_image_index + 1:last_image_index + 1], durations=self.durations[prev_image_index + 1:last_image_index + 1])
                combined_sounds = sum(self.audiofiles[prev_image_index + 1:last_image_index + 1])
                audio_name = "%s/%s%s.wav" % (settings.tempPath, "atestaudio", i)
                combined_sounds.export(audio_name, format="wav")
                video_clip = VideoFileClip(transition_file_name).fx(afx.volumex, 0.2)
                audio_clip = AudioFileClip(audio_name)
                clip = clip.set_audio(audio_clip)
                clip_with_interval = concatenate_videoclips([clip, video_clip])
                clips.append(clip_with_interval)
                #self.closeReader(video_clip)

        #gc.collect()
        main_vid_duration = 0
        for i in range(1, len(clips), 1):
            main_vid_duration += clips[i].duration

        print("Generating Audio Loop (%s) " % main_vid_duration)
        print("Using Audio Loop %s" % self.background_music_name)
        music_loop = afx.audio_loop(AudioFileClip(self.background_music_name).fx(afx.volumex, 0.2),
                                    duration=int(main_vid_duration))
        music_loop.to_audiofile("%s/music-loop.wav" % settings.tempPath)
        #del music_loop
        #gc.collect()
        pause_time = int(clips[0].duration * 1000)
        print("Adding pause to start of Audio Loop (%s) " % (pause_time / 1000))
        audio_clip = AudioSegment.from_wav("%s/music-loop.wav" % settings.tempPath)
        new_audio = AudioSegment.silent(duration=(pause_time)) + audio_clip
        new_audio.export("%s/music-loop2.wav" % settings.tempPath, format='wav')
        #del new_audio
        #gc.collect()
        #video_with_audio = main_vid.set_audio(CompositeAudioClip([main_vid.audio, music_loop]))

        # here we are combining the first clip with the last
        print("Combining all Video Clips %s" % (pause_time / 1000))
        main_vid_combined = concatenate_videoclips(clips)
        #del clips
        #gc.collect()
        main_vid_with_audio = main_vid_combined.set_audio(CompositeAudioClip([main_vid_combined.audio, AudioFileClip("%s/music-loop2.wav" % settings.tempPath)]))
        #del main_vid_combined
        #gc.collect()

        folder_location = settings.finishedvideosdirectory + "/vid%s" % self.scriptno
        if not os.path.exists(folder_location):
            os.makedirs(folder_location)
        print("Writing video to location %s" % folder_location)
        main_vid_with_audio.write_videofile("%s/%s.mp4" % (folder_location, "vid%s" % self.scriptno), threads=4,
                                            fps=settings.movieFPS, temp_audiofile=settings.currentPath + "\\temp.mp3")
        return folder_location


    def closeReader(self, target):
        target.reader.close()
        #if target.audio and target.audio.reader:
        #    target.audio.reader.close_proc()

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
        """
        self.clips[0] will always be the title clip
        We want to add the audio loop to all of the clips apart from the first one
        """
        main_vid = concatenate_videoclips(self.clips[2:], method="compose")
        music_loop = afx.audio_loop(AudioFileClip(self.background_music_name).fx(afx.volumex, 0.2), duration=int(main_vid.duration))
        video_with_audio = main_vid.set_audio(CompositeAudioClip([main_vid.audio, music_loop]))


        # here we are combining the first clip with the last
        main_vid_combined = concatenate_videoclips([self.clips[0], self.clips[1], video_with_audio])
        main_vid_combined.write_videofile("%s/%s.mp4" % (settings.exportPath, name), fps=settings.movieFPS)
        """
        print(self.clips[0].duration)
        raw_video = concatenate_videoclips(self.clips, method="compose")
        music_loop = afx.audio_loop(AudioFileClip("%s/Music/%s"%(settings.assetPath, self.background_music_name)), duration=int(raw_video.duration))
        music_loop = music_loop
        video_with_audio = raw_video.set_audio(CompositeAudioClip([raw_video.audio, music_loop]))

        video_with_audio.write_videofile("%s/%s.mp4" % (settings.exportPath, name), fps=settings.movieFPS)
        """
