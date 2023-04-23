import ffmpeg

subs = r'/test/1/s.ass'
output_file = "Z:/test/1/nus.mkv"
video_file = ffmpeg.input("Z:/test/1/v.mkv")
output_options = {
        'vcodec': 'libx264',
        'acodec': '-an',
        'vf': f'ass={subs}'

    }
output = ffmpeg.output(
    video_file['v'],
    output_file,
    **output_options,)
ffmpeg.run(output)
