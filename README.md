# text-to-speech

テキストファイル(input.txt)に文章を入力すると、Amazon Pollyを使ってそれを読み上げる音声ファイルを生成し、その音声を再生する。

読み上げる文章はdisplay.txtに出力される。

# 動作環境

macOS, Python3

# Install

```
git clone git@github.com:oh-sky/text-to-speech.git

cd text-to-speech

cp text_to_speech_conf.py.default text_to_speech_conf.py

pip3 install boto3 watchdog
```

# Usage

```
touch input.txt
touch display.txt

/path/to/python3 /path/to/text-to-speech/text_to_speech.py &

echo 'ハローワールド' > input.txt
```
