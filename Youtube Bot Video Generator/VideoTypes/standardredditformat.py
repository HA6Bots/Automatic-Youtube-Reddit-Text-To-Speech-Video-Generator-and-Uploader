from PIL import ImageFont, ImageDraw, Image
import numpy as np
import settings
from copy import deepcopy
import cv2
from VideoTypes import videoformat, imageframe
import ast
import pickle
import random
from moviepy.editor import *
import sys

class StandardReddit(videoformat.VideoFormat):

    def __init__(self, savename, dictionary, musictype):
        self.scriptsaveidentifier = savename
        self.loadFormat(dictionary)
        self.musictype = musictype
        self.selectMusic(musictype)


    def stillImage(self, commentThread):
        commentThread = commentThread[0]
        fontSizeInfo = self.calculateFontSize(commentThread, self.settings.preferred_font_size)
        fontSizeD = fontSizeInfo[0]
        marginOffsetX = fontSizeInfo[1]
        marginOffsetY = fontSizeInfo[2]
        fontpath = ("%s/Verdana.ttf" % (settings.assetPath))
        font = ImageFont.truetype(fontpath, fontSizeD)

        font_header = ImageFont.truetype(fontpath, int(fontSizeD * self.settings.comment_author_factor))

        my_img = np.zeros((self.settings.imageSize[1], self.settings.imageSize[0], 3), dtype="uint8")
        my_img[:, :, :] = self.settings.background_color
        img_pil = Image.fromarray(my_img)
        draw = ImageDraw.Draw(img_pil, mode="RGBA")

        poffsetX = marginOffsetX
        poffsetY = marginOffsetY

        # script = imageframe.VideoScript(texttext)
        # script.insertLineWrappingTags()
        # print(script.inputString)

        if type(commentThread) == tuple:
            for comment in commentThread:
                author = comment.author
                upvotes = comment.upvotes
                script = imageframe.VideoScript(comment.text)
                script.insertLineWrappingTags()
                script.insertAudioBreakTags()
                instructions = script.getTags()
                lineWidth = 0
                lineHeight = 0

                lastText = ""
                currentline = ""
                draw.text((poffsetX + lineWidth, poffsetY + lineHeight), author, font=font_header,
                          fill=tuple(self.settings.author_details_color))
                tempXoffset = font_header.getsize(author)[0]
                draw.text((poffsetX + lineWidth + tempXoffset, poffsetY + lineHeight),
                          " %s" % imageframe.redditPointsFormat(upvotes), font=font_header,
                          fill=tuple(self.settings.author_text_color))
                poffsetY += font_header.getsize(author)[1]

                for instr in instructions:
                    text = ast.literal_eval(repr(instr[0]))
                    tag = instr[1]
                    draw.text((poffsetX + lineWidth, poffsetY + lineHeight), text, font=font,
                              fill=tuple(self.settings.comment_text_color))

                    if tag == "<LW>" or tag == "":
                        if not lastText == text:
                            if not text.replace(" ", "") == "":
                                lastText += text
                        currentline += text
                        currentline = ""
                        lineWidth = 0
                        poffsetY += (font.getsize("asd")[1])
                    else:
                        lineWidth = (font.getsize(text)[0])

                    if tag == "<BRK>" or tag == "":
                        if not lastText == text:
                            lastText += text
                        currentline += text
                        lineWidth = (font.getsize(currentline)[0])

                        lastText = ""
                tempWidth = font.getsize("1" * self.settings.reply_characters_factorX)[0]
                tempHeight = font.getsize("random")[1]
                poffsetY += (tempHeight * self.settings.reply_fontsize_factorY)
                poffsetX += (tempWidth * self.settings.reply_fontsize_factorX)

        my_img = deepcopy(np.array(img_pil))
        return my_img


    #1280 x 720 youtube max
    def renderThumbnail(self, commentThread):
        commentThread = commentThread[0]
        upvotes = commentThread[0].upvotes
        subcomments = commentThread[0].subcomments
        fontpath = ("%s/Verdana.ttf" % (settings.assetPath))
        fontpathbold = ("%s/verdanab.ttf" % (settings.assetPath))

        font_subreddit = ImageFont.truetype(fontpath, 80)
        font_below_icons = ImageFont.truetype(fontpathbold, 60)

        my_img = np.zeros((720, 1280, 3), dtype="uint8")
        my_img[:, :, :] = self.settings.background_color
        img_pil = Image.fromarray(my_img)
        draw = ImageDraw.Draw(img_pil, mode="RGBA")


        xPosLogo, yPosLogo = (30, 30)
        logowidth, logoheight = ((font_subreddit.getsize("test")[1]), (font_subreddit.getsize("test")[1]))
        upvoteiconwidth, upvoteiconheight = ((font_below_icons.getsize("test")[1]), (font_below_icons.getsize("test")[1]))
        icon = Image.open(settings.assetPath + "/askredditlogo.png").resize((logowidth, logoheight), Image.NEAREST)
        img_pil.paste(icon, (xPosLogo, yPosLogo), icon)
        xPosCommentIcon, yPosCommentIcon = (30, img_pil.height - logoheight * 2)
        iconbannerOffsetX = 20
        iconbannergap = 90


        icon_upvotes = Image.open(settings.assetPath + "/upvotewhite.png").resize((upvoteiconwidth, upvoteiconheight), Image.NEAREST)
        icon_comments = Image.open(settings.assetPath + "/chatwhite.png").resize((upvoteiconwidth, upvoteiconheight), Image.NEAREST)
        img_pil.paste(icon_upvotes, (xPosCommentIcon, yPosCommentIcon), icon_upvotes)
        img_pil.paste(icon_comments, (iconbannergap + xPosCommentIcon + upvoteiconwidth + font_below_icons.getsize(imageframe.redditPointsFormat(upvotes))[0] + iconbannerOffsetX * 2, yPosCommentIcon), icon_comments)

        draw.text((xPosLogo + logowidth, yPosLogo - 5), "r/AskReddit", font=font_subreddit,
                  fill="#FFFFFF")

        draw.text((xPosCommentIcon + upvoteiconwidth + iconbannerOffsetX, yPosCommentIcon), str(imageframe.redditPointsFormat(upvotes)), font=font_below_icons,
                  fill="#FFFFFF")

        draw.text((iconbannergap + xPosCommentIcon + (upvoteiconwidth * 2) + font_below_icons.getsize(imageframe.redditPointsFormat(upvotes))[0] + iconbannerOffsetX * 3, yPosCommentIcon),
                  str(imageframe.redditPointsFormat(subcomments)), font=font_below_icons,
                  fill="#FFFFFF")


        my_img = deepcopy(np.array(img_pil))
        return my_img


    def calculateFontSize(self, commentThread, fontSize=settings.preferred_font_size, thumbnail = False):
        fontSize = fontSize
        fontpath = ("%s/Verdana.ttf" % (settings.assetPath))
        # fontpathbold = ("%s/verdanab.ttf" % (settings.assetPath))

        lineWidths = [9999]
        lineHeights = [9999]
        timesLooped = 0
        endLoop = False
        upvoteMarginX = 0
        upvoteGapX = 0
        upvoteGapY = 0

        while True:
            if endLoop:
                break

            font = ImageFont.truetype(fontpath, fontSize - timesLooped)

            font_header = ImageFont.truetype(fontpath,
                                             int(fontSize - timesLooped * self.settings.comment_author_factor))

            upvoteGapX = font.getsize("1" * self.settings.upvote_gap_scale_x)[0]
            upvoteGapY = font.getsize("1")[1] * self.settings.upvote_gap_scale_y

            upvoteMarginX = font.getsize("1" * self.settings.upvote_fontsize_scale)[0] + upvoteGapX

            poffsetX = upvoteMarginX
            poffsetY = upvoteGapY
            lineWidths.clear()
            lineHeights.clear()

            if type(commentThread) == tuple:
                for comment in commentThread:
                    author = comment.author
                    upvotes = comment.upvotes
                    script = imageframe.VideoScript(comment.text)
                    if not thumbnail:
                        script.insertLineWrappingTags(self.settings.characters_per_line)
                    else:
                        script.insertLineWrappingTags(30)

                    script.insertAudioBreakTags()
                    instructions = script.getTags()

                    lastText = ""
                    currentline = ""

                    poffsetY += font_header.getsize(author)[1]

                    for instr in instructions:
                        text = ast.literal_eval(repr(instr[0]))
                        tag = instr[1]

                        if tag == "<LW>" or tag == "":
                            lastText += text
                            currentline += text
                            lineWidths.append(poffsetX + font.getsize(currentline)[0])
                            currentline = ""
                            poffsetY += (font.getsize("asd")[1])
                        else:
                            pass

                        if tag == "<BRK>" or tag == "":
                            lastText += text
                            currentline += text

                            lastText = ""
                    tempWidth = font.getsize("1" * self.settings.reply_characters_factorX)[0]
                    tempHeight = font.getsize("random")[1]
                    poffsetX += (tempWidth * self.settings.reply_fontsize_factorX)
                    poffsetY += (tempHeight * self.settings.reply_fontsize_factorY)
                    lineHeights.append(poffsetY)

            # yeah, I know this code below is a bit messy but we need to loop the code one more time with the correct
            # font size in order to get the right values we need for lineWidths and lineHeights for margin calculations

            timesLooped += 1

            if max(lineHeights) < self.settings.imageSize[1] and max(lineWidths) < self.settings.imageSize[0]:
                endLoop = True

        fontSizeReturn = fontSize - timesLooped
        marginOffsetX = (self.settings.imageSize[0] - max(lineWidths)) / 2
        marginOffsetY = (self.settings.imageSize[1] - max(lineHeights)) / 2

        return (fontSizeReturn, marginOffsetX, marginOffsetY, upvoteMarginX, upvoteGapX, upvoteGapY)

    def renderClips(self, content, title):
        clips = [] #commentThreads
        title_wrapper = imageframe.CommentWrapper(title[0], title[1], title[2])
        new_content = []
        new_content.append((title_wrapper,))
        frameNo = 0
        for con in content:
            new_content.append(con)
        for i, subcontent in enumerate(new_content):
            print("Rendering clip (%s/%s)" % (i + 1, len(new_content)))
            try:
                frames = []
                if not i == 0:
                    fontSizeInfo = self.calculateFontSize(subcontent, self.settings.preferred_font_size)
                else:
                    # if it is the title max out font size
                    fontSizeInfo = self.calculateFontSize(subcontent, 100)
                fontSize = fontSizeInfo[0]
                marginOffsetX = fontSizeInfo[1]
                marginOffsetY = fontSizeInfo[2]
                upvoteMarginX = fontSizeInfo[3]
                upvoteGapX = fontSizeInfo[4]
                upvoteGapY = fontSizeInfo[5]


                fontpath = ("%s/Verdana.ttf" % (settings.assetPath))
                font = ImageFont.truetype(fontpath, fontSize)
                font_header = ImageFont.truetype(fontpath, int(fontSize * self.settings.comment_author_factor))

                my_img = np.zeros((self.settings.imageSize[1], self.settings.imageSize[0], 3), dtype="uint8")

                if settings.use_overlay:
                    im_frame = Image.open(f"{settings.overlayPath}/{settings.overlay_image}")
                    my_img = np.asarray(im_frame)
                else:
                    my_img[:, :, :] = self.settings.background_color

                img_pil = Image.fromarray(my_img)
                draw = ImageDraw.Draw(img_pil)

                offsetX = marginOffsetX
                offsetY = marginOffsetY


                if type(subcontent) is tuple:

                    if self.settings.hasBoundingBox:

                        authorSize = font_header.getsize(subcontent[0].author)[0]
                        upvoteSize = font_header.getsize(" %s" % imageframe.redditPointsFormat(subcontent[0].upvotes, True))[0]

                        boundingBoxWidth = self.settings.imageSize[0] - offsetX
                        boundingBoxHeight = self.settings.imageSize[1] - offsetY

                        if boundingBoxWidth < offsetX + authorSize + upvoteSize:
                            boundingBoxWidth = offsetX + authorSize + upvoteSize + upvoteMarginX

                        draw.rectangle([(offsetX, offsetY),
                                        (boundingBoxWidth, boundingBoxHeight)],
                                       fill=tuple(self.settings.bounding_box_colour))


                    offsetX += upvoteMarginX
                    offsetY += upvoteGapY

                    for comment in subcontent:
                        author = comment.author
                        text = comment.text
                        upvotes = comment.upvotes
                        script = imageframe.VideoScript(text)
                        script.insertLineWrappingTags()
                        script.insertNewLineTags()
                        script.insertAudioBreakTags()
                        instructions = script.getTags()
                        lineWidth = 0
                        lineHeight = 0

                        lastText = ""
                        currentline = ""


                        draw.text((offsetX + lineWidth, offsetY + lineHeight), author, font=font_header,
                                  fill=tuple(self.settings.author_details_color))
                        tempXoffset = font_header.getsize(author)[0]

                        if self.settings.hasUpvoteButton:
                            icon_upvotes = Image.open(settings.assetPath + "/upvoteorange.png").resize(
                                (int(upvoteMarginX) - int(upvoteGapX), int(upvoteMarginX) - int(upvoteGapX)), Image.NEAREST)
                            img_pil.paste(icon_upvotes, (int(offsetX) - int(upvoteMarginX), int(offsetY)), icon_upvotes)

                            icon_upvotes_flipped = Image.open(settings.assetPath + "/upvotewhiteflipped.png").resize(
                                (int(upvoteMarginX) - int(upvoteGapX), int(upvoteMarginX) - int(upvoteGapX)), Image.NEAREST)
                            img_pil.paste(icon_upvotes_flipped, (
                            int(offsetX) - int(upvoteMarginX), int(offsetY) + int(upvoteMarginX) + int(upvoteGapY)),
                                          icon_upvotes_flipped)

                        draw.text((offsetX + lineWidth + tempXoffset, offsetY + lineHeight),
                                  " %s" % imageframe.redditPointsFormat(upvotes, True), font=font_header,
                                  fill=tuple(self.settings.author_text_color))
                        offsetY += font_header.getsize(author)[1]

                        for instr in instructions:
                            text = ast.literal_eval(repr(instr[0]))
                            text = text.replace("\\'", "'")
                            tag = instr[1]
                            draw.text((offsetX + lineWidth, offsetY + lineHeight), text, font=font,
                                      fill=tuple(self.settings.comment_text_color))
                            if tag == "<LW>":
                                if not lastText == text:
                                    if not text.replace(" ", "") == "":
                                        lastText += text

                                currentline += text
                                currentline = ""
                                lineWidth = 0
                                offsetY += (font.getsize("asd")[1])
                            else:
                                if tag == "":
                                    offsetY += (font.getsize("asd")[1])
                                else:
                                    lineWidth = (font.getsize(text)[0])

                            if tag == "<BRK>" or tag == "":
                                if not lastText == text:
                                    lastText += text
                                currentline += text
                                lineWidth = (font.getsize(currentline)[0])


                                my_img = deepcopy(np.array(img_pil))
                                frameNo += 1

                                #cv2.imshow('image', my_img)
                                #cv2.waitKey(0)

                                newFrame = imageframe.Frame(my_img, lastText, frameNo)
                                lastText = ""
                                frames.append(newFrame)
                        tempWidth = font.getsize("1" * self.settings.reply_characters_factorX)[0]
                        tempHeight = font.getsize("random")[1]
                        offsetY += (tempHeight * self.settings.reply_fontsize_factorY)
                        offsetX += (tempWidth * self.settings.reply_fontsize_factorX)
                    commentThread = imageframe.CommentThread(frames)
                    clips.append(commentThread)
            except IndexError:
                print("index error, skipping clip.")
        return clips


    def loadClip(self, path):
        pickle_in = open((path), "rb")
        return pickle.load(pickle_in)

    def createMovie(self, clips, movie):
        for i, clip in enumerate(clips):
            print("Formatting clip (%s/%s)" % (i + 1, len(clips)))
            imageArray = [(image.image_path, image.audio_path2, image.text) for image in clip.frames]
            # gets all images and durations inside each CommentThread list of Frames
            for j, image in enumerate(imageArray):
                image_path = image[0]
                audio_path = image[1]
                text = image[2]
                if not j == len(imageArray) - 1:
                    movie.addFrame(image_path, audio_path)
                    #print("standard frame: %s" % text)
                else:
                    if not i == 0:
                        intervalFile = random.choice(os.listdir("%s/Intervals/" % settings.assetPath))

                        while "DS_Store" in intervalFile or "outro" in intervalFile:
                            intervalFile = random.choice(os.listdir("%s/Intervals/" % settings.assetPath))

                        movie.addFrameWithTransition(image_path, audio_path, "%s/Intervals/%s" % (settings.assetPath, intervalFile))
                    else:
                        movie.addFrameWithTransitionAndPause(image_path, audio_path, "%s/Intervals/standard.mp4" % settings.assetPath, 1000)
                    #print("end frame: %s" % text)

