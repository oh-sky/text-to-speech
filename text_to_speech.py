import os
import queue
import shutil
import time
from subprocess import call

import boto3
from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import text_to_speech_conf

cue = queue.PriorityQueue()

boto3_session = boto3.Session(profile_name=text_to_speech_conf.AWS_CLI_PROFILE)
polly = boto3_session.client('polly')

class DictionFilesHandler(FileSystemEventHandler):

    # 監視対象ディレクトリに変更があったときのコールバック
    def on_modified(self, event):

        # INPUT_TEXT_FILENAME に入力があった場合の処理
        if self.__is_new_text_input(event):

            # INPUT_TEXT_FILENAMEの内容を新しいファイルにコピー
            new_text_filename = self.__copy_input_to_new_text_file()
            # INPUT_TEXT_FILENAMEの内容を空にする
            shutil.copy('/dev/null', text_to_speech_conf.INPUT_TEXT_FILENAME)

            # 入力されたテキストから音声ファイルを生成
            new_speech_filename = self.__create_speech_from_text_file(new_text_filename)

            # 新しく生成したテキストファイル名および音声ファイル名のタプルをキューに挿入
            cue.put((0, {
                'speech_filename': new_speech_filename,
                'text_filename': new_text_filename
            }))

    def __is_new_text_input(self, event):
        if isinstance(event, FileModifiedEvent) \
           and event.src_path == text_to_speech_conf.INPUT_TEXT_FILENAME \
           and os.path.getsize(text_to_speech_conf.INPUT_TEXT_FILENAME) > 0:

            return True

        return False

    def __copy_input_to_new_text_file(self):
        new_text_file = str(time.time()) + '.txt'
        shutil.copy(text_to_speech_conf.INPUT_TEXT_FILENAME, new_text_file)
        return new_text_file

    def __create_speech_from_text_file(self, text_filename):
        text_fp = open(text_filename, 'r')
        text_content = text_fp.read()

        polly_response = polly.synthesize_speech(LanguageCode='ja-JP', OutputFormat='mp3', VoiceId='Mizuki', Text=text_content)

        if polly_response['ContentType'] != 'audio/mpeg':
            raise RuntimeError('Response from polly is not mp3.')

        audio_filename = text_filename + '.mp3'
        audio_fp = open(audio_filename, 'wb')
        audio_fp.write(polly_response['AudioStream'].read())

        return audio_filename

# このスクリプトを実行するディレクトリの監視を開始
watch_dog_observer = Observer()
watch_dog_observer.schedule(DictionFilesHandler(), './', recursive=True)
watch_dog_observer.start()

# メインルゥティン
while True:
    speech = cue.get()[1]
    shutil.copy(speech['text_filename'], text_to_speech_conf.DISPLAY_TEXT_FILENAME)
    call('afplay ' + speech['speech_filename'], shell=True)
