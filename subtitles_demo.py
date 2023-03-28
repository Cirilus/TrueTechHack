import pvleopard
import os
from pytube import YouTube



def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

def to_srt(
        words,
        endpoint_sec: float = 1.,
        length_limit=16) -> str:
    def _helper(end: int) -> None:
        lines.append("%d" % section)
        lines.append(
            "%s --> %s" %
            (
                second_to_timecode(words[start].start_sec),
                second_to_timecode(words[end].end_sec)
            )
        )
        lines.append(' '.join(x.word for x in words[start:(end + 1)]))
        lines.append('')

    lines = list()
    section = 0
    start = 0
    for k in range(1, len(words)):
        if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                (length_limit is not None and (k - start) >= length_limit):
            _helper(k - 1)
            start = k
            section += 1
    _helper(len(words) - 1)

    return '\n'.join(lines)


def voice_to_subs(audio_path:str, subtitles_path:str):
    leopard = pvleopard.create(access_key="iLCUQv9V2bc1p2nR3G2N70ClJet5mDmnQs1fmxNmXEp/ciGhDpE8Ew==")
    print(audio_path)
    transcript, words = leopard.process_file(audio_path)
    with open(subtitles_path, mode='w') as file:
        file.write(to_srt(words))


if __name__ == "__main__":
    audio_path= "tmp/test.mp3"
    base_path = "/home/kirill/prog/hacks/TrueTech/"
    youtube = YouTube("https://www.youtube.com/watch?v=rEq1Z0bjdwc")
    audio_stream = youtube \
    .streams \
    .filter(only_audio=True, audio_codec='opus') \
    .order_by('bitrate') \
    .last()
    audio_stream.download(
        output_path=os.path.dirname(audio_path),
        filename=os.path.basename(audio_path)
    )
    print("audio downloaded")
    voice_to_subs(
        base_path + audio_path,
        base_path + "tmp/subs.srt",
    )