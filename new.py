import ffmpeg


output_file = "C:/1/nus.mkv"
video_file = ffmpeg.input("C:/1/v.mkv")
output_options = {
        'vcodec': 'libx264',
        'acodec': '-an',
        'vf': 'ass=/1/s.ass'

    }
output = ffmpeg.output(
    video_file['v'],
    output_file,
    **output_options,)
ffmpeg.run(output)
